"""Email service using Resend for transactional emails."""
import os
import asyncio
import logging
import resend

logger = logging.getLogger(__name__)

resend.api_key = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")


async def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """Send a password reset email. Returns True on success."""
    if not resend.api_key:
        logger.warning("RESEND_API_KEY not set — skipping email send")
        return False

    html = f"""
    <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:480px;margin:0 auto;padding:40px 24px;">
      <div style="text-align:center;margin-bottom:32px;">
        <div style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;padding:10px;margin-bottom:12px;">
          <span style="color:#fff;font-size:20px;font-weight:bold;">TS</span>
        </div>
        <h1 style="font-size:22px;font-weight:700;color:#1e293b;margin:8px 0 0;">TrendScout</h1>
      </div>
      <h2 style="font-size:20px;font-weight:700;color:#1e293b;margin-bottom:8px;">Reset your password</h2>
      <p style="font-size:14px;color:#64748b;line-height:1.6;margin-bottom:24px;">
        We received a request to reset your password. Click the button below to choose a new one. This link expires in 1 hour.
      </p>
      <div style="text-align:center;margin-bottom:24px;">
        <a href="{reset_link}" style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 32px;border-radius:10px;">
          Reset Password
        </a>
      </div>
      <p style="font-size:12px;color:#94a3b8;line-height:1.6;">
        If you didn't request this, you can safely ignore this email. Your password won't change.
      </p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;" />
      <p style="font-size:11px;color:#94a3b8;text-align:center;">
        TrendScout &mdash; AI product validation for ecommerce
      </p>
    </div>
    """

    params = {
        "from": SENDER_EMAIL,
        "to": [to_email],
        "subject": "Reset your TrendScout password",
        "html": html,
    }

    try:
        result = await asyncio.to_thread(resend.Emails.send, params)
        email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
        logger.info(f"Password reset email sent to {to_email} (id: {email_id})")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}")
        return False
