"""
Email Service for TrendScout

Handles sending weekly digest emails and Product of the Week emails using Resend API.
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

import resend
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Resend
resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
FRONTEND_URL = os.environ.get('FRONTEND_URL') or os.environ.get('REACT_APP_BACKEND_URL', 'https://www.trendscout.click')


class EmailService:
    def __init__(self):
        self.sender_email = SENDER_EMAIL

    async def send_email(self, to_email: str, subject: str, html_content: str) -> Dict[str, Any]:
        params = {
            "from": self.sender_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        try:
            email = await asyncio.to_thread(resend.Emails.send, params)
            logger.info(f"Email sent to {to_email}, ID: {email.get('id')}")
            return {"status": "success", "email_id": email.get("id"), "recipient": to_email}
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {"status": "error", "error": str(e), "recipient": to_email}

    async def send_weekly_digest(self, to_email: str, user_name: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        html_content = self._generate_weekly_digest_html(user_name, report_data)
        week_num = report_data.get('metadata', {}).get('week_number', datetime.now().isocalendar()[1])
        subject = f"TrendScout Weekly Digest - Week {week_num} Top Products"
        return await self.send_email(to_email, subject, html_content)

    async def send_product_of_the_week(
        self,
        to_email: str,
        user_name: str,
        product: Dict[str, Any],
        referral_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        html_content = self._generate_potw_html(user_name, product, referral_code)
        subject = f"Product of the Week: {product.get('product_name', 'Hot Opportunity')} - TrendScout"
        return await self.send_email(to_email, subject, html_content)

    def _generate_potw_html(self, user_name: str, product: Dict[str, Any], referral_code: Optional[str] = None) -> str:
        product_name = product.get('product_name', 'Unknown Product')
        launch_score = product.get('launch_score', 0)
        category = product.get('category', 'N/A')
        trend_stage = product.get('trend_stage', 'rising')
        margin_range = product.get('margin_range', 'N/A')
        score_color = self._get_score_color(launch_score)
        product_id = product.get('id', '')

        if launch_score >= 80:
            score_label = "Strong Launch"
        elif launch_score >= 60:
            score_label = "Promising"
        elif launch_score >= 40:
            score_label = "Risky"
        else:
            score_label = "Avoid"

        product_url = f"{FRONTEND_URL}/p/{product_id}"
        trending_url = f"{FRONTEND_URL}/trending-products"

        referral_section = ""
        if referral_code:
            referral_link = f"{FRONTEND_URL}/signup?ref={referral_code}"
            referral_section = f"""
            <tr>
                <td style="padding: 0 30px 20px;">
                    <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); border: 1px solid #86efac; border-radius: 12px; padding: 20px; text-align: center;">
                        <div style="font-size: 16px; font-weight: 600; color: #166534; margin-bottom: 8px;">
                            Share TrendScout & Earn Bonus Store Slots
                        </div>
                        <div style="font-size: 13px; color: #15803d; margin-bottom: 16px;">
                            For every friend that signs up, you earn a bonus store slot (up to 5).
                        </div>
                        <a href="{referral_link}" style="display: inline-block; background: #16a34a; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; font-size: 14px;">
                            Share Your Referral Link
                        </a>
                        <div style="margin-top: 12px; font-size: 11px; color: #6b7280;">
                            Your code: <strong>{referral_code}</strong>
                        </div>
                    </div>
                </td>
            </tr>
            """

        # Runner-up products (we'll show placeholders - the actual data is passed in product dict)
        runners_up_html = ""
        runners_up = product.get('_runners_up', [])
        for i, runner in enumerate(runners_up[:3], 2):
            r_score = runner.get('launch_score', 0)
            r_color = self._get_score_color(r_score)
            runners_up_html += f"""
            <tr>
                <td style="padding: 8px 12px; border-bottom: 1px solid #f1f5f9;">
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                        <tr>
                            <td style="width: 24px; vertical-align: middle;">
                                <div style="width: 20px; height: 20px; background: #e2e8f0; border-radius: 50%; text-align: center; line-height: 20px; color: #64748b; font-weight: bold; font-size: 10px;">{i}</div>
                            </td>
                            <td style="padding-left: 10px; vertical-align: middle;">
                                <div style="font-weight: 500; color: #334155; font-size: 13px;">{runner.get('product_name', 'Product')}</div>
                                <div style="font-size: 11px; color: #94a3b8;">{runner.get('category', '')}</div>
                            </td>
                            <td style="width: 50px; text-align: right; vertical-align: middle;">
                                <div style="font-size: 16px; font-weight: bold; color: {r_color}; font-family: monospace;">{r_score}</div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            """

        runners_section = ""
        if runners_up_html:
            runners_section = f"""
            <tr>
                <td style="padding: 0 30px 20px;">
                    <div style="font-size: 14px; font-weight: 600; color: #475569; margin-bottom: 8px;">Also Trending</div>
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                        {runners_up_html}
                    </table>
                </td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f8fafc; padding: 20px 0;">
                <tr>
                    <td align="center">
                        <table cellpadding="0" cellspacing="0" border="0" width="600" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">

                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); padding: 28px; text-align: center;">
                                    <div style="font-size: 22px; font-weight: bold; color: white; letter-spacing: -0.5px;">TrendScout</div>
                                    <div style="font-size: 13px; color: rgba(255,255,255,0.85); margin-top: 6px;">Product of the Week</div>
                                </td>
                            </tr>

                            <!-- Greeting -->
                            <tr>
                                <td style="padding: 28px 30px 16px;">
                                    <div style="font-size: 16px; color: #1e293b;">Hi {user_name or 'there'},</div>
                                    <div style="font-size: 14px; color: #64748b; margin-top: 6px; line-height: 1.5;">
                                        This week's standout product has a Launch Score of <strong style="color: {score_color};">{launch_score}</strong>. Here's why it caught our attention:
                                    </div>
                                </td>
                            </tr>

                            <!-- Featured Product Card -->
                            <tr>
                                <td style="padding: 0 30px 20px;">
                                    <div style="border: 2px solid #e0e7ff; border-radius: 12px; overflow: hidden;">
                                        <div style="background: linear-gradient(135deg, #eef2ff 0%, #faf5ff 100%); padding: 24px; text-align: center;">
                                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #6366f1; font-weight: 600; margin-bottom: 8px;">
                                                #1 Product of the Week
                                            </div>
                                            <div style="font-size: 22px; font-weight: 700; color: #1e293b; margin-bottom: 4px;">
                                                {product_name}
                                            </div>
                                            <div style="font-size: 13px; color: #64748b;">{category}</div>
                                        </div>
                                        <div style="padding: 20px;">
                                            <table cellpadding="0" cellspacing="0" border="0" width="100%">
                                                <tr>
                                                    <td style="text-align: center; padding: 8px; width: 33%;">
                                                        <div style="font-size: 28px; font-weight: bold; color: {score_color}; font-family: monospace;">{launch_score}</div>
                                                        <div style="font-size: 11px; color: #64748b;">Launch Score</div>
                                                        <div style="margin-top: 4px;"><span style="background: {score_color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600;">{score_label}</span></div>
                                                    </td>
                                                    <td style="text-align: center; padding: 8px; width: 33%; border-left: 1px solid #f1f5f9;">
                                                        <div style="font-size: 16px; font-weight: 600; color: #334155; text-transform: capitalize;">{trend_stage}</div>
                                                        <div style="font-size: 11px; color: #64748b;">Trend Stage</div>
                                                    </td>
                                                    <td style="text-align: center; padding: 8px; width: 33%; border-left: 1px solid #f1f5f9;">
                                                        <div style="font-size: 16px; font-weight: 600; color: #10b981;">{margin_range}</div>
                                                        <div style="font-size: 11px; color: #64748b;">Est. Margin</div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div style="padding: 0 20px 20px; text-align: center;">
                                            <a href="{product_url}" style="display: inline-block; background: #4f46e5; color: white; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: 600; font-size: 14px;">
                                                View Full Analysis
                                            </a>
                                        </div>
                                    </div>
                                </td>
                            </tr>

                            {runners_section}

                            <!-- View All Trending -->
                            <tr>
                                <td style="padding: 0 30px 20px; text-align: center;">
                                    <a href="{trending_url}" style="font-size: 14px; color: #4f46e5; font-weight: 500; text-decoration: none;">
                                        See all trending products &rarr;
                                    </a>
                                </td>
                            </tr>

                            {referral_section}

                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f8fafc; padding: 20px 30px; border-top: 1px solid #e2e8f0;">
                                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                                        <tr>
                                            <td style="font-size: 12px; color: #94a3b8; line-height: 1.5;">
                                                You're receiving this because you subscribed to TrendScout product alerts.
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding-top: 8px;">
                                                <a href="{FRONTEND_URL}/settings/notifications" style="font-size: 12px; color: #6366f1; text-decoration: none;">
                                                    Manage email preferences
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return html

    def _generate_weekly_digest_html(self, user_name: str, report_data: Dict[str, Any]) -> str:
        metadata = report_data.get('metadata', {})
        summary = report_data.get('summary', {})
        public_preview = report_data.get('public_preview', {})
        top_products = public_preview.get('top_5_products', [])

        generated_at = metadata.get('generated_at', datetime.now(timezone.utc).isoformat())
        try:
            date_obj = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%B %d, %Y')
        except Exception:
            formatted_date = 'This Week'

        products_html = ""
        for i, product in enumerate(top_products[:5], 1):
            launch_score = product.get('launch_score', product.get('success_probability', 0))
            score_color = self._get_score_color(launch_score)
            products_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                        <tr>
                            <td style="width: 30px; vertical-align: top;">
                                <div style="width: 24px; height: 24px; background: #f59e0b; border-radius: 50%; text-align: center; line-height: 24px; color: white; font-weight: bold; font-size: 12px;">{i}</div>
                            </td>
                            <td style="padding-left: 12px;">
                                <div style="font-weight: 600; color: #1f2937; font-size: 14px;">{product.get('name', product.get('product_name', 'Unknown'))}</div>
                                <div style="font-size: 12px; color: #6b7280; margin-top: 4px;">{product.get('category', 'N/A')} &bull; {product.get('trend_stage', 'N/A')}</div>
                            </td>
                            <td style="width: 80px; text-align: right; vertical-align: top;">
                                <div style="font-size: 20px; font-weight: bold; color: {score_color}; font-family: monospace;">{launch_score:.0f}</div>
                                <div style="font-size: 10px; color: #6b7280;">Launch Score</div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f3f4f6; padding: 20px 0;">
                <tr><td align="center">
                    <table cellpadding="0" cellspacing="0" border="0" width="600" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <tr><td style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); padding: 30px; text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: white;">TrendScout</div>
                            <div style="font-size: 14px; color: rgba(255,255,255,0.9); margin-top: 8px;">Weekly Winning Products Digest</div>
                        </td></tr>
                        <tr><td style="padding: 30px 30px 20px;">
                            <div style="font-size: 18px; color: #1f2937;">Hi {user_name or 'there'},</div>
                            <div style="font-size: 14px; color: #6b7280; margin-top: 8px; line-height: 1.5;">Here's your weekly digest of top products. Generated on {formatted_date}.</div>
                        </td></tr>
                        <tr><td style="padding: 0 30px 20px;">
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f8fafc; border-radius: 8px;">
                                <tr>
                                    <td style="padding: 20px; text-align: center; border-right: 1px solid #e5e7eb;">
                                        <div style="font-size: 28px; font-weight: bold; color: #4f46e5;">{summary.get('total_products_analyzed', 20)}</div>
                                        <div style="font-size: 11px; color: #6b7280; text-transform: uppercase;">Analyzed</div>
                                    </td>
                                    <td style="padding: 20px; text-align: center; border-right: 1px solid #e5e7eb;">
                                        <div style="font-size: 28px; font-weight: bold; color: #10b981;">{summary.get('strong_launch_count', summary.get('launch_opportunities', 0))}</div>
                                        <div style="font-size: 11px; color: #6b7280; text-transform: uppercase;">Strong Launch</div>
                                    </td>
                                    <td style="padding: 20px; text-align: center;">
                                        <div style="font-size: 28px; font-weight: bold; color: #f59e0b;">{summary.get('avg_launch_score', summary.get('avg_success_probability', 0)):.0f}</div>
                                        <div style="font-size: 11px; color: #6b7280; text-transform: uppercase;">Avg Score</div>
                                    </td>
                                </tr>
                            </table>
                        </td></tr>
                        <tr><td style="padding: 0 30px 20px;">
                            <div style="font-size: 16px; font-weight: 600; color: #1f2937; margin-bottom: 12px;">Top 5 Products This Week</div>
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                                {products_html if products_html else '<tr><td style="padding: 20px; text-align: center; color: #6b7280;">No products available</td></tr>'}
                            </table>
                        </td></tr>
                        <tr><td style="padding: 10px 30px 30px; text-align: center;">
                            <a href="{FRONTEND_URL}/reports/weekly-winning-products" style="display: inline-block; background-color: #4f46e5; color: white; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 14px;">View Full Report</a>
                        </td></tr>
                        <tr><td style="background-color: #f8fafc; padding: 20px 30px; border-top: 1px solid #e5e7eb;">
                            <table cellpadding="0" cellspacing="0" border="0" width="100%">
                                <tr><td style="font-size: 12px; color: #6b7280; line-height: 1.5;">You're receiving this because you subscribed to weekly digests from TrendScout.</td></tr>
                                <tr><td style="padding-top: 12px;"><a href="{FRONTEND_URL}/settings/notifications" style="font-size: 12px; color: #4f46e5; text-decoration: none;">Manage email preferences</a></td></tr>
                            </table>
                        </td></tr>
                    </table>
                </td></tr>
            </table>
        </body>
        </html>
        """
        return html

    def _get_score_color(self, score: float) -> str:
        if score >= 80:
            return '#10b981'
        elif score >= 60:
            return '#3b82f6'
        elif score >= 40:
            return '#f59e0b'
        return '#ef4444'

    async def send_product_alert_email(self, to_email: str, notification: Dict[str, Any], product: Dict[str, Any]) -> Dict[str, Any]:
        notification_type = notification.get("notification_type", "alert")
        product_name = notification.get("product_name", "Unknown Product")
        launch_score = notification.get("launch_score", 0)

        subjects = {
            "strong_launch": f"Strong Launch Alert: {product_name} ({launch_score})",
            "exploding_trend": f"Exploding Trend: {product_name}",
            "watchlist_alert": f"Watchlist Alert: {product_name}",
            "score_milestone": f"Score Milestone: {product_name}"
        }
        subject = subjects.get(notification_type, f"TrendScout Alert: {product_name}")
        html = self._generate_alert_email_html(notification, product)
        return await self.send_email(to_email, subject, html)

    def _generate_alert_email_html(self, notification: Dict[str, Any], product: Dict[str, Any]) -> str:
        product_name = notification.get("product_name", "Unknown Product")
        launch_score = notification.get("launch_score", 0)
        trend_stage = notification.get("trend_stage", "unknown")
        estimated_margin = notification.get("estimated_margin", 0)
        category = notification.get("category", "Unknown")
        reason = notification.get("reason", "Opportunity detected")
        title = notification.get("title", "Product Alert")
        is_watchlist = notification.get("is_watchlist", False)
        product_id = notification.get("product_id", "")
        score_color = self._get_score_color(launch_score)

        if launch_score >= 80:
            score_label = "Strong Launch"
        elif launch_score >= 60:
            score_label = "Promising"
        elif launch_score >= 40:
            score_label = "Risky"
        else:
            score_label = "Avoid"

        watchlist_badge = '<span style="background:#8b5cf6;color:white;padding:4px 8px;border-radius:4px;font-size:12px;margin-left:8px;">Watchlist</span>' if is_watchlist else ""
        product_url = f"{FRONTEND_URL}/product/{product_id}"

        html = f"""
        <!DOCTYPE html>
        <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8fafc;">
            <div style="max-width:600px;margin:0 auto;padding:20px;">
                <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:24px;border-radius:12px 12px 0 0;text-align:center;">
                    <h1 style="color:white;margin:0;font-size:24px;">TrendScout</h1>
                    <p style="color:rgba(255,255,255,0.9);margin:8px 0 0 0;font-size:14px;">Product Alert</p>
                </div>
                <div style="background:white;padding:24px;border-bottom:1px solid #e2e8f0;">
                    <h2 style="margin:0;color:#1e293b;font-size:18px;">{title}</h2>
                    <p style="margin:8px 0 0 0;color:#64748b;font-size:14px;">{reason}</p>
                </div>
                <div style="background:white;padding:24px;">
                    <div style="margin-bottom:16px;">
                        <h3 style="margin:0;color:#1e293b;font-size:20px;display:inline;">{product_name}</h3>
                        {watchlist_badge}
                    </div>
                    <div style="background:{score_color}15;border-left:4px solid {score_color};padding:16px;margin-bottom:16px;border-radius:0 8px 8px 0;">
                        <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
                            <td><p style="margin:0;color:#64748b;font-size:12px;text-transform:uppercase;">Launch Score</p><p style="margin:4px 0 0 0;color:{score_color};font-size:32px;font-weight:bold;">{launch_score}</p></td>
                            <td style="text-align:right;"><span style="background:{score_color};color:white;padding:6px 12px;border-radius:20px;font-size:14px;font-weight:600;">{score_label}</span></td>
                        </tr></table>
                    </div>
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom:20px;">
                        <tr>
                            <td style="background:#f8fafc;padding:12px;border-radius:8px;width:50%;"><p style="margin:0;color:#64748b;font-size:12px;">Category</p><p style="margin:4px 0 0 0;color:#1e293b;font-weight:600;">{category}</p></td>
                            <td style="width:12px;"></td>
                            <td style="background:#f8fafc;padding:12px;border-radius:8px;width:50%;"><p style="margin:0;color:#64748b;font-size:12px;">Trend Stage</p><p style="margin:4px 0 0 0;color:#1e293b;font-weight:600;text-transform:capitalize;">{trend_stage}</p></td>
                        </tr>
                    </table>
                    <a href="{product_url}" style="display:block;background:#6366f1;color:white;text-align:center;padding:14px 24px;border-radius:8px;text-decoration:none;font-weight:600;font-size:16px;">View Product Details</a>
                </div>
                <div style="background:#f1f5f9;padding:20px;border-radius:0 0 12px 12px;text-align:center;">
                    <p style="margin:0;color:#64748b;font-size:12px;">You're receiving this because you have alert notifications enabled. <a href="{FRONTEND_URL}/settings/notifications" style="color:#6366f1;">Manage preferences</a></p>
                </div>
            </div>
        </body></html>
        """
        return html


# Singleton instance
email_service = EmailService()
