import random
import string
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


async def send_email(to_email: str, subject: str, html_body: str):
    """Send an email via SMTP. If SMTP is not configured, prints OTP to console."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"[DEV MODE] Email to {to_email}: {subject}\n{html_body}")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message.attach(MIMEText(html_body, "html"))

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )


async def send_otp_email(to_email: str, otp: str, name: str = "User"):
    subject = "ProXM — Password Reset OTP"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: 'Segoe UI', sans-serif; background: #0f0f1a; color: #e2e8f0; padding: 40px;">
      <div style="max-width: 480px; margin: 0 auto; background: #1a1a2e; border-radius: 16px; padding: 40px; border: 1px solid #2d2d5e;">
        <h1 style="color: #a78bfa; margin-bottom: 8px;">ProXM</h1>
        <p style="color: #94a3b8; margin-bottom: 32px;">AI-Proctored Examination Platform</p>
        <h2 style="color: #e2e8f0;">Hello, {name} 👋</h2>
        <p style="color: #94a3b8;">Here is your one-time password to reset your account:</p>
        <div style="background: #0f0f1a; border: 1px solid #a78bfa; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
          <span style="font-size: 40px; font-weight: 700; letter-spacing: 12px; color: #a78bfa;">{otp}</span>
        </div>
        <p style="color: #64748b; font-size: 14px;">This OTP expires in <strong style="color:#e2e8f0;">10 minutes</strong>. Do not share it with anyone.</p>
        <hr style="border: 1px solid #2d2d5e; margin: 24px 0;"/>
        <p style="color: #475569; font-size: 12px;">If you didn't request this, please ignore this email.</p>
      </div>
    </body>
    </html>
    """
    await send_email(to_email, subject, html_body)
