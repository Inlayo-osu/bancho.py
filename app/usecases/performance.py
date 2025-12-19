from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypedDict

import akatsuki_pp_py
import rosu_pp_py

from app.constants.mods import Mods


@dataclass
class ScoreParams:
    mode: int
    mods: int | None = None
    combo: int | None = None

    # caller may pass either acc OR 300/100/50/geki/katu/miss
    # passing both will result in a value error being raised
    acc: float | None = None

    n300: int | None = None
    n100: int | None = None
    n50: int | None = None
    ngeki: int | None = None
    nkatu: int | None = None
    nmiss: int | None = None


class PerformanceRating(TypedDict):
    pp: float
    pp_acc: float | None
    pp_aim: float | None
    pp_speed: float | None
    pp_flashlight: float | None
    effective_miss_count: float | None
    pp_difficulty: float | None


class DifficultyRating(TypedDict):
    stars: float
    aim: float | None
    speed: float | None
    flashlight: float | None
    slider_factor: float | None
    speed_note_count: float | None
    stamina: float | None
    color: float | None
    rhythm: float | None
    peak: float | None


class PerformanceResult(TypedDict):
    performance: PerformanceRating
    difficulty: DifficultyRating


def calculate_performances(
    osu_file_path: str,
    scores: Iterable[ScoreParams],
) -> list[PerformanceResult]:
    """\
    Calculate performance for multiple scores on a single beatmap.

    Typically most useful for mass-recalculation situations.

    TODO: Some level of error handling & returning to caller should be
    implemented here to handle cases where e.g. the beatmap file is invalid
    or there an issue during calculation.
    """
    # Convert scores to list to allow multiple iterations
    scores_list = list(scores)

    # Determine if we need akatsuki or rosu beatmap
    use_akatsuki = any(
        score.mods and (score.mods & (Mods.RELAX | Mods.AUTOPILOT))
        for score in scores_list
    )
    use_rosu = any(
        not score.mods or not (score.mods & (Mods.RELAX | Mods.AUTOPILOT))
        for score in scores_list
    )

    akatsuki_bmap = akatsuki_pp_py.Beatmap(path=osu_file_path) if use_akatsuki else None
    rosu_bmap = rosu_pp_py.Beatmap(path=osu_file_path) if use_rosu else None

    results: list[PerformanceResult] = []

    for score in scores_list:
        if score.acc and (
            score.n300 or score.n100 or score.n50 or score.ngeki or score.nkatu
        ):
            raise ValueError(
                "Must not specify accuracy AND 300/100/50/geki/katu. Only one or the other.",
            )

        # rosupp ignores NC and requires DT
        if score.mods is not None:
            if score.mods & Mods.NIGHTCORE:
                score.mods |= Mods.DOUBLETIME

        # Use akatsuki-pp-py for relax/autopilot, rosu-pp-py for vanilla
        is_relax_mode = score.mods and (score.mods & (Mods.RELAX | Mods.AUTOPILOT))

        if is_relax_mode:
            calculator = akatsuki_pp_py.Calculator(
                mode=score.mode,
                mods=score.mods or 0,
                combo=score.combo,
                acc=score.acc,
                n300=score.n300,
                n100=score.n100,
                n50=score.n50,
                n_geki=score.ngeki,
                n_katu=score.nkatu,
                n_misses=score.nmiss,
            )
            result = calculator.performance(akatsuki_bmap)  # type: ignore[arg-type]
        else:
            # rosu-pp-py uses Performance class with different API
            # Only pass non-None parameters
            perf_kwargs: dict[str, int | float] = {
                "mods": score.mods or 0,
                "lazer": False,  # Use stable (non-lazer) scoring
            }
            if score.combo is not None:
                perf_kwargs["combo"] = score.combo
            if score.acc is not None:
                perf_kwargs["accuracy"] = score.acc
            if score.n300 is not None:
                perf_kwargs["n300"] = score.n300
            if score.n100 is not None:
                perf_kwargs["n100"] = score.n100
            if score.n50 is not None:
                perf_kwargs["n50"] = score.n50
            if score.ngeki is not None:
                perf_kwargs["n_geki"] = score.ngeki
            if score.nkatu is not None:
                perf_kwargs["n_katu"] = score.nkatu
            if score.nmiss is not None:
                perf_kwargs["misses"] = score.nmiss

            perf = rosu_pp_py.Performance(**perf_kwargs)
            result = perf.calculate(rosu_bmap)  # type: ignore[arg-type, assignment]

        pp: float = result.pp

        if math.isnan(pp) or math.isinf(pp):
            # TODO: report to logserver
            pp = 0.0
        else:
            pp = float(round(pp, 3))

        # Handle attribute name differences between akatsuki-pp-py and rosu-pp-py
        # rosu-pp-py uses pp_accuracy, akatsuki-pp-py uses pp_acc
        pp_acc = getattr(result, "pp_accuracy", None) or getattr(result, "pp_acc", None)

        results.append(
            {
                "performance": {
                    "pp": pp,
                    "pp_acc": pp_acc,
                    "pp_aim": getattr(result, "pp_aim", None),
                    "pp_speed": getattr(result, "pp_speed", None),
                    "pp_flashlight": getattr(result, "pp_flashlight", None),
                    "effective_miss_count": getattr(
                        result,
                        "effective_miss_count",
                        None,
                    ),
                    "pp_difficulty": getattr(result, "pp_difficulty", None),
                },
                "difficulty": {
                    "stars": result.difficulty.stars,
                    "aim": getattr(result.difficulty, "aim", None),
                    "speed": getattr(result.difficulty, "speed", None),
                    "flashlight": getattr(result.difficulty, "flashlight", None),
                    "slider_factor": getattr(result.difficulty, "slider_factor", None),
                    "speed_note_count": getattr(
                        result.difficulty,
                        "speed_note_count",
                        None,
                    ),
                    "stamina": getattr(result.difficulty, "stamina", None),
                    "color": getattr(result.difficulty, "color", None),
                    "rhythm": getattr(result.difficulty, "rhythm", None),
                    "peak": getattr(result.difficulty, "peak", None),
                },
            },
        )

    return results
