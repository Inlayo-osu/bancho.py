from __future__ import annotations

import asyncio
import time

import app.packets
import app.settings
import app.state
from app.constants.gamemodes import GameMode
from app.constants.privileges import Privileges
from app.logging import Ansi
from app.logging import log

OSU_CLIENT_MIN_PING_INTERVAL = 300000 // 1000  # defined by osu!


async def initialize_housekeeping_tasks() -> None:
    """Create tasks for each housekeeping tasks."""
    log("Initializing housekeeping tasks.", Ansi.LCYAN)

    loop = asyncio.get_running_loop()

    app.state.sessions.housekeeping_tasks.update(
        {
            loop.create_task(task)
            for task in (
                _remove_expired_donation_privileges(interval=30 * 60),
                _update_bot_status(interval=5 * 60),
                _disconnect_ghosts(interval=OSU_CLIENT_MIN_PING_INTERVAL // 3),
            )
        },
    )


async def _remove_expired_donation_privileges(interval: int) -> None:
    """Remove donation privileges from users with expired sessions."""
    while True:
        if app.settings.DEBUG:
            log("Removing expired donation privileges.", Ansi.LMAGENTA)

        expired_donors = await app.state.services.database.fetch_all(
            "SELECT id FROM users "
            "WHERE donor_end <= UNIX_TIMESTAMP() "
            "AND priv & :donor_priv",
            {"donor_priv": Privileges.DONATOR.value},
        )

        for expired_donor in expired_donors:
            player = await app.state.sessions.players.from_cache_or_sql(
                id=expired_donor["id"],
            )

            assert player is not None

            # TODO: perhaps make a `revoke_donor` method?
            await player.remove_privs(Privileges.DONATOR)
            player.donor_end = 0
            await app.state.services.database.execute(
                "UPDATE users SET donor_end = 0 WHERE id = :id",
                {"id": player.id},
            )

            if player.is_online:
                player.enqueue(
                    app.packets.notification("Your supporter status has expired."),
                )

            log(f"{player}'s supporter status has expired.", Ansi.LMAGENTA)

        await asyncio.sleep(interval)


async def _disconnect_ghosts(interval: int) -> None:
    """Actively disconnect users above the
    disconnection time threshold on the osu! server."""
    while True:
        await asyncio.sleep(interval)
        current_time = time.time()

        for player in app.state.sessions.players:
            if current_time - player.last_recv_time > OSU_CLIENT_MIN_PING_INTERVAL:
                log(f"Auto-dced {player}.", Ansi.LMAGENTA)
                player.logout()


async def _update_bot_status(interval: int) -> None:
    """Re roll the bot status, every `interval`."""
    while True:
        await asyncio.sleep(interval)
        app.packets.bot_stats.cache_clear()


async def rebuild_redis_leaderboards() -> None:
    """Rebuild Redis leaderboards from database on server startup."""
    log("Rebuilding Redis leaderboards from database...", Ansi.LCYAN)

    # Get all game modes (0-11: vanilla, relax, autopilot)
    all_modes = list(range(12))

    for mode_value in all_modes:
        try:
            mode = GameMode(mode_value)
        except ValueError:
            continue

        # Clear existing leaderboard data for this mode
        await app.state.services.redis.delete(f"bancho:leaderboard:{mode_value}")

        # Fetch all users with unrestricted privileges and their stats
        users = await app.state.services.database.fetch_all(
            "SELECT s.id, s.pp, u.country "
            "FROM stats s "
            "INNER JOIN users u ON s.id = u.id "
            "WHERE s.mode = :mode AND u.priv & :unrestricted AND s.pp > 0",
            {"mode": mode_value, "unrestricted": Privileges.UNRESTRICTED.value},
        )

        if not users:
            continue

        # Build global leaderboard
        global_leaderboard = {str(user["id"]): user["pp"] for user in users}
        if global_leaderboard:
            await app.state.services.redis.zadd(
                f"bancho:leaderboard:{mode_value}",
                global_leaderboard,
            )

        # Build country leaderboards
        country_leaderboards: dict[str, dict[str, float]] = {}
        for user in users:
            country = user["country"]
            if country not in country_leaderboards:
                country_leaderboards[country] = {}
            country_leaderboards[country][str(user["id"])] = user["pp"]

        # Clear and populate country leaderboards
        for country, leaderboard in country_leaderboards.items():
            leaderboard_key = f"bancho:leaderboard:{mode_value}:{country}"
            await app.state.services.redis.delete(leaderboard_key)
            if leaderboard:
                await app.state.services.redis.zadd(leaderboard_key, leaderboard)

        log(
            f"Rebuilt mode {mode_value} ({mode!r}) leaderboard with {len(users)} users.",
            Ansi.LGREEN,
        )

    log("Redis leaderboard rebuild complete!", Ansi.LGREEN)
