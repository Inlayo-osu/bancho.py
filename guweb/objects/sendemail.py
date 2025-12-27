"""Email sending utilities for guweb."""

from __future__ import annotations

import imaplib
import smtplib
import traceback
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from discord_webhook import DiscordEmbed
from discord_webhook import DiscordWebhook
from objects import glob
from objects import logUtils as log

__all__ = ("mailSend",)


def _log_exception(msg: str = "") -> str:
    """Log exception with traceback."""
    error_trace = traceback.format_exc()
    log.error(f"{msg}\n{error_trace}")
    return error_trace


def mailSend(
    nick: str,
    to_email: str,
    subject: str,
    body: str,
    email_type: str = "",
) -> int:
    """
    Send email via SMTP and optionally log to Discord.
    
    Args:
        nick: Recipient nickname
        to_email: Recipient email address
        subject: Email subject
        body: Email body text
        email_type: Type prefix for logging (e.g., "Register", "Forgot")
    
    Returns:
        200 if successful, error object otherwise
    """
    sender_email = glob.config.SENDER_EMAIL
    sender_password = glob.config.SENDER_EMAIL_PASSWORD
    
    # Build email message
    msg = MIMEMultipart()
    msg["From"] = f"InlayoBot <{sender_email}>"
    
    # Handle non-ASCII nicknames
    if nick and not nick.isascii():
        nick = str(Header(nick, "utf-8").encode())
    
    msg["To"] = f"{nick} <{to_email}>" if nick else to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    # Send email via SMTP
    try:
        smtp = smtplib.SMTP_SSL(**glob.config.SMTP_SERVER_INFO)
        smtp.login(sender_email, sender_password)
        smtp.sendmail(sender_email, to_email, msg.as_string())
        smtp.quit()
        log.info(f"{email_type} Email sent successfully to {to_email}")
    except Exception as e:
        _log_exception(f"{email_type} Email sending failed: {e}")
        return e  # Return error object
    
    # Copy to sent folder (IMAP)
    try:
        imap = imaplib.IMAP4_SSL(**glob.config.IMAP_SERVER_INFO)
        imap.login(sender_email, sender_password)
        imap.append("Sent", None, None, msg.as_bytes())
        imap.logout()
        log.info("Successfully copied to sent mail!")
    except Exception as e:
        _log_exception(f"Failed to copy to sent mail: {e}")
        # Don't fail the whole operation if IMAP fails
    
    # Log to Discord webhook
    if glob.config.DISCORD_EMAIL_LOG_WEBHOOK:
        try:
            msg_str = msg.as_string()
            if len(msg_str) > 4096:
                msg_str = msg_str[:4096] + "..."
            
            webhook = DiscordWebhook(url=glob.config.DISCORD_EMAIL_LOG_WEBHOOK)
            embed = DiscordEmbed(description=msg_str, color=242424)
            embed.set_author(
                name=f"BanchoBot Sent {email_type} Email",
                url=f"https://osu.{glob.config.domain}/u/1",
                icon_url=f"https://a.{glob.config.domain}/1",
            )
            embed.set_footer(text="via guweb!")
            webhook.add_embed(embed)
            webhook.execute()
        except Exception as e:
            _log_exception(f"Discord webhook failed: {e}")
            # Don't fail if webhook fails
    
    return 200

