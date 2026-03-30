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

    async def send_instant_product_alert(self, to_email: str, product_name: str, category: str, score: int, product_id: str, trend_label: str = "Emerging") -> dict:
        """Send instant product alert email when a high-scoring product matches a subscription."""
        site = self.site_url or "https://trendscout.click"
        score_color = "#10b981" if score >= 70 else "#6366f1" if score >= 50 else "#64748b"
        html = f"""
        <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:520px;margin:0 auto;padding:40px 24px;background:#ffffff;">
          <div style="text-align:center;margin-bottom:24px;">
            <div style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;padding:10px;margin-bottom:8px;">
              <span style="color:#fff;font-size:18px;font-weight:bold;">TS</span>
            </div>
            <h1 style="font-size:18px;font-weight:700;color:#1e293b;margin:8px 0 0;">New Product Alert</h1>
          </div>

          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:20px;text-align:center;margin-bottom:20px;">
            <p style="font-size:12px;color:#64748b;margin:0 0 4px;text-transform:uppercase;letter-spacing:0.5px;">Product Detected</p>
            <h2 style="font-size:20px;font-weight:700;color:#1e293b;margin:0 0 4px;">{product_name}</h2>
            <p style="font-size:13px;color:#94a3b8;margin:0 0 12px;">{category}</p>
            <span style="font-family:monospace;font-size:36px;font-weight:800;color:{score_color};">{score}</span>
            <span style="font-size:14px;color:#94a3b8;">/100</span>
            <div style="margin-top:8px;">
              <span style="display:inline-block;background:{score_color}20;color:{score_color};font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;">
                {trend_label}
              </span>
            </div>
          </div>

          <p style="font-size:13px;color:#64748b;line-height:1.6;text-align:center;margin-bottom:20px;">
            This product matched your alert criteria. Click below to view the full analysis.
          </p>

          <div style="text-align:center;">
            <a href="{site}/product/{product_id}"
               style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 32px;border-radius:10px;">
              View Full Analysis
            </a>
          </div>

          <hr style="border:none;border-top:1px solid #e2e8f0;margin:28px 0;" />
          <p style="font-size:11px;color:#94a3b8;text-align:center;">
            TrendScout &mdash; AI product validation for ecommerce<br/>
            <a href="{site}/product-alerts" style="color:#94a3b8;">Manage your alerts</a>
          </p>
        </div>
        """
        return await self.send_email(to_email, f"New Product Alert: {product_name} (Score {score})", html)

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

    async def send_viability_result_email(self, to_email: str, product_name: str, score: int, verdict: str, summary: str, strengths: list, risks: list) -> dict:
        """Drip Email 1: Instant viability result after email capture."""
        site = self.site_url or "https://trendscout.click"
        score_color = "#10b981" if score >= 65 else "#f59e0b" if score >= 40 else "#ef4444"
        strengths_html = "".join(f'<li style="padding:4px 0;color:#334155;font-size:13px;">{s}</li>' for s in (strengths or []))
        risks_html = "".join(f'<li style="padding:4px 0;color:#334155;font-size:13px;">{r}</li>' for r in (risks or []))
        html = f"""
        <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:560px;margin:0 auto;padding:40px 24px;">
          <div style="text-align:center;margin-bottom:24px;">
            <div style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;padding:10px;">
              <span style="color:#fff;font-size:18px;font-weight:bold;">TS</span>
            </div>
            <h1 style="font-size:20px;font-weight:700;color:#1e293b;margin:10px 0 4px;">Your UK Viability Result</h1>
            <p style="font-size:13px;color:#94a3b8;margin:0;">Here's the analysis you requested</p>
          </div>
          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:24px;text-align:center;margin-bottom:20px;">
            <p style="font-size:13px;color:#64748b;margin:0 0 4px;">Product</p>
            <h2 style="font-size:18px;font-weight:700;color:#1e293b;margin:0 0 12px;">{product_name}</h2>
            <span style="font-family:monospace;font-size:40px;font-weight:800;color:{score_color};">{score}</span>
            <span style="font-size:16px;color:#94a3b8;">/100</span>
            <div style="margin-top:8px;">
              <span style="display:inline-block;background:{score_color}20;color:{score_color};font-size:12px;font-weight:600;padding:4px 12px;border-radius:20px;">{verdict}</span>
            </div>
          </div>
          <p style="font-size:14px;color:#334155;line-height:1.6;margin-bottom:20px;">{summary}</p>
          <table width="100%" cellpadding="0" cellspacing="0"><tr>
            <td style="vertical-align:top;width:50%;padding-right:8px;">
              <h3 style="font-size:13px;font-weight:600;color:#10b981;margin:0 0 6px;">Strengths</h3>
              <ul style="margin:0;padding-left:16px;">{strengths_html}</ul>
            </td>
            <td style="vertical-align:top;width:50%;padding-left:8px;">
              <h3 style="font-size:13px;font-weight:600;color:#ef4444;margin:0 0 6px;">Risks</h3>
              <ul style="margin:0;padding-left:16px;">{risks_html}</ul>
            </td>
          </tr></table>
          <div style="text-align:center;margin-top:24px;">
            <a href="{site}/signup?utm_source=email&utm_medium=drip&utm_campaign=viability_result&utm_content=cta_full_analysis" style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 32px;border-radius:10px;">
              Get Full Analysis — Start Free
            </a>
            <p style="font-size:12px;color:#94a3b8;margin-top:8px;">No credit card needed. Cancel anytime.</p>
          </div>
          <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;" />
          <p style="font-size:11px;color:#94a3b8;text-align:center;">TrendScout &mdash; AI product research for UK ecommerce<br/>Reply "unsubscribe" to stop emails</p>
        </div>
        """
        return await self.send_email(to_email, f"Your viability result: {product_name} scored {score}/100", html)

    async def send_trending_drip_email(self, to_email: str, products: list) -> dict:
        """Drip Email 2 (Day 2): Top trending products this week."""
        site = self.site_url or "https://trendscout.click"
        rows = ""
        for p in products[:3]:
            name = p.get("product_name", p.get("name", "Unknown"))
            score = p.get("launch_score", p.get("viability_score", 0))
            cat = p.get("category", "General")
            color = "#10b981" if score >= 65 else "#6366f1" if score >= 45 else "#64748b"
            rows += f"""
            <tr>
              <td style="padding:12px;border-bottom:1px solid #f1f5f9;">
                <span style="font-weight:600;color:#1e293b;font-size:14px;">{name}</span>
                <br/><span style="font-size:12px;color:#94a3b8;">{cat}</span>
              </td>
              <td style="padding:12px;border-bottom:1px solid #f1f5f9;text-align:center;">
                <span style="font-family:monospace;font-size:20px;font-weight:700;color:{color};">{score}</span>
                <span style="font-size:11px;color:#94a3b8;">/100</span>
              </td>
            </tr>"""
        if not rows:
            rows = '<tr><td colspan="2" style="padding:20px;text-align:center;color:#94a3b8;">Check back soon for new products!</td></tr>'
        html = f"""
        <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:560px;margin:0 auto;padding:40px 24px;">
          <div style="text-align:center;margin-bottom:24px;">
            <div style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;padding:10px;">
              <span style="color:#fff;font-size:18px;font-weight:bold;">TS</span>
            </div>
            <h1 style="font-size:20px;font-weight:700;color:#1e293b;margin:10px 0 4px;">3 Trending Products This Week</h1>
            <p style="font-size:13px;color:#94a3b8;margin:0;">Products gaining traction in the UK right now</p>
          </div>
          <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;">
            <tr style="background:#f8fafc;">
              <th style="padding:10px 12px;text-align:left;font-size:12px;font-weight:600;color:#64748b;">Product</th>
              <th style="padding:10px 12px;text-align:center;font-size:12px;font-weight:600;color:#64748b;">Score</th>
            </tr>
            {rows}
          </table>
          <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;padding:16px;margin:20px 0;text-align:center;">
            <p style="font-size:13px;color:#0369a1;font-weight:600;margin:0 0 4px;">Want the full analysis on these products?</p>
            <p style="font-size:12px;color:#64748b;margin:0;">Start your free trial to see margins, competition, and AI ad angles.</p>
          </div>
          <div style="text-align:center;margin-top:20px;">
            <a href="{site}/signup?utm_source=email&utm_medium=drip&utm_campaign=trending_day2&utm_content=cta_free_trial" style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 32px;border-radius:10px;">
              Start Free Trial
            </a>
          </div>
          <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;" />
          <p style="font-size:11px;color:#94a3b8;text-align:center;">TrendScout &mdash; AI product research for UK ecommerce<br/>Reply "unsubscribe" to stop emails</p>
        </div>
        """
        return await self.send_email(to_email, "3 products trending in the UK this week", html)

    async def send_trial_drip_email(self, to_email: str) -> dict:
        """Drip Email 3 (Day 5): Free trial reminder."""
        site = self.site_url or "https://trendscout.click"
        html = f"""
        <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:560px;margin:0 auto;padding:40px 24px;">
          <div style="text-align:center;margin-bottom:24px;">
            <div style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;padding:10px;">
              <span style="color:#fff;font-size:18px;font-weight:bold;">TS</span>
            </div>
            <h1 style="font-size:22px;font-weight:700;color:#1e293b;margin:10px 0 4px;">Your free trial is waiting</h1>
          </div>
          <p style="font-size:14px;color:#334155;line-height:1.6;">
            A few days ago you checked a product idea on TrendScout. Since then, new products have started trending in the UK.
          </p>
          <p style="font-size:14px;color:#334155;line-height:1.6;">
            With a free trial you get:
          </p>
          <table width="100%" cellpadding="0" cellspacing="0" style="margin:16px 0;">
            <tr><td style="padding:8px 0;font-size:14px;color:#334155;">
              <span style="color:#10b981;font-weight:bold;margin-right:8px;">&#10003;</span> Unlimited product discovery
            </td></tr>
            <tr><td style="padding:8px 0;font-size:14px;color:#334155;">
              <span style="color:#10b981;font-weight:bold;margin-right:8px;">&#10003;</span> Full UK Viability Scores with 7-signal breakdown
            </td></tr>
            <tr><td style="padding:8px 0;font-size:14px;color:#334155;">
              <span style="color:#10b981;font-weight:bold;margin-right:8px;">&#10003;</span> AI-generated ad angles and launch recommendations
            </td></tr>
            <tr><td style="padding:8px 0;font-size:14px;color:#334155;">
              <span style="color:#10b981;font-weight:bold;margin-right:8px;">&#10003;</span> Margin calculator and profitability simulator
            </td></tr>
          </table>
          <div style="background:#fef3c7;border:1px solid #fde68a;border-radius:10px;padding:16px;margin:20px 0;">
            <p style="font-size:13px;color:#92400e;font-weight:600;margin:0 0 4px;">No credit card required</p>
            <p style="font-size:12px;color:#78350f;margin:0;">Try everything free for 7 days. If it's not useful, cancel with one click.</p>
          </div>
          <div style="text-align:center;margin-top:24px;">
            <a href="{site}/signup?utm_source=email&utm_medium=drip&utm_campaign=trial_day5&utm_content=cta_start_trial" style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-size:15px;font-weight:600;text-decoration:none;padding:14px 40px;border-radius:10px;">
              Start Your Free Trial
            </a>
          </div>
          <hr style="border:none;border-top:1px solid #e2e8f0;margin:28px 0;" />
          <p style="font-size:11px;color:#94a3b8;text-align:center;">TrendScout &mdash; AI product research for UK ecommerce<br/>Reply "unsubscribe" to stop emails</p>
        </div>
        """
        return await self.send_email(to_email, "Your free trial is waiting — TrendScout", html)




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


async def send_welcome_email(to_email: str, first_name: str = "") -> bool:
    """Send a welcome email to a new TrendScout user. Returns True on success."""
    if not resend.api_key:
        logger.warning("RESEND_API_KEY not set — skipping welcome email")
        return False

    name = first_name or to_email.split("@")[0].capitalize()
    site = SITE_URL or "https://trendscout.click"

    html = f"""
    <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:560px;margin:0 auto;padding:40px 24px;background:#ffffff;">

      <!-- Header -->
      <div style="text-align:center;margin-bottom:32px;">
        <div style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:14px;padding:12px 16px;margin-bottom:12px;">
          <span style="color:#fff;font-size:22px;font-weight:800;letter-spacing:-0.5px;">TrendScout</span>
        </div>
        <p style="color:#64748b;font-size:13px;margin:4px 0 0;">UK Product Intelligence for Dropshippers</p>
      </div>

      <!-- Hero -->
      <h1 style="font-size:26px;font-weight:800;color:#0f172a;margin:0 0 8px;line-height:1.2;">
        Welcome to TrendScout, {name}! 🎉
      </h1>
      <p style="font-size:15px;color:#475569;line-height:1.7;margin:0 0 28px;">
        You've just unlocked access to the UK's smartest dropshipping product intelligence tool.
        Here's how to get your first winning product in the next 5 minutes.
      </p>

      <!-- Steps -->
      <div style="background:#f8fafc;border-radius:12px;padding:24px;margin-bottom:28px;">
        <p style="font-size:13px;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:1px;margin:0 0 16px;">Get started in 3 steps</p>

        <div style="display:flex;margin-bottom:16px;">
          <div style="min-width:32px;height:32px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;display:flex;align-items:center;justify-content:center;margin-right:14px;margin-top:2px;">
            <span style="color:#fff;font-weight:700;font-size:14px;">1</span>
          </div>
          <div>
            <p style="font-weight:700;color:#0f172a;font-size:14px;margin:0 0 2px;">Browse Trending Products</p>
            <p style="color:#64748b;font-size:13px;margin:0;line-height:1.5;">See what's trending right now across TikTok and UK marketplaces — with real supplier costs and profit margins.</p>
          </div>
        </div>

        <div style="display:flex;margin-bottom:16px;">
          <div style="min-width:32px;height:32px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;display:flex;align-items:center;justify-content:center;margin-right:14px;margin-top:2px;">
            <span style="color:#fff;font-weight:700;font-size:14px;">2</span>
          </div>
          <div>
            <p style="font-weight:700;color:#0f172a;font-size:14px;margin:0 0 2px;">Check the Launch Score</p>
            <p style="color:#64748b;font-size:13px;margin:0;line-height:1.5;">Each product gets a score out of 100 — combining trend velocity, competition level, and UK demand signals.</p>
          </div>
        </div>

        <div style="display:flex;">
          <div style="min-width:32px;height:32px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;display:flex;align-items:center;justify-content:center;margin-right:14px;margin-top:2px;">
            <span style="color:#fff;font-weight:700;font-size:14px;">3</span>
          </div>
          <div>
            <p style="font-weight:700;color:#0f172a;font-size:14px;margin:0 0 2px;">Launch with One Click</p>
            <p style="color:#64748b;font-size:13px;margin:0;line-height:1.5;">Get your ad copy, target audience, profit calculator and supplier link — ready to go in seconds.</p>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div style="text-align:center;margin-bottom:32px;">
        <a href="{site}/trending-products"
           style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:12px;letter-spacing:-0.2px;">
          Browse Trending Products →
        </a>
        <p style="font-size:12px;color:#94a3b8;margin:12px 0 0;">or <a href="{site}/free-tools" style="color:#6366f1;text-decoration:none;">try the free product checker</a></p>
      </div>

      <!-- This week's highlight -->
      <div style="border:1px solid #e2e8f0;border-radius:12px;padding:20px;margin-bottom:28px;">
        <p style="font-size:13px;font-weight:700;color:#0f172a;margin:0 0 6px;">💡 Pro tip for new members</p>
        <p style="font-size:13px;color:#475569;margin:0;line-height:1.6;">
          Filter by <strong>Trend Stage: Rising</strong> on the products page to find items that are growing fast
          but haven't hit peak competition yet — that's your window.
        </p>
      </div>

      <!-- Footer -->
      <hr style="border:none;border-top:1px solid #f1f5f9;margin:24px 0;" />
      <p style="font-size:12px;color:#94a3b8;text-align:center;line-height:1.6;margin:0;">
        TrendScout &mdash; Built for UK dropshippers &nbsp;·&nbsp;
        <a href="{site}/pricing" style="color:#6366f1;text-decoration:none;">View plans</a> &nbsp;·&nbsp;
        <a href="{site}/help" style="color:#6366f1;text-decoration:none;">Help</a>
      </p>
    </div>
    """

    try:
        result = await asyncio.to_thread(
            resend.Emails.send,
            {
                "from": SENDER_EMAIL,
                "to": [to_email],
                "subject": f"Welcome to TrendScout, {name}! Here's how to find your first winning product 🚀",
                "html": html,
            },
        )
        email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
        logger.info(f"Welcome email sent to {to_email} (id: {email_id})")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to_email}: {e}")
        return False
