"""
Email Service for ViralScout

Handles sending weekly digest emails to subscribed users using Resend API.
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


class EmailService:
    """
    Service for sending emails via Resend.
    """
    
    def __init__(self):
        self.sender_email = SENDER_EMAIL
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> Dict[str, Any]:
        """
        Send an email using Resend API.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            
        Returns:
            Dict with status and email_id
        """
        params = {
            "from": self.sender_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        
        try:
            # Run sync SDK in thread to keep FastAPI non-blocking
            email = await asyncio.to_thread(resend.Emails.send, params)
            logger.info(f"Email sent to {to_email}, ID: {email.get('id')}")
            return {
                "status": "success",
                "email_id": email.get("id"),
                "recipient": to_email
            }
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "recipient": to_email
            }
    
    async def send_weekly_digest(
        self,
        to_email: str,
        user_name: str,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send weekly winning products digest email.
        
        Args:
            to_email: Recipient email address
            user_name: User's display name
            report_data: Weekly report data
            
        Returns:
            Send result dict
        """
        # Generate email content
        html_content = self._generate_weekly_digest_html(user_name, report_data)
        
        # Get week info for subject
        week_num = report_data.get('metadata', {}).get('week_number', datetime.now().isocalendar()[1])
        subject = f"ViralScout Weekly Digest - Week {week_num} Top Products"
        
        return await self.send_email(to_email, subject, html_content)
    
    def _generate_weekly_digest_html(
        self,
        user_name: str,
        report_data: Dict[str, Any]
    ) -> str:
        """
        Generate HTML content for weekly digest email.
        Uses inline CSS and table layout for email client compatibility.
        """
        metadata = report_data.get('metadata', {})
        summary = report_data.get('summary', {})
        public_preview = report_data.get('public_preview', {})
        
        # Get top products
        top_products = public_preview.get('top_5_products', [])
        
        # Format date
        generated_at = metadata.get('generated_at', datetime.now(timezone.utc).isoformat())
        try:
            date_obj = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%B %d, %Y')
        except:
            formatted_date = 'This Week'
        
        # Build products HTML
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
                                <div style="width: 24px; height: 24px; background: #f59e0b; border-radius: 50%; text-align: center; line-height: 24px; color: white; font-weight: bold; font-size: 12px;">
                                    {i}
                                </div>
                            </td>
                            <td style="padding-left: 12px;">
                                <div style="font-weight: 600; color: #1f2937; font-size: 14px;">
                                    {product.get('name', product.get('product_name', 'Unknown Product'))}
                                </div>
                                <div style="font-size: 12px; color: #6b7280; margin-top: 4px;">
                                    {product.get('category', 'N/A')} &bull; {product.get('trend_stage', 'N/A')}
                                </div>
                            </td>
                            <td style="width: 80px; text-align: right; vertical-align: top;">
                                <div style="font-size: 20px; font-weight: bold; color: {score_color}; font-family: monospace;">
                                    {launch_score:.0f}
                                </div>
                                <div style="font-size: 10px; color: #6b7280;">
                                    Launch Score
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            """
        
        # Main email HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f3f4f6; padding: 20px 0;">
                <tr>
                    <td align="center">
                        <table cellpadding="0" cellspacing="0" border="0" width="600" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                            
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); padding: 30px; text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: white;">
                                        ViralScout
                                    </div>
                                    <div style="font-size: 14px; color: rgba(255,255,255,0.9); margin-top: 8px;">
                                        Weekly Winning Products Digest
                                    </div>
                                </td>
                            </tr>
                            
                            <!-- Greeting -->
                            <tr>
                                <td style="padding: 30px 30px 20px;">
                                    <div style="font-size: 18px; color: #1f2937;">
                                        Hi {user_name or 'there'},
                                    </div>
                                    <div style="font-size: 14px; color: #6b7280; margin-top: 8px; line-height: 1.5;">
                                        Here's your weekly digest of top products with the best launch potential.
                                        Generated on {formatted_date}.
                                    </div>
                                </td>
                            </tr>
                            
                            <!-- Stats Summary -->
                            <tr>
                                <td style="padding: 0 30px 20px;">
                                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f8fafc; border-radius: 8px;">
                                        <tr>
                                            <td style="padding: 20px; text-align: center; border-right: 1px solid #e5e7eb;">
                                                <div style="font-size: 28px; font-weight: bold; color: #4f46e5;">
                                                    {summary.get('total_products_analyzed', 20)}
                                                </div>
                                                <div style="font-size: 11px; color: #6b7280; text-transform: uppercase;">
                                                    Products Analyzed
                                                </div>
                                            </td>
                                            <td style="padding: 20px; text-align: center; border-right: 1px solid #e5e7eb;">
                                                <div style="font-size: 28px; font-weight: bold; color: #10b981;">
                                                    {summary.get('strong_launch_count', summary.get('launch_opportunities', 0))}
                                                </div>
                                                <div style="font-size: 11px; color: #6b7280; text-transform: uppercase;">
                                                    Strong Launch
                                                </div>
                                            </td>
                                            <td style="padding: 20px; text-align: center;">
                                                <div style="font-size: 28px; font-weight: bold; color: #f59e0b;">
                                                    {summary.get('avg_launch_score', summary.get('avg_success_probability', 0)):.0f}
                                                </div>
                                                <div style="font-size: 11px; color: #6b7280; text-transform: uppercase;">
                                                    Avg Score
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            
                            <!-- Top Products Section -->
                            <tr>
                                <td style="padding: 0 30px 20px;">
                                    <div style="font-size: 16px; font-weight: 600; color: #1f2937; margin-bottom: 12px;">
                                        Top 5 Products This Week
                                    </div>
                                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                                        {products_html if products_html else '<tr><td style="padding: 20px; text-align: center; color: #6b7280;">No products available</td></tr>'}
                                    </table>
                                </td>
                            </tr>
                            
                            <!-- CTA Button -->
                            <tr>
                                <td style="padding: 10px 30px 30px; text-align: center;">
                                    <a href="https://viralscout.com/reports/weekly-winning-products" style="display: inline-block; background-color: #4f46e5; color: white; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 14px;">
                                        View Full Report
                                    </a>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f8fafc; padding: 20px 30px; border-top: 1px solid #e5e7eb;">
                                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                                        <tr>
                                            <td style="font-size: 12px; color: #6b7280; line-height: 1.5;">
                                                You're receiving this email because you subscribed to weekly digests from ViralScout.
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding-top: 12px;">
                                                <a href="https://viralscout.com/settings/notifications" style="font-size: 12px; color: #4f46e5; text-decoration: none;">
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
    
    def _get_score_color(self, score: float) -> str:
        """Get color hex for launch score"""
        if score >= 80:
            return '#10b981'  # Green
        elif score >= 60:
            return '#3b82f6'  # Blue
        elif score >= 40:
            return '#f59e0b'  # Amber
        return '#ef4444'  # Red


# Singleton instance
email_service = EmailService()
