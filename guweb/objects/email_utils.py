from __future__ import annotations

__all__ = ("send_email", "send_verification_email", "send_password_reset_email")

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiohttp


class EmailConfig:
    """SMTP email configuration"""

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Inlayo Server")
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_AUDIT_LOG_WEBHOOK", "")


async def send_discord_notification(
    email_type: str,
    to_email: str,
    subject: str,
    username: str | None = None,
    extra_info: str | None = None,
) -> bool:
    """
    Send email notification to Discord webhook

    Args:
        email_type: Type of email (Verification, Password Reset, etc.)
        to_email: Recipient email address
        subject: Email subject
        username: Username (optional)
        extra_info: Additional information (optional)

    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    if not EmailConfig.DISCORD_WEBHOOK_URL:
        return False

    try:
        # Create Discord embed
        embed = {
            "title": f"📧 {email_type}",
            "color": 0x666666,  # Gray color
<<<<<<< HEAD
            "fields": [],
=======
            "fields": [
                {"name": "수신자", "value": to_email, "inline": True},
                {"name": "제목", "value": subject, "inline": True},
            ],
>>>>>>> 285736336d59c6297f36fcbc80f7021ee97fab5a
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Inlayo Email System"},
        }

        if username:
<<<<<<< HEAD
            embed["fields"].append({
                "name": "User",
                "value": username,
                "inline": True
            })
        
        embed["fields"].append({
            "name": "Recipient",
            "value": to_email,
            "inline": True
        })
        
        if extra_info:
            embed["fields"].append({
                "name": "Content",
                "value": extra_info,
                "inline": False
            })
        
        payload = {
            "embeds": [embed]
        }
        
=======
            embed["fields"].insert(
                0,
                {"name": "사용자", "value": username, "inline": True},
            )

        if extra_info:
            embed["fields"].append(
                {"name": "추가 정보", "value": extra_info, "inline": False},
            )

        payload = {"embeds": [embed]}

>>>>>>> 285736336d59c6297f36fcbc80f7021ee97fab5a
        async with aiohttp.ClientSession() as session:
            async with session.post(
                EmailConfig.DISCORD_WEBHOOK_URL,
                json=payload,
            ) as response:
                return response.status == 204
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")
        return False


async def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: str | None = None,
    email_type: str = "General Email",
    username: str | None = None,
    extra_info: str | None = None,
) -> bool:
    """
    Send an email using SMTP

    Args:
        to_email: Recipient email address
        subject: Email subject
        body_html: HTML body content
        body_text: Plain text body content (optional)
        email_type: Type of email for Discord notification
        username: Username for Discord notification
        extra_info: Extra info for Discord notification

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{EmailConfig.SMTP_FROM_NAME} <{EmailConfig.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email

        # Add plain text part
        if body_text:
            part1 = MIMEText(body_text, "plain")
            msg.attach(part1)

        # Add HTML part
        part2 = MIMEText(body_html, "html")
        msg.attach(part2)

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

        # Send Discord notification
        await send_discord_notification(
            email_type=email_type,
            to_email=to_email,
            subject=subject,
            username=username,
            extra_info=extra_info,
        )

        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


async def send_verification_email(
    to_email: str,
    username: str,
    verification_code: str,
) -> bool:
    """Send account verification email"""
    subject = "Verify your Inlayo account"

    body_html = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #1a1a1a;
                    color: #ffffff;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #2a2a2a;
                    border-radius: 10px;
                    padding: 30px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #666666;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .code {{
                    font-size: 24px;
                    font-weight: bold;
                    letter-spacing: 5px;
                    color: #aaaaaa;
                    padding: 15px;
                    background-color: #1a1a1a;
                    border-radius: 5px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <p>Hello {username},</p>
                <p>Thank you for registering! Please verify your email address by using the code below:</p>
                <div class="code">{verification_code}</div>
                <p>This code will expire in 24 hours.</p>
                <p>If you didn't create an account, please ignore this email.</p>
            </div>
        </body>
    </html>
    """

    body_text = f"""
    Welcome to Inlayo!

    Hello {username},

    Thank you for registering! Please verify your email address by using the code below:

    {verification_code}

    This code will expire in 24 hours.

    If you didn't create an account, please ignore this email.
    """

    return await send_email(
        to_email=to_email,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        email_type="Email Verification",
        username=username,
        extra_info=f"Verification Code: {verification_code}",
    )


async def send_password_reset_email(
    to_email: str,
    username: str,
    reset_link: str,
) -> bool:
    """Send password reset email"""
    subject = "Reset your Inlayo password"

    body_html = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #1a1a1a;
                    color: #ffffff;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #2a2a2a;
                    border-radius: 10px;
                    padding: 30px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #666666;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <p>Hello {username},</p>
                <p>We received a request to reset your password. Use the link below:</p>
                <p style="word-break: break-all; color: #aaaaaa;">{reset_link}</p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request a password reset, please ignore this email.</p>
            </div>
        </body>
    </html>
    """

    body_text = f"""
    Password Reset Request

    Hello {username},

    We received a request to reset your password. Visit the link below to reset it:

    {reset_link}

    This link will expire in 1 hour.

    If you didn't request a password reset, please ignore this email.
    """

    return await send_email(
        to_email=to_email,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        email_type="Password Reset",
        username=username,
        extra_info=f"Reset Link: {reset_link}",
    )
