"""
Monthly Market Trends Report Generator

Generates monthly reports highlighting market trends and category insights.
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


class MonthlyMarketTrendsReport(ReportGenerator):
    """
    Generates Monthly Market Trends Reports
    
    Includes:
    - Emerging product categories
    - Trend clusters from Market Opportunity Radar
    - Demand vs competition analysis
    - Fastest growing product niches
    - Categories to watch next month
    """
    
    async def generate(self, target_date: datetime = None) -> GeneratedReport:
        """Generate the monthly market trends report"""
        if target_date is None:
            target_date = datetime.now(timezone.utc)
        
        period_start, period_end = self.get_month_bounds(target_date)
        slug = self.generate_slug(ReportType.MONTHLY_MARKET_TRENDS, target_date)
        
        # Check if report already exists
        existing = await self.get_report_by_slug(slug)
        if existing and existing.get("metadata", {}).get("status") == "completed":
            return GeneratedReport(**existing)
        
        # Get data
        all_products = await self.get_all_products(limit=500)
        clusters = await self.get_category_clusters()
        
        # Analyze all clusters
        cluster_analysis = []
        for category, products in clusters.items():
            if len(products) >= 2:
                metrics = await self.calculate_cluster_metrics(products)
                cluster_analysis.append({
                    "category": category,
                    **metrics
                })
        
        # Sort clusters by different criteria
        emerging_categories = self._identify_emerging_categories(cluster_analysis)
        fastest_growing = self._identify_fastest_growing(cluster_analysis)
        demand_competition = self._analyze_demand_vs_competition(cluster_analysis)
        categories_to_watch = self._identify_categories_to_watch(cluster_analysis)
        saturating_categories = self._identify_saturating_categories(cluster_analysis)
        
        # Build sections
        sections = []
        
        # Section 1: Emerging Categories (Free+)
        sections.append(ReportSection(
            title="Emerging Product Categories",
            description="Categories showing strong early signals and growth potential",
            data={
                "categories": emerging_categories[:10],
                "insights": self._generate_emerging_insights(emerging_categories)
            },
            access_level=ReportAccessLevel.FREE
        ))
        
        # Section 2: Trend Clusters (Pro+)
        sections.append(ReportSection(
            title="Market Opportunity Clusters",
            description="Product groups showing coordinated growth patterns",
            data={
                "clusters": [
                    {
                        "category": c["category"],
                        "product_count": c["product_count"],
                        "avg_success_probability": c["avg_success_probability"],
                        "dominant_trend_stage": c["dominant_trend_stage"],
                        "growth_momentum": c["growth_momentum"],
                        "top_products": [
                            {
                                "name": p.get("product_name"),
                                "success_probability": p.get("success_probability", 0),
                                "trend_stage": p.get("trend_stage")
                            }
                            for p in c.get("top_products", [])[:3]
                        ]
                    }
                    for c in cluster_analysis[:15]
                ]
            },
            access_level=ReportAccessLevel.PRO
        ))
        
        # Section 3: Demand vs Competition (Free+)
        sections.append(ReportSection(
            title="Demand vs Competition Analysis",
            description="Where demand exceeds competition - optimal entry points",
            data={
                "high_demand_low_competition": demand_competition["favorable"],
                "balanced_markets": demand_competition["balanced"],
                "saturated_markets": demand_competition["saturated"],
                "insights": demand_competition["insights"]
            },
            access_level=ReportAccessLevel.FREE
        ))
        
        # Section 4: Fastest Growing Niches (Pro+)
        sections.append(ReportSection(
            title="Fastest Growing Product Niches",
            description="Categories with the highest growth momentum this month",
            data={
                "top_growing": fastest_growing[:10],
                "growth_metrics": self._calculate_growth_metrics(fastest_growing)
            },
            access_level=ReportAccessLevel.PRO
        ))
        
        # Section 5: Categories to Watch (Elite)
        sections.append(ReportSection(
            title="Categories to Watch Next Month",
            description="Predicted opportunities based on trend velocity and early signals",
            data={
                "watch_list": categories_to_watch[:10],
                "predictions": self._generate_predictions(categories_to_watch)
            },
            access_level=ReportAccessLevel.ELITE
        ))
        
        # Section 6: Saturation Warnings (Elite)
        sections.append(ReportSection(
            title="Market Saturation Warnings",
            description="Categories showing signs of oversaturation - approach with caution",
            data={
                "saturating_categories": saturating_categories[:10],
                "warning_level": self._calculate_warning_level(saturating_categories)
            },
            access_level=ReportAccessLevel.ELITE
        ))
        
        # Build summary
        summary = {
            "total_products_analyzed": len(all_products),
            "total_categories": len(cluster_analysis),
            "emerging_categories_count": len(emerging_categories),
            "fastest_growing_count": len([c for c in fastest_growing if c.get("growth_momentum", 0) > 30]),
            "saturating_categories_count": len(saturating_categories),
            "top_opportunity_categories": [c["category"] for c in cluster_analysis[:5]],
            "month_name": target_date.strftime("%B"),
            "year": target_date.year,
            "market_health": self._assess_market_health(cluster_analysis)
        }
        
        # Build public preview
        public_preview = {
            "top_3_emerging": [
                {
                    "category": c["category"],
                    "product_count": c["product_count"],
                    "growth_momentum": c.get("growth_momentum", 0)
                }
                for c in emerging_categories[:3]
            ],
            "market_snapshot": {
                "total_categories": len(cluster_analysis),
                "growing_categories": len([c for c in cluster_analysis if c.get("growth_momentum", 0) > 20]),
                "declining_categories": len([c for c in cluster_analysis if c.get("growth_momentum", 0) < -10])
            },
            "demand_competition_summary": {
                "favorable_markets": len(demand_competition["favorable"]),
                "saturated_markets": len(demand_competition["saturated"])
            },
            "teaser_message": f"Unlock the full report to see {len(cluster_analysis)} category analyses, growth predictions, and detailed market insights."
        }
        
        # Create metadata
        metadata = ReportMetadata(
            report_type=ReportType.MONTHLY_MARKET_TRENDS,
            title=f"Monthly Market Trends - {target_date.strftime('%B')} {target_date.year}",
            description=f"Comprehensive ecommerce market analysis covering {len(cluster_analysis)} product categories",
            period_start=period_start,
            period_end=period_end,
            status=ReportStatus.COMPLETED,
            access_level=ReportAccessLevel.FREE,
            product_count=len(all_products),
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
    
    def _identify_emerging_categories(
        self, 
        clusters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify categories with strong early trend signals"""
        emerging = []
        
        for cluster in clusters:
            early_count = cluster.get("trend_stages", {}).get("early", 0)
            rising_count = cluster.get("trend_stages", {}).get("rising", 0)
            total = cluster.get("product_count", 1)
            
            # Calculate emergence score
            emergence_score = (
                (early_count / total) * 40 +
                (rising_count / total) * 30 +
                cluster.get("growth_momentum", 0) * 0.3
            )
            
            if emergence_score > 20:  # Threshold for emerging
                emerging.append({
                    **cluster,
                    "emergence_score": round(emergence_score, 1),
                    "signal_strength": "strong" if emergence_score > 50 else "moderate"
                })
        
        emerging.sort(key=lambda x: x.get("emergence_score", 0), reverse=True)
        return emerging
    
    def _identify_fastest_growing(
        self, 
        clusters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify categories with highest growth momentum"""
        growing = [
            c for c in clusters 
            if c.get("growth_momentum", 0) > 0
        ]
        growing.sort(key=lambda x: x.get("growth_momentum", 0), reverse=True)
        return growing
    
    def _analyze_demand_vs_competition(
        self, 
        clusters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze demand relative to competition in each category"""
        favorable = []
        balanced = []
        saturated = []
        
        for cluster in clusters:
            avg_success = cluster.get("avg_success_probability", 50)
            avg_competition = cluster.get("avg_competition_score", 60)
            growth = cluster.get("growth_momentum", 0)
            
            # Calculate demand-competition ratio
            demand_score = avg_success + (growth * 0.5)
            
            if demand_score > avg_competition + 20:
                favorable.append({
                    "category": cluster["category"],
                    "demand_score": round(demand_score, 1),
                    "competition_score": round(avg_competition, 1),
                    "opportunity_gap": round(demand_score - avg_competition, 1),
                    "product_count": cluster["product_count"]
                })
            elif avg_competition > demand_score + 20:
                saturated.append({
                    "category": cluster["category"],
                    "demand_score": round(demand_score, 1),
                    "competition_score": round(avg_competition, 1),
                    "saturation_gap": round(avg_competition - demand_score, 1),
                    "product_count": cluster["product_count"]
                })
            else:
                balanced.append({
                    "category": cluster["category"],
                    "demand_score": round(demand_score, 1),
                    "competition_score": round(avg_competition, 1),
                    "product_count": cluster["product_count"]
                })
        
        favorable.sort(key=lambda x: x.get("opportunity_gap", 0), reverse=True)
        saturated.sort(key=lambda x: x.get("saturation_gap", 0), reverse=True)
        
        insights = []
        if len(favorable) > 3:
            insights.append(f"{len(favorable)} categories show favorable demand-to-competition ratios")
        if len(saturated) > len(favorable):
            insights.append("Market is competitive - focus on differentiation")
        else:
            insights.append("Good opportunity balance in current market")
        
        return {
            "favorable": favorable,
            "balanced": balanced,
            "saturated": saturated,
            "insights": insights
        }
    
    def _identify_categories_to_watch(
        self, 
        clusters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify categories likely to grow next month"""
        watch_list = []
        
        for cluster in clusters:
            # Factors for prediction
            early_signals = cluster.get("trend_stages", {}).get("early", 0)
            rising_signals = cluster.get("trend_stages", {}).get("rising", 0)
            growth = cluster.get("growth_momentum", 0)
            avg_success = cluster.get("avg_success_probability", 0)
            
            # Prediction score based on leading indicators
            prediction_score = (
                early_signals * 15 +
                rising_signals * 10 +
                growth * 0.4 +
                avg_success * 0.3
            )
            
            if prediction_score > 30:
                watch_list.append({
                    "category": cluster["category"],
                    "prediction_score": round(prediction_score, 1),
                    "current_stage": cluster.get("dominant_trend_stage"),
                    "expected_trajectory": self._predict_trajectory(cluster),
                    "confidence": "high" if prediction_score > 60 else "medium",
                    "product_count": cluster["product_count"]
                })
        
        watch_list.sort(key=lambda x: x.get("prediction_score", 0), reverse=True)
        return watch_list
    
    def _predict_trajectory(self, cluster: Dict[str, Any]) -> str:
        """Predict the trajectory of a category"""
        growth = cluster.get("growth_momentum", 0)
        stage = cluster.get("dominant_trend_stage", "stable")
        
        if growth > 40 and stage in ["early", "rising"]:
            return "Strong growth expected"
        elif growth > 20:
            return "Continued growth likely"
        elif growth > 0:
            return "Stable with growth potential"
        elif growth > -10:
            return "Stabilizing"
        else:
            return "Potential decline"
    
    def _identify_saturating_categories(
        self, 
        clusters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify categories showing saturation signs"""
        saturating = []
        
        for cluster in clusters:
            saturated_count = cluster.get("trend_stages", {}).get("saturated", 0)
            declining_count = cluster.get("trend_stages", {}).get("declining", 0)
            total = cluster.get("product_count", 1)
            avg_competition = cluster.get("avg_competition_score", 50)
            
            # Saturation score
            saturation_score = (
                (saturated_count / total) * 40 +
                (declining_count / total) * 30 +
                (avg_competition / 100) * 30
            )
            
            if saturation_score > 40:
                saturating.append({
                    "category": cluster["category"],
                    "saturation_score": round(saturation_score, 1),
                    "warning_level": "high" if saturation_score > 70 else "moderate",
                    "product_count": cluster["product_count"],
                    "recommendation": self._saturation_recommendation(saturation_score)
                })
        
        saturating.sort(key=lambda x: x.get("saturation_score", 0), reverse=True)
        return saturating
    
    def _saturation_recommendation(self, score: float) -> str:
        """Generate recommendation based on saturation score"""
        if score > 70:
            return "Avoid new entries - market is oversaturated"
        elif score > 55:
            return "Proceed with caution - differentiation required"
        else:
            return "Monitor closely - early saturation signals"
    
    def _generate_emerging_insights(
        self, 
        emerging: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate insights from emerging categories"""
        insights = []
        
        if len(emerging) >= 5:
            top_cats = [e["category"] for e in emerging[:3]]
            insights.append(f"Top emerging categories: {', '.join(top_cats)}")
        
        strong_signals = [e for e in emerging if e.get("signal_strength") == "strong"]
        if strong_signals:
            insights.append(f"{len(strong_signals)} categories showing strong emergence signals")
        
        if not insights:
            insights.append("Limited emerging category signals this period")
        
        return insights
    
    def _calculate_growth_metrics(
        self, 
        growing: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate aggregate growth metrics"""
        if not growing:
            return {"avg_growth": 0, "max_growth": 0, "total_growing": 0}
        
        momentums = [g.get("growth_momentum", 0) for g in growing]
        
        return {
            "avg_growth": round(sum(momentums) / len(momentums), 1),
            "max_growth": round(max(momentums), 1),
            "total_growing": len(growing),
            "rapid_growth_count": len([m for m in momentums if m > 50])
        }
    
    def _generate_predictions(
        self, 
        watch_list: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate prediction text for categories to watch"""
        predictions = []
        
        for item in watch_list[:5]:
            predictions.append(
                f"{item['category']}: {item['expected_trajectory']} (confidence: {item['confidence']})"
            )
        
        return predictions
    
    def _calculate_warning_level(
        self, 
        saturating: List[Dict[str, Any]]
    ) -> str:
        """Calculate overall market warning level"""
        if not saturating:
            return "low"
        
        high_warnings = len([s for s in saturating if s.get("warning_level") == "high"])
        
        if high_warnings >= 5:
            return "high"
        elif high_warnings >= 2 or len(saturating) >= 5:
            return "moderate"
        return "low"
    
    def _assess_market_health(
        self, 
        clusters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess overall market health"""
        if not clusters:
            return {"status": "unknown", "score": 0}
        
        total_growth = sum(c.get("growth_momentum", 0) for c in clusters)
        avg_growth = total_growth / len(clusters)
        
        growing_count = len([c for c in clusters if c.get("growth_momentum", 0) > 10])
        declining_count = len([c for c in clusters if c.get("growth_momentum", 0) < -10])
        
        # Health score (0-100)
        health_score = min(100, max(0, 50 + avg_growth + (growing_count - declining_count) * 5))
        
        if health_score >= 70:
            status = "excellent"
        elif health_score >= 55:
            status = "good"
        elif health_score >= 40:
            status = "moderate"
        else:
            status = "challenging"
        
        return {
            "status": status,
            "score": round(health_score, 1),
            "growing_categories": growing_count,
            "declining_categories": declining_count
        }
