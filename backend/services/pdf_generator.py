"""
PDF Report Generator Service

Generates professional PDF reports for weekly and monthly market intelligence.
Uses ReportLab for PDF generation.
"""

import io
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    Generates professional PDF reports from report data.
    """
    
    # Brand colors
    COLORS = {
        'primary': colors.HexColor('#4F46E5'),      # Indigo
        'secondary': colors.HexColor('#6366F1'),    # Lighter indigo
        'success': colors.HexColor('#10B981'),      # Green
        'warning': colors.HexColor('#F59E0B'),      # Amber
        'danger': colors.HexColor('#EF4444'),       # Red
        'info': colors.HexColor('#3B82F6'),         # Blue
        'text': colors.HexColor('#1F2937'),         # Dark gray
        'muted': colors.HexColor('#6B7280'),        # Gray
        'light': colors.HexColor('#F3F4F6'),        # Light gray
        'white': colors.white,
    }
    
    # Launch score colors
    LAUNCH_COLORS = {
        'strong_launch': colors.HexColor('#10B981'),  # Green
        'promising': colors.HexColor('#3B82F6'),       # Blue
        'risky': colors.HexColor('#F59E0B'),           # Amber
        'avoid': colors.HexColor('#EF4444'),           # Red
    }
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.COLORS['primary'],
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.COLORS['muted'],
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.COLORS['primary'],
            spaceBefore=20,
            spaceAfter=10
        ))
        
        # Subsection header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=self.COLORS['text'],
            spaceBefore=15,
            spaceAfter=8
        ))
        
        # Custom body text (different name to avoid conflict)
        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.COLORS['text'],
            spaceAfter=8,
            leading=14
        ))
        
        # Stat value
        self.styles.add(ParagraphStyle(
            name='StatValue',
            parent=self.styles['Normal'],
            fontSize=20,
            textColor=self.COLORS['primary'],
            alignment=TA_CENTER
        ))
        
        # Stat label
        self.styles.add(ParagraphStyle(
            name='StatLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.COLORS['muted'],
            alignment=TA_CENTER
        ))
    
    def generate_weekly_report_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate PDF for weekly winning products report.
        
        Args:
            report_data: Report data from the reports API
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        story = []
        
        # Extract data
        metadata = report_data.get('metadata', {})
        summary = report_data.get('summary', {})
        sections = report_data.get('sections', [])
        public_preview = report_data.get('public_preview', {})
        
        # Header
        story.extend(self._build_header(
            title=metadata.get('title', 'Weekly Winning Products Report'),
            subtitle=f"Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y')}"
        ))
        
        # Executive Summary
        story.extend(self._build_executive_summary(summary))
        
        # Top Products Section - try multiple sources
        top_products = self._extract_products_from_sections(sections, 'Top 20 Winning Products')
        
        # Fallback to public preview if no products found
        if not top_products:
            top_products = public_preview.get('top_5_products', [])
        
        if top_products and isinstance(top_products, list):
            story.extend(self._build_products_table(
                title="Top Winning Products",
                products=top_products[:15]
            ))
        
        # Category Breakdown
        categories = self._extract_section_data(sections, 'Category Performance')
        if categories:
            story.extend(self._build_category_table(categories))
        
        # Market Insights
        story.extend(self._build_market_insights(summary))
        
        # Footer
        story.extend(self._build_footer())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _extract_products_from_sections(self, sections: List, section_title: str) -> List:
        """Extract products list from a section"""
        for section in sections:
            if isinstance(section, dict):
                title = section.get('title', '')
                if section_title.lower() in title.lower():
                    data = section.get('data')
                    if data is None:
                        continue
                    # Data might be a dict with 'products' key or a list directly
                    if isinstance(data, dict):
                        products = data.get('products', [])
                        if isinstance(products, list):
                            return products
                    elif isinstance(data, list):
                        return data
        return []
        
        # Category Breakdown
        categories = self._extract_section_data(sections, 'Category Performance')
        if categories:
            story.extend(self._build_category_table(categories))
        
        # Market Insights
        story.extend(self._build_market_insights(summary))
        
        # Footer
        story.extend(self._build_footer())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_monthly_report_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate PDF for monthly market trends report.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        story = []
        
        metadata = report_data.get('metadata', {})
        summary = report_data.get('summary', {})
        sections = report_data.get('sections', [])
        
        # Header
        story.extend(self._build_header(
            title=metadata.get('title', 'Monthly Market Trends Report'),
            subtitle=f"Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y')}"
        ))
        
        # Executive Summary
        story.extend(self._build_executive_summary(summary))
        
        # Emerging Categories
        emerging = self._extract_section_data(sections, 'Emerging Categories')
        if emerging:
            story.extend(self._build_emerging_categories(emerging))
        
        # Top Products
        top_products = self._extract_products_from_sections(sections, 'Top Products')
        if top_products and isinstance(top_products, list):
            story.extend(self._build_products_table(
                title="Top Products This Month",
                products=top_products[:10]
            ))
        
        # Market Overview
        story.extend(self._build_market_overview(summary))
        
        # Footer
        story.extend(self._build_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _build_header(self, title: str, subtitle: str) -> List:
        """Build report header section"""
        elements = []
        
        # Brand name
        elements.append(Paragraph(
            "ViralScout",
            ParagraphStyle(
                'Brand',
                parent=self.styles['Normal'],
                fontSize=14,
                textColor=self.COLORS['primary'],
                alignment=TA_CENTER,
                spaceAfter=5
            )
        ))
        
        # Title
        elements.append(Paragraph(title, self.styles['ReportTitle']))
        
        # Subtitle
        elements.append(Paragraph(subtitle, self.styles['ReportSubtitle']))
        
        # Divider
        elements.append(HRFlowable(
            width="100%",
            thickness=2,
            color=self.COLORS['primary'],
            spaceAfter=20
        ))
        
        return elements
    
    def _build_executive_summary(self, summary: Dict[str, Any]) -> List:
        """Build executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Stats grid
        stats = [
            ('Products Analyzed', str(summary.get('total_products_analyzed', 0))),
            ('Avg Launch Score', f"{summary.get('avg_launch_score', summary.get('avg_success_probability', 0)):.0f}"),
            ('Strong Launch', str(summary.get('strong_launch_count', summary.get('launch_opportunities', 0)))),
            ('Top Category', self._truncate_text(summary.get('top_category', 'N/A'), 15)),
        ]
        
        # Create stats table
        stats_data = [[
            self._create_stat_cell(label, value) for label, value in stats
        ]]
        
        stats_table = Table(stats_data, colWidths=[120, 120, 120, 120])
        stats_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['light']),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['primary']),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Key insights
        if summary.get('key_insight') or summary.get('market_insight'):
            insight = summary.get('key_insight') or summary.get('market_insight', '')
            elements.append(Paragraph(
                f"<b>Key Insight:</b> {insight}",
                self.styles['ReportBody']
            ))
        
        return elements
    
    def _create_stat_cell(self, label: str, value: str) -> List:
        """Create a stat cell with value and label"""
        return [
            Paragraph(str(value), self.styles['StatValue']),
            Paragraph(label, self.styles['StatLabel'])
        ]
    
    def _build_products_table(self, title: str, products: List[Dict]) -> List:
        """Build products table section"""
        elements = []
        
        elements.append(Paragraph(title, self.styles['SectionHeader']))
        
        if not products:
            elements.append(Paragraph("No products available.", self.styles['ReportBody']))
            return elements
        
        # Table header
        header = ['#', 'Product Name', 'Launch Score', 'Category', 'Trend']
        
        # Table data
        data = [header]
        for i, product in enumerate(products[:15], 1):
            launch_score = product.get('launch_score', product.get('success_probability', 0))
            launch_label = self._get_launch_label(launch_score)
            
            row = [
                str(i),
                self._truncate_text(product.get('name', product.get('product_name', 'Unknown')), 30),
                f"{launch_score:.0f} ({launch_label})",
                self._truncate_text(product.get('category', 'N/A'), 15),
                product.get('trend_stage', 'N/A')
            ]
            data.append(row)
        
        # Create table
        col_widths = [30, 180, 100, 90, 70]
        table = Table(data, colWidths=col_widths)
        
        # Table styling
        style = TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Body
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Rank column
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Score column
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS['light']]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['muted']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
        
        # Color code launch scores
        for i, product in enumerate(products[:15], 1):
            launch_score = product.get('launch_score', product.get('success_probability', 0))
            color = self._get_launch_color(launch_score)
            style.add('TEXTCOLOR', (2, i), (2, i), color)
        
        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_category_table(self, categories: Any) -> List:
        """Build category breakdown table"""
        elements = []
        
        elements.append(Paragraph("Category Performance", self.styles['SectionHeader']))
        
        if isinstance(categories, dict):
            cat_list = categories.get('categories', [])
        elif isinstance(categories, list):
            cat_list = categories
        else:
            cat_list = []
        
        if not cat_list:
            elements.append(Paragraph("No category data available.", self.styles['ReportBody']))
            return elements
        
        # Table header
        header = ['Category', 'Products', 'Avg Score', 'Trend']
        data = [header]
        
        for cat in cat_list[:10]:
            if isinstance(cat, dict):
                row = [
                    self._truncate_text(cat.get('name', cat.get('category', 'Unknown')), 25),
                    str(cat.get('product_count', cat.get('count', 0))),
                    f"{cat.get('avg_score', cat.get('avg_launch_score', 0)):.0f}",
                    cat.get('trend', cat.get('growth', 'stable'))
                ]
                data.append(row)
        
        if len(data) > 1:
            table = Table(data, colWidths=[180, 80, 80, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS['light']]),
                ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['muted']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _build_emerging_categories(self, emerging: Any) -> List:
        """Build emerging categories section"""
        elements = []
        
        elements.append(Paragraph("Emerging Categories", self.styles['SectionHeader']))
        
        if isinstance(emerging, dict):
            cat_list = emerging.get('categories', [])
        elif isinstance(emerging, list):
            cat_list = emerging
        else:
            cat_list = []
        
        if not cat_list:
            elements.append(Paragraph("No emerging category data available.", self.styles['ReportBody']))
            return elements
        
        for cat in cat_list[:5]:
            if isinstance(cat, dict):
                name = cat.get('name', cat.get('category', 'Unknown'))
                growth = cat.get('growth_rate', cat.get('growth', 0))
                elements.append(Paragraph(
                    f"<b>{name}</b> - Growth: {growth}%",
                    self.styles['ReportBody']
                ))
        
        elements.append(Spacer(1, 15))
        return elements
    
    def _build_market_insights(self, summary: Dict[str, Any]) -> List:
        """Build market insights section"""
        elements = []
        
        elements.append(Paragraph("Market Insights", self.styles['SectionHeader']))
        
        insights = []
        
        # Generate insights based on data
        strong_count = summary.get('strong_launch_count', summary.get('launch_opportunities', 0))
        if strong_count > 0:
            insights.append(f"{strong_count} products show strong launch potential this week.")
        
        low_comp = summary.get('low_competition_count', summary.get('low_competition_opportunities', 0))
        if low_comp > 0:
            insights.append(f"{low_comp} opportunities identified with low competition.")
        
        top_cat = summary.get('top_category', '')
        if top_cat:
            insights.append(f"Top performing category: {top_cat}")
        
        hot_count = summary.get('hot_categories_count', 0)
        if hot_count > 0:
            insights.append(f"{hot_count} categories showing strong momentum.")
        
        if not insights:
            insights.append("Market conditions are stable with moderate opportunities.")
        
        for insight in insights:
            elements.append(Paragraph(f"• {insight}", self.styles['ReportBody']))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _build_market_overview(self, summary: Dict[str, Any]) -> List:
        """Build monthly market overview section"""
        elements = []
        
        elements.append(Paragraph("Market Overview", self.styles['SectionHeader']))
        
        overview_text = summary.get('market_overview', summary.get('summary_text', ''))
        if overview_text:
            elements.append(Paragraph(overview_text, self.styles['ReportBody']))
        else:
            elements.append(Paragraph(
                "This month's market analysis shows continued opportunities in trending product categories. "
                "Focus on products with strong launch scores (80+) for best results.",
                self.styles['ReportBody']
            ))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _build_footer(self) -> List:
        """Build report footer"""
        elements = []
        
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=self.COLORS['muted'],
            spaceBefore=10,
            spaceAfter=10
        ))
        
        elements.append(Paragraph(
            f"Report generated by ViralScout on {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')}",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=self.COLORS['muted'],
                alignment=TA_CENTER
            )
        ))
        
        elements.append(Paragraph(
            "This report contains data-driven insights for product research purposes.",
            ParagraphStyle(
                'Disclaimer',
                parent=self.styles['Normal'],
                fontSize=7,
                textColor=self.COLORS['muted'],
                alignment=TA_CENTER
            )
        ))
        
        return elements
    
    def _extract_section_data(self, sections: List, section_title: str) -> Any:
        """Extract data from a specific section"""
        for section in sections:
            if isinstance(section, dict):
                title = section.get('title', '')
                if section_title.lower() in title.lower():
                    return section.get('data', section)
        return None
    
    def _get_launch_label(self, score: float) -> str:
        """Get launch score label"""
        if score >= 80:
            return 'Strong'
        elif score >= 60:
            return 'Promising'
        elif score >= 40:
            return 'Risky'
        return 'Avoid'
    
    def _get_launch_color(self, score: float) -> colors.Color:
        """Get color for launch score"""
        if score >= 80:
            return self.LAUNCH_COLORS['strong_launch']
        elif score >= 60:
            return self.LAUNCH_COLORS['promising']
        elif score >= 40:
            return self.LAUNCH_COLORS['risky']
        return self.LAUNCH_COLORS['avoid']
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to max length"""
        if not text:
            return 'N/A'
        text = str(text)
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + '...'


# Singleton instance
pdf_generator = PDFReportGenerator()
