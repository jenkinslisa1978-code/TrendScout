"""
Report Generator Base Class

Base infrastructure for generating market intelligence reports.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    WEEKLY_WINNING_PRODUCTS = "weekly_winning_products"
    MONTHLY_MARKET_TRENDS = "monthly_market_trends"


class ReportAccessLevel(str, Enum):
    PUBLIC = "public"
    FREE = "free"
    PRO = "pro"
    ELITE = "elite"


class ReportStatus(str, Enum):
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportMetadata(BaseModel):
    """Metadata about a generated report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: ReportType
    title: str
    description: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: ReportStatus = ReportStatus.GENERATING
    access_level: ReportAccessLevel = ReportAccessLevel.FREE
    product_count: int = 0
    cluster_count: int = 0
    is_latest: bool = True
    slug: str = ""  # URL-friendly identifier like "2026-03-week-10"
    

class ReportSection(BaseModel):
    """A section within a report"""
    title: str
    description: str
    data: Dict[str, Any]
    access_level: ReportAccessLevel = ReportAccessLevel.FREE


class GeneratedReport(BaseModel):
    """Complete generated report structure"""
    metadata: ReportMetadata
    sections: List[ReportSection]
    summary: Dict[str, Any]
    public_preview: Dict[str, Any]  # Limited data for public/SEO version


class ReportGenerator:
    """
    Base class for report generators.
    Provides common utilities for all report types.
    """
    
    def __init__(self, db):
        self.db = db
    
    async def get_products_in_period(
        self, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get products updated within a date range"""
        cursor = self.db.products.find(
            {
                "updated_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            },
            {"_id": 0}
        ).sort("win_score", -1).limit(limit)
        
        return await cursor.to_list(limit)
    
    async def get_all_products(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Get all canonical products sorted by win score"""
        cursor = self.db.products.find(
            {"is_canonical": {"$ne": False}},  # Only canonical products
            {"_id": 0}
        ).sort("win_score", -1).limit(limit)
        
        return await cursor.to_list(limit)
    
    async def get_top_products(
        self, 
        limit: int = 20,
        min_score: int = 40
    ) -> List[Dict[str, Any]]:
        """Get top canonical products by launch_score (primary decision metric)"""
        # First try to get products by launch_score
        cursor = self.db.products.find(
            {
                "launch_score": {"$gte": min_score},
                "is_canonical": {"$ne": False}
            },
            {"_id": 0}
        ).sort("launch_score", -1).limit(limit)
        
        products = await cursor.to_list(limit)
        
        # Fallback to win_score if launch_score not populated
        if len(products) < limit:
            cursor = self.db.products.find(
                {
                    "win_score": {"$gte": min_score},
                    "is_canonical": {"$ne": False}
                },
                {"_id": 0}
            ).sort("win_score", -1).limit(limit)
            products = await cursor.to_list(limit)
        
        # Final fallback to trend_score
        if len(products) < limit:
            cursor = self.db.products.find(
                {"is_canonical": {"$ne": False}},
                {"_id": 0}
            ).sort("trend_score", -1).limit(limit)
            products = await cursor.to_list(limit)
        
        return products
    
    async def get_saturating_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get canonical products showing saturation signals"""
        cursor = self.db.products.find(
            {
                "is_canonical": {"$ne": False},
                "$or": [
                    {"market_saturation": {"$gte": 70}},
                    {"competition_level": "high"},
                    {"trend_stage": "saturated"}
                ]
            },
            {"_id": 0}
        ).sort("market_saturation", -1).limit(limit)
        
        return await cursor.to_list(limit)
    
    async def get_category_clusters(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group products by category for cluster analysis"""
        products = await self.get_all_products(500)
        
        clusters = {}
        for product in products:
            category = product.get("category", "Other")
            if category not in clusters:
                clusters[category] = []
            clusters[category].append(product)
        
        return clusters
    
    async def calculate_cluster_metrics(
        self, 
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate aggregate metrics for a product cluster"""
        if not products:
            return {}
        
        total = len(products)
        
        avg_trend_score = sum(p.get("trend_score", 0) for p in products) / total
        avg_success_prob = sum(p.get("success_probability", 0) for p in products) / total
        avg_margin = sum(p.get("estimated_margin", 0) for p in products) / total
        avg_competition = sum(
            {"low": 30, "medium": 60, "high": 90}.get(p.get("competition_level", "medium"), 60)
            for p in products
        ) / total
        
        # Count trend stages
        trend_stages = {}
        for p in products:
            stage = p.get("trend_stage", "stable")
            trend_stages[stage] = trend_stages.get(stage, 0) + 1
        
        # Dominant trend stage
        dominant_stage = max(trend_stages, key=trend_stages.get) if trend_stages else "stable"
        
        # Growth rate
        rising_count = sum(1 for p in products if p.get("trend_stage") in ["rising", "exploding"])
        growth_momentum = (rising_count / total) * 100 if total > 0 else 0
        
        return {
            "product_count": total,
            "avg_trend_score": round(avg_trend_score, 1),
            "avg_success_probability": round(avg_success_prob, 1),
            "avg_margin": round(avg_margin, 2),
            "avg_competition_score": round(avg_competition, 1),
            "trend_stages": trend_stages,
            "dominant_trend_stage": dominant_stage,
            "growth_momentum": round(growth_momentum, 1),
            "top_products": sorted(
                products, 
                key=lambda x: x.get("win_score", 0), 
                reverse=True
            )[:5]
        }
    
    async def save_report(self, report: GeneratedReport) -> str:
        """Save generated report to database"""
        # Mark previous reports of same type as not latest
        await self.db.reports.update_many(
            {
                "metadata.report_type": report.metadata.report_type.value,
                "metadata.is_latest": True
            },
            {"$set": {"metadata.is_latest": False}}
        )
        
        # Convert to dict for MongoDB
        report_dict = report.model_dump()
        report_dict["metadata"]["report_type"] = report.metadata.report_type.value
        report_dict["metadata"]["status"] = report.metadata.status.value
        report_dict["metadata"]["access_level"] = report.metadata.access_level.value
        report_dict["metadata"]["period_start"] = report.metadata.period_start.isoformat()
        report_dict["metadata"]["period_end"] = report.metadata.period_end.isoformat()
        report_dict["metadata"]["generated_at"] = report.metadata.generated_at.isoformat()
        
        # Convert section access levels
        for section in report_dict["sections"]:
            section["access_level"] = section["access_level"]
        
        await self.db.reports.insert_one(report_dict)
        
        return report.metadata.id
    
    async def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report by ID"""
        report = await self.db.reports.find_one(
            {"metadata.id": report_id},
            {"_id": 0}
        )
        return report
    
    async def get_report_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get a specific report by slug"""
        report = await self.db.reports.find_one(
            {"metadata.slug": slug},
            {"_id": 0}
        )
        return report
    
    async def get_latest_report(self, report_type: ReportType) -> Optional[Dict[str, Any]]:
        """Get the latest report of a specific type"""
        report = await self.db.reports.find_one(
            {
                "metadata.report_type": report_type.value,
                "metadata.is_latest": True,
                "metadata.status": "completed"
            },
            {"_id": 0}
        )
        return report
    
    async def get_report_history(
        self, 
        report_type: Optional[ReportType] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get historical reports"""
        query = {"metadata.status": "completed"}
        if report_type:
            query["metadata.report_type"] = report_type.value
        
        cursor = self.db.reports.find(
            query,
            {"_id": 0, "metadata": 1, "summary": 1}
        ).sort("metadata.generated_at", -1).limit(limit)
        
        return await cursor.to_list(limit)
    
    def generate_slug(self, report_type: ReportType, date: datetime) -> str:
        """Generate URL-friendly slug for a report"""
        if report_type == ReportType.WEEKLY_WINNING_PRODUCTS:
            week_num = date.isocalendar()[1]
            return f"{date.year}-week-{week_num}"
        elif report_type == ReportType.MONTHLY_MARKET_TRENDS:
            return f"{date.year}-{date.strftime('%B').lower()}"
        return f"{date.strftime('%Y-%m-%d')}"
    
    def get_week_bounds(self, date: datetime = None) -> tuple:
        """Get start and end of the week containing the given date"""
        if date is None:
            date = datetime.now(timezone.utc)
        
        # Monday as start of week
        start = date - timedelta(days=date.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        end = start + timedelta(days=6)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return start, end
    
    def get_month_bounds(self, date: datetime = None) -> tuple:
        """Get start and end of the month containing the given date"""
        if date is None:
            date = datetime.now(timezone.utc)
        
        start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get last day of month
        if date.month == 12:
            end = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = date.replace(month=date.month + 1, day=1) - timedelta(days=1)
        
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return start, end
