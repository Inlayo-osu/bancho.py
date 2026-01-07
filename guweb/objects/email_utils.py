from __future__ import annotations

__all__ = ("send_email", "send_verification_email", "send_password_reset_email")

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from discord_webhook import DiscordWebhook, DiscordEmbed


class EmailConfig:
    """SMTP email configuration"""

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Inlayo Server")
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_AUDIT_LOG_WEBHOOK", "")


def send_discord_notification(
    email_type: str,
    to_email: str,
    subject: str,
    full_message: str,
    username: str | None = None,
) -> bool:
    """
    Send email notification to Discord webhook

    Args:
        email_type: Type of email (Verification, Password Reset, etc.)
        to_email: Recipient email address
        subject: Email subject
        full_message: Full email message content
        username: Username (optional)

    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    if not EmailConfig.DISCORD_WEBHOOK_URL:
        return False

    try:
        # Truncate message if too long (Discord embed description limit is 4096)
        if len(full_message) > 4096:
            full_message = full_message[:4093] + "..."

        # Create webhook
        webhook = DiscordWebhook(url=EmailConfig.DISCORD_WEBHOOK_URL)
        
        # Create embed with full message
        embed = DiscordEmbed(description=full_message, color=242424)
        
        # Set author as BanchoBot
        embed.set_author(
            name=f"BanchoBot Sent {email_type}",
            url="https://osu.ppy.sh/u/1",
            icon_url="https://a.ppy.sh/1"
        )
        
        # Set footer
        embed.set_footer(text="via guweb!")
        
        # Add embed to webhook
        webhook.add_embed(embed)
        
        # Execute webhook
        response = webhook.execute()
        return True
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")
        import traceback
        traceback.print_exc()
        return False


async def send_email(
    to_email: str,
    subject: str,
    body_text: str,
    email_type: str = "General Email",
    username: str | None = None,
    extra_info: str | None = None,
) -> tuple[bool, str | None]:
    """
    Send an email using SMTP

    Args:
        to_email: Recipient email address
        subject: Email subject
        body_text: Plain text body content
        email_type: Type of email for Discord notification
        username: Username for Discord notification
        extra_info: Extra info for Discord notification

    Returns:
        tuple: (success: bool, error_message: str | None)
    """
    try:
        # Create plain text message
        msg = MIMEText(body_text, "plain")
        msg["Subject"] = subject
        msg["From"] = f"{EmailConfig.SMTP_FROM_NAME} <{EmailConfig.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email

        # Connect to SMTP server
        if EmailConfig.SMTP_PORT == 465:
            # Use SMTP_SSL for port 465
            import smtplib

            with smtplib.SMTP_SSL(
                EmailConfig.SMTP_HOST,
                EmailConfig.SMTP_PORT,
            ) as server:
                server.login(EmailConfig.SMTP_USER, EmailConfig.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Use STARTTLS for port 587
            with smtplib.SMTP(EmailConfig.SMTP_HOST, EmailConfig.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailConfig.SMTP_USER, EmailConfig.SMTP_PASSWORD)
                server.send_message(msg)

        # Send Discord notification with full email message
        send_discord_notification(
            email_type=email_type,
            to_email=to_email,
            subject=subject,
            full_message=msg.as_string(),
            username=username,
        )

        return True, None
    except Exception as e:
        error_msg = str(e)
        print(f"Failed to send email: {e}")
        
        # Extract domain error from SMTP error message
        if "not found domain" in error_msg:
            domain = error_msg.split("not found domain: ")[-1].strip("')")
            return False, f"Email domain not found: {domain}"
        elif "550" in error_msg:
            return False, "Invalid email address or domain"
        elif "535" in error_msg:
            return False, "SMTP authentication failed"
        else:
            return False, f"Failed to send email: {error_msg}"


async def send_verification_email(
    to_email: str,
    username: str,
    verification_code: str,
) -> tuple[bool, str | None]:
    """Send account verification email"""
    subject = "Verify your Inlayo account"

    body_text = f"""Welcome to Inlayo!

Hello {username},

Thank you for registering! Please verify your email address by using the code below:

{verification_code}

This code will expire in 10 minutes.

If you didn't create an account, please ignore this email.

---
Inlayo Team"""

    return await send_email(
        to_email=to_email,
        subject=subject,
        body_text=body_text,
        email_type="Email Verification",
        username=username,
        extra_info=f"Verification Code: {verification_code}",
    )


async def send_password_reset_email(
    to_email: str,
    username: str,
    reset_link: str,
) -> tuple[bool, str | None]:
    """Send password reset email"""
    subject = "Reset your Inlayo password"

    body_text = f"""Password Reset Request

Hello {username},

We received a request to reset your password. Visit the link below to reset it:

{reset_link}

This link will expire in 10 minutes.

If you didn't request a password reset, please ignore this email.

---
Inlayo Team"""

    return await send_email(
        to_email=to_email,
        subject=subject,
        body_text=body_text,
        email_type="Password Reset",
        username=username,
        extra_info=f"Reset Link: {reset_link}",
    )
