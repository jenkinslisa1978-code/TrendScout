"""
Weekly Winning Products Report Generator

Generates weekly reports highlighting top opportunity products.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List

from .report_generator import (
    ReportGenerator,
    ReportType,
    ReportAccessLevel,
    ReportStatus,
    ReportMetadata,
    ReportSection,
    GeneratedReport
)


class WeeklyWinningProductsReport(ReportGenerator):
    """
    Generates Weekly Winning Products Reports
    
    Includes:
    - Top 20 highest opportunity products
    - Trend stage analysis
    - Estimated margins
    - Competition levels
    - Success probability
    - Key opportunity clusters
    - Products becoming saturated
    """
    
    async def generate(self, target_date: datetime = None) -> GeneratedReport:
        """Generate the weekly winning products report"""
        if target_date is None:
            target_date = datetime.now(timezone.utc)
        
        period_start, period_end = self.get_week_bounds(target_date)
        slug = self.generate_slug(ReportType.WEEKLY_WINNING_PRODUCTS, target_date)
        
        # Check if report already exists
        existing = await self.get_report_by_slug(slug)
        if existing and existing.get("metadata", {}).get("status") == "completed":
            return GeneratedReport(**existing)
        
        # Get data
        top_products = await self.get_top_products(limit=20)
        saturating_products = await self.get_saturating_products(limit=10)
        clusters = await self.get_category_clusters()
        
        # Analyze clusters
        cluster_analysis = []
        for category, products in clusters.items():
            if len(products) >= 2:  # Only meaningful clusters
                metrics = await self.calculate_cluster_metrics(products)
                cluster_analysis.append({
                    "category": category,
                    **metrics
                })
        
        # Sort clusters by opportunity
        cluster_analysis.sort(
            key=lambda x: (x.get("growth_momentum", 0) + x.get("avg_success_probability", 0)) / 2,
            reverse=True
        )
        
        # Build sections
        sections = []
        
        # Section 1: Top 20 Products (Full access for Pro+)
        sections.append(ReportSection(
            title="Top 20 Winning Products",
            description="Highest opportunity products ranked by success probability, trend velocity, and margin potential",
            data={
                "products": [
                    self._format_product(p, full_access=True)
                    for p in top_products
                ]
            },
            access_level=ReportAccessLevel.PRO
        ))
        
        # Section 2: Trend Stage Analysis (Free+)
        trend_distribution = self._calculate_trend_distribution(top_products)
        sections.append(ReportSection(
            title="Trend Stage Analysis",
            description="Distribution of products across trend lifecycle stages",
            data={
                "distribution": trend_distribution,
                "insights": self._generate_trend_insights(trend_distribution)
            },
            access_level=ReportAccessLevel.FREE
        ))
        
        # Section 3: Opportunity Clusters (Pro+)
        sections.append(ReportSection(
            title="Key Opportunity Clusters",
            description="Product categories showing strong growth momentum",
            data={
                "clusters": cluster_analysis[:10]
            },
            access_level=ReportAccessLevel.PRO
        ))
        
        # Section 4: Competition Analysis (Free+)
        competition_analysis = self._analyze_competition(top_products)
        sections.append(ReportSection(
            title="Competition Analysis",
            description="Market competition levels across top products",
            data={
                "distribution": competition_analysis["distribution"],
                "low_competition_count": competition_analysis["low_competition_count"],
                "insights": competition_analysis["insights"]
            },
            access_level=ReportAccessLevel.FREE
        ))
        
        # Section 5: Margin Analysis (Pro+)
        margin_analysis = self._analyze_margins(top_products)
        sections.append(ReportSection(
            title="Margin Potential",
            description="Profit margin analysis of top opportunity products",
            data={
                "avg_margin": margin_analysis["avg_margin"],
                "margin_ranges": margin_analysis["ranges"],
                "top_margin_products": margin_analysis["top_margin_products"]
            },
            access_level=ReportAccessLevel.PRO
        ))
        
        # Section 6: Saturation Warning (Elite only)
        sections.append(ReportSection(
            title="Saturation Warning",
            description="Products showing signs of market saturation - consider avoiding",
            data={
                "saturating_products": [
                    self._format_product(p, full_access=True)
                    for p in saturating_products
                ],
                "total_saturating": len(saturating_products)
            },
            access_level=ReportAccessLevel.ELITE
        ))
        
        # Build summary
        summary = {
            "total_products_analyzed": len(top_products),
            "avg_success_probability": round(
                sum(p.get("success_probability", 0) for p in top_products) / len(top_products), 1
            ) if top_products else 0,
            "top_categories": [c["category"] for c in cluster_analysis[:5]],
            "trending_stages": trend_distribution,
            "low_competition_opportunities": competition_analysis["low_competition_count"],
            "avg_margin": margin_analysis["avg_margin"],
            "saturation_warnings": len(saturating_products),
            "week_number": target_date.isocalendar()[1],
            "year": target_date.year
        }
        
        # Build public preview (limited data)
        public_preview = {
            "top_5_products": [
                self._format_product(p, full_access=False)
                for p in top_products[:5]
            ],
            "trend_distribution": trend_distribution,
            "competition_snapshot": {
                "low": competition_analysis["distribution"].get("low", 0),
                "medium": competition_analysis["distribution"].get("medium", 0),
                "high": competition_analysis["distribution"].get("high", 0)
            },
            "top_categories": [c["category"] for c in cluster_analysis[:3]],
            "total_products": len(top_products),
            "teaser_message": f"Unlock the full report to see all {len(top_products)} winning products, detailed margins, and opportunity clusters."
        }
        
        # Create metadata
        metadata = ReportMetadata(
            report_type=ReportType.WEEKLY_WINNING_PRODUCTS,
            title=f"Weekly Winning Products - Week {target_date.isocalendar()[1]}, {target_date.year}",
            description=f"Top {len(top_products)} highest opportunity products for dropshipping and ecommerce",
            period_start=period_start,
            period_end=period_end,
            status=ReportStatus.COMPLETED,
            access_level=ReportAccessLevel.FREE,  # Base access level
            product_count=len(top_products),
            cluster_count=len(cluster_analysis),
            slug=slug
        )
        
        # Create report
        report = GeneratedReport(
            metadata=metadata,
            sections=sections,
            summary=summary,
            public_preview=public_preview
        )
        
        # Save to database
        await self.save_report(report)
        
        return report
    
    def _format_product(self, product: Dict[str, Any], full_access: bool = True) -> Dict[str, Any]:
        """Format product data for report, with optional access restrictions"""
        base = {
            "id": product.get("id"),
            "name": product.get("product_name"),
            "category": product.get("category"),
            "image_url": product.get("image_url"),
            "trend_stage": product.get("trend_stage"),
            "success_probability": product.get("success_probability", 0),
            "competition_level": product.get("competition_level"),
            "trend_score": product.get("trend_score", 0),
            "is_simulated": product.get("data_source") == "simulated"
        }
        
        if full_access:
            base.update({
                "supplier_cost": product.get("supplier_cost", 0),
                "retail_price": product.get("estimated_retail_price", 0),
                "estimated_margin": product.get("estimated_margin", 0),
                "margin_score": product.get("margin_score", 0),
                "market_saturation": product.get("market_saturation", 0),
                "early_trend_score": product.get("early_trend_score", 0),
                "early_trend_label": product.get("early_trend_label"),
                "win_score": product.get("win_score", 0),
                "validation_reasoning": self._get_validation_reasoning(product)
            })
        else:
            # Limited data for public preview
            base["estimated_margin"] = "Unlock for details"
            base["validation_reasoning"] = "Upgrade to see full analysis"
        
        return base
    
    def _get_validation_reasoning(self, product: Dict[str, Any]) -> str:
        """Generate validation reasoning text"""
        success_prob = product.get("success_probability", 0)
        trend_stage = product.get("trend_stage", "stable")
        competition = product.get("competition_level", "medium")
        margin = product.get("estimated_margin", 0)
        
        reasons = []
        
        if success_prob >= 70:
            reasons.append("Strong success probability")
        elif success_prob >= 50:
            reasons.append("Moderate success potential")
        
        if trend_stage in ["exploding", "rising"]:
            reasons.append(f"Currently {trend_stage} in trend cycle")
        elif trend_stage == "early":
            reasons.append("Early trend opportunity")
        
        if competition == "low":
            reasons.append("Low competition makes market entry easier")
        elif competition == "high":
            reasons.append("High competition requires strong differentiation")
        
        if margin >= 30:
            reasons.append(f"Excellent margin potential (£{margin:.2f})")
        elif margin >= 15:
            reasons.append(f"Good margin potential (£{margin:.2f})")
        
        return ". ".join(reasons) if reasons else "Requires further analysis"
    
    def _calculate_trend_distribution(self, products: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of trend stages"""
        distribution = {}
        for p in products:
            stage = p.get("trend_stage", "stable")
            distribution[stage] = distribution.get(stage, 0) + 1
        return distribution
    
    def _generate_trend_insights(self, distribution: Dict[str, int]) -> List[str]:
        """Generate insights from trend distribution"""
        insights = []
        total = sum(distribution.values())
        
        if total == 0:
            return ["No trend data available"]
        
        rising = distribution.get("rising", 0) + distribution.get("exploding", 0)
        early = distribution.get("early", 0)
        saturated = distribution.get("saturated", 0)
        
        if rising / total > 0.5:
            insights.append("Market is highly active with majority of products in growth phase")
        
        if early / total > 0.3:
            insights.append("Strong early trend signals detected - first mover opportunities available")
        
        if saturated / total > 0.2:
            insights.append("Caution: Significant saturation in the market this week")
        
        if not insights:
            insights.append("Balanced market conditions with mixed growth signals")
        
        return insights
    
    def _analyze_competition(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competition levels across products"""
        distribution = {"low": 0, "medium": 0, "high": 0}
        
        for p in products:
            level = p.get("competition_level", "medium")
            distribution[level] = distribution.get(level, 0) + 1
        
        low_count = distribution.get("low", 0)
        total = sum(distribution.values())
        
        insights = []
        if low_count >= 5:
            insights.append(f"{low_count} products with low competition - excellent entry points")
        if distribution.get("high", 0) > total * 0.5:
            insights.append("Most opportunities are in competitive markets - strong positioning required")
        
        return {
            "distribution": distribution,
            "low_competition_count": low_count,
            "insights": insights
        }
    
    def _analyze_margins(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze margin potential across products"""
        margins = [p.get("estimated_margin", 0) for p in products]
        
        if not margins:
            return {"avg_margin": 0, "ranges": {}, "top_margin_products": []}
        
        avg_margin = sum(margins) / len(margins)
        
        # Categorize by margin ranges
        ranges = {
            "excellent_30_plus": len([m for m in margins if m >= 30]),
            "good_20_30": len([m for m in margins if 20 <= m < 30]),
            "moderate_10_20": len([m for m in margins if 10 <= m < 20]),
            "low_under_10": len([m for m in margins if m < 10])
        }
        
        # Top margin products
        top_margin = sorted(products, key=lambda x: x.get("estimated_margin", 0), reverse=True)[:5]
        
        return {
            "avg_margin": round(avg_margin, 2),
            "ranges": ranges,
            "top_margin_products": [
                {
                    "name": p.get("product_name"),
                    "margin": p.get("estimated_margin", 0),
                    "category": p.get("category")
                }
                for p in top_margin
            ]
        }
