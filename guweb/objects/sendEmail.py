import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from objects import glob
from objects import logUtils as log
from discord_webhook import DiscordWebhook, DiscordEmbed
import traceback

sender_email = glob.config.SENDER_EMAIL
sender_password = glob.config.SENDER_EMAIL_PASSWORD

def exceptionE(msg=""): 
    e = traceback.format_exc()
    log.error(f"{msg} \n{e}")
    return e

def mailSend(nick: str, to_email: str, subject: str, body: str, type=" "):
    sc = 200
    msg = MIMEMultipart()
    msg['From'] = f'InlayoBot <{sender_email}>'
    if nick and not nick.isascii(): 
        nick = str(Header(nick, 'utf-8').encode())
    msg['To'] = f"{nick} <{to_email}>" if nick else to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        smtp = smtplib.SMTP_SSL(**glob.config.SMTP_SERVER_INFO)
        smtp.login(sender_email, sender_password)
        smtp.sendmail(sender_email, to_email, msg.as_string())
        smtp.quit()
        log.info(f"{type} Email sent successfully")
    except Exception as e:
        exceptionE(f"{type} Email sending failed: {e}")
        sc = e

    try:
        if sc == 200:
            imap = imaplib.IMAP4_SSL(**glob.config.IMAP_SERVER_INFO)
            imap.login(sender_email, sender_password)
            imap.append("Sent", None, None, msg.as_bytes())
            log.info("Successfully copied to sent mail!")
        else: 
            log.warning("Did not copy to sent mail due to email sending failure")
    except Exception as e:
        exceptionE(f"Failed to copy to sent mail: {e}")
        sc = e

    try:
        if sc != 200: 
            raise sc
        msg = msg.as_string()
        if len(msg) > 4096: 
            msg = msg[:4096]
        webhook = DiscordWebhook(url=glob.config.DISCORD_EMAIL_LOG_WEBHOOK)
        embed = DiscordEmbed(description=msg, color=242424)
        embed.set_author(name=f"BanchoBot Sent {type}email", url=f"https://osu.{glob.config.domain}/u/1", icon_url=f"https://a.{glob.config.domain}/1")
        embed.set_footer(text="via guweb!")
        webhook.add_embed(embed)
        webhook.execute()
    except Exception as e:
        exceptionE(f"Discord webhook sending failed! | {e}")
    
    return sc
