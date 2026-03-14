"""Email service using Resend for transactional emails."""
import os
import asyncio
import logging
import resend

logger = logging.getLogger(__name__)

resend.api_key = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
SITE_URL = os.environ.get("SITE_URL", "")


class EmailService:
    """Resend-backed email service for TrendScout transactional emails."""

    def __init__(self):
        self.sender = SENDER_EMAIL
        self.site_url = SITE_URL

    async def send_email(self, to_email: str, subject: str, html_content: str) -> dict:
        if not resend.api_key:
            logger.warning("RESEND_API_KEY not set — skipping email")
            return {"status": "skipped", "error": "RESEND_API_KEY not configured"}
        try:
            result = await asyncio.to_thread(
                resend.Emails.send,
                {"from": self.sender, "to": [to_email], "subject": subject, "html": html_content},
            )
            email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
            logger.info(f"Email sent to {to_email} (id: {email_id})")
            return {"status": "success", "id": email_id}
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return {"status": "error", "error": str(e)}

    async def send_weekly_digest(self, to_email: str, user_name: str, report_data: dict, next_steps: list = None) -> dict:
        site = self.site_url or "https://trendscout.click"
        sections = report_data.get("sections", [])

        # Extract top products from report
        top_products_html = ""
        for section in sections:
            if section.get("locked"):
                continue
            products = section.get("products", section.get("data", {}).get("products", []))
            if isinstance(products, list) and products:
                for p in products[:5]:
                    name = p.get("product_name", p.get("name", "Unknown"))
                    score = p.get("launch_score", p.get("score", 0))
                    category = p.get("category", "")
                    color = "#10b981" if score >= 70 else "#6366f1" if score >= 50 else "#64748b"
                    top_products_html += f"""
                    <tr>
                      <td style="padding:10px 12px;border-bottom:1px solid #f1f5f9;">
                        <span style="font-weight:600;color:#1e293b;">{name}</span>
                        <br/><span style="font-size:12px;color:#94a3b8;">{category}</span>
                      </td>
                      <td style="padding:10px 12px;border-bottom:1px solid #f1f5f9;text-align:center;">
                        <span style="font-weight:700;font-family:monospace;color:{color};font-size:18px;">{score}</span>
                        <span style="font-size:11px;color:#94a3b8;">/100</span>
                      </td>
                    </tr>"""
                break

        if not top_products_html:
            top_products_html = """
            <tr><td colspan="2" style="padding:20px;text-align:center;color:#94a3b8;">
              No products available this week. Check back soon!
            </td></tr>"""

        # Build next-steps section
        next_steps_html = ""
        if next_steps:
            step_items = ""
            for step in next_steps[:3]:
                step_items += f"""
                <tr>
                  <td style="padding:10px 14px;border-bottom:1px solid #f1f5f9;">
                    <span style="font-weight:600;color:#1e293b;font-size:14px;">{step.get('title', '')}</span>
                    <br/><span style="font-size:12px;color:#64748b;line-height:1.5;">{step.get('description', '')}</span>
                  </td>
                  <td style="padding:10px 14px;border-bottom:1px solid #f1f5f9;text-align:right;vertical-align:middle;">
                    <a href="{site}{step.get('action', {}).get('href', '/dashboard')}"
                       style="display:inline-block;background:#6366f1;color:#fff;font-size:12px;font-weight:600;text-decoration:none;padding:6px 14px;border-radius:6px;">
                      {step.get('action', {}).get('label', 'Go')}
                    </a>
                  </td>
                </tr>"""

            next_steps_html = f"""
            <div style="margin-top:28px;">
              <h2 style="font-size:18px;font-weight:700;color:#1e293b;margin-bottom:12px;">
                What Should You Do Next?
              </h2>
              <p style="font-size:13px;color:#64748b;margin-bottom:14px;">Personalised actions based on your activity this week.</p>
              <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;">
                {step_items}
              </table>
            </div>"""

        html = f"""
        <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:560px;margin:0 auto;padding:40px 24px;background:#ffffff;">
          <div style="text-align:center;margin-bottom:28px;">
            <div style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;padding:10px;margin-bottom:10px;">
              <span style="color:#fff;font-size:18px;font-weight:bold;">TS</span>
            </div>
            <h1 style="font-size:22px;font-weight:700;color:#1e293b;margin:8px 0 0;">Your Weekly TrendScout Digest</h1>
          </div>

          <p style="font-size:15px;color:#1e293b;margin-bottom:4px;">Hi {user_name},</p>
          <p style="font-size:14px;color:#64748b;line-height:1.6;margin-bottom:24px;">
            Here are this week's top-scoring products and your personalised next steps.
          </p>

          <h2 style="font-size:18px;font-weight:700;color:#1e293b;margin-bottom:12px;">
            Top Products This Week
          </h2>
          <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;">
            <tr style="background:#f8fafc;">
              <th style="padding:10px 12px;text-align:left;font-size:12px;color:#64748b;font-weight:600;">Product</th>
              <th style="padding:10px 12px;text-align:center;font-size:12px;color:#64748b;font-weight:600;">Score</th>
            </tr>
            {top_products_html}
          </table>

          {next_steps_html}

          <div style="text-align:center;margin-top:28px;">
            <a href="{site}/dashboard"
               style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 32px;border-radius:10px;">
              Open Dashboard
            </a>
          </div>

          <hr style="border:none;border-top:1px solid #e2e8f0;margin:28px 0;" />
          <p style="font-size:11px;color:#94a3b8;text-align:center;">
            TrendScout &mdash; AI product validation for ecommerce<br/>
            <a href="{site}/settings/notifications" style="color:#94a3b8;">Unsubscribe from weekly digest</a>
          </p>
        </div>
        """

        period = report_data.get("metadata", {}).get("period", {})
        week_label = period.get("label", "This Week")

        return await self.send_email(to_email, f"TrendScout Weekly Digest — {week_label}", html)

    async def send_product_alert_email(self, to_email: str, product_name: str, alert_type: str, details: str) -> dict:
        site = self.site_url or "https://trendscout.click"
        html = f"""
        <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:480px;margin:0 auto;padding:40px 24px;">
          <div style="text-align:center;margin-bottom:28px;">
            <div style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;padding:10px;">
              <span style="color:#fff;font-size:18px;font-weight:bold;">TS</span>
            </div>
          </div>
          <h2 style="font-size:18px;font-weight:700;color:#1e293b;">Product Alert: {product_name}</h2>
          <p style="font-size:13px;color:#64748b;margin-bottom:8px;"><strong>Type:</strong> {alert_type}</p>
          <p style="font-size:14px;color:#1e293b;line-height:1.6;">{details}</p>
          <div style="text-align:center;margin-top:24px;">
            <a href="{site}/dashboard" style="display:inline-block;background:#6366f1;color:#fff;font-size:14px;font-weight:600;text-decoration:none;padding:10px 28px;border-radius:8px;">View on Dashboard</a>
          </div>
          <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;" />
          <p style="font-size:11px;color:#94a3b8;text-align:center;">TrendScout &mdash; AI product validation for ecommerce</p>
        </div>
        """
        return await self.send_email(to_email, f"TrendScout Alert: {product_name}", html)

    async def send_product_of_the_week(self, to_email: str, user_name: str, product: dict) -> dict:
        site = self.site_url or "https://trendscout.click"
        name = product.get("product_name", "Unknown")
        score = product.get("launch_score", 0)
        category = product.get("category", "")
        product_id = product.get("id", "")
        color = "#10b981" if score >= 70 else "#6366f1"

        html = f"""
        <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:480px;margin:0 auto;padding:40px 24px;">
          <div style="text-align:center;margin-bottom:28px;">
            <div style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;padding:10px;">
              <span style="color:#fff;font-size:18px;font-weight:bold;">TS</span>
            </div>
            <h1 style="font-size:20px;font-weight:700;color:#1e293b;margin:10px 0 0;">Product of the Week</h1>
          </div>
          <p style="font-size:14px;color:#64748b;">Hi {user_name},</p>
          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:20px;margin:16px 0;text-align:center;">
            <h2 style="font-size:20px;font-weight:700;color:#1e293b;margin-bottom:4px;">{name}</h2>
            <p style="font-size:13px;color:#94a3b8;margin-bottom:12px;">{category}</p>
            <span style="font-family:monospace;font-size:32px;font-weight:700;color:{color};">{score}</span>
            <span style="font-size:14px;color:#94a3b8;">/100</span>
          </div>
          <div style="text-align:center;margin-top:20px;">
            <a href="{site}/product/{product_id}" style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 28px;border-radius:10px;">View Full Analysis</a>
          </div>
          <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;" />
          <p style="font-size:11px;color:#94a3b8;text-align:center;">TrendScout &mdash; AI product validation for ecommerce</p>
        </div>
        """
        return await self.send_email(to_email, f"TrendScout: Product of the Week — {name}", html)


# Module-level instance
email_service = EmailService()


# Backward-compatible standalone function
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

    try:
        result = await asyncio.to_thread(
            resend.Emails.send,
            {"from": SENDER_EMAIL, "to": [to_email], "subject": "Reset your TrendScout password", "html": html},
        )
        email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
        logger.info(f"Password reset email sent to {to_email} (id: {email_id})")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}")
        return False
