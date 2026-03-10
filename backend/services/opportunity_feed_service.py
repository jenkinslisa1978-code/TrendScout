"""
Opportunity Feed Service

Generates and manages live opportunity feed events for the dashboard.
Creates meaningful, non-spammy events when product signals change significantly.
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class FeedEventType(str, Enum):
    """Types of feed events, ordered by priority"""
    ENTERED_STRONG_LAUNCH = "entered_strong_launch"  # Highest priority
    NEW_HIGH_SCORE = "new_high_score"
    TREND_SPIKE = "trend_spike"
    COMPETITION_INCREASE = "competition_increase"
    APPROACHING_SATURATION = "approaching_saturation"


# Event type configurations
EVENT_CONFIG = {
    FeedEventType.ENTERED_STRONG_LAUNCH: {
        "priority": 1,
        "color": "green",
        "icon": "rocket",
        "title": "Strong Launch Opportunity",
        "description_template": "entered Strong Launch category with score {launch_score}"
    },
    FeedEventType.NEW_HIGH_SCORE: {
        "priority": 2,
        "color": "green", 
        "icon": "star",
        "title": "New High Score Product",
        "description_template": "detected with launch score {launch_score}"
    },
    FeedEventType.TREND_SPIKE: {
        "priority": 3,
        "color": "blue",
        "icon": "trending-up",
        "title": "Trend Velocity Spike",
        "description_template": "trend momentum increased by {change_percent}%"
    },
    FeedEventType.COMPETITION_INCREASE: {
        "priority": 4,
        "color": "amber",
        "icon": "users",
        "title": "Competition Rising",
        "description_template": "competition level changed to {competition_level}"
    },
    FeedEventType.APPROACHING_SATURATION: {
        "priority": 5,
        "color": "red",
        "icon": "alert-triangle",
        "title": "Approaching Saturation",
        "description_template": "market saturation reached {saturation}%"
    }
}


class OpportunityFeedService:
    """
    Service for managing live opportunity feed events.
    
    Design principles:
    - Only create events for meaningful signal changes
    - Avoid noisy/spammy entries
    - Support future features (watchlist alerts, email, push)
    """
    
    # Thresholds for event generation (avoid noise)
    THRESHOLDS = {
        "strong_launch_score": 80,
        "high_score_minimum": 75,
        "trend_spike_percent": 15,  # Minimum % change to trigger
        "competition_change_threshold": 1,  # Level change (e.g., low -> medium)
        "saturation_warning_threshold": 70,
        "min_hours_between_same_event": 4,  # Dedupe window
    }
    
    def __init__(self, db):
        self.db = db
    
    async def create_event(
        self,
        event_type: FeedEventType,
        product: Dict[str, Any],
        reason: str,
        change_data: Optional[Dict[str, Any]] = None,
        confidence: float = 0.8
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new feed event if it's meaningful and not a duplicate.
        
        Args:
            event_type: Type of event
            product: Product data
            reason: Plain-English reason for the event
            change_data: Additional data about what changed
            confidence: Confidence score (0-1)
            
        Returns:
            Created event or None if skipped
        """
        # Check for recent duplicate
        if await self._is_duplicate_event(event_type, product.get('id')):
            return None
        
        config = EVENT_CONFIG[event_type]
        
        event = {
            "id": str(uuid.uuid4()),
            "event_type": event_type.value,
            "priority": config["priority"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            
            # Product data
            "product_id": product.get("id"),
            "product_name": product.get("product_name"),
            "launch_score": product.get("launch_score", 0),
            "launch_score_label": product.get("launch_score_label", "risky"),
            "trend_stage": product.get("trend_stage", "unknown"),
            "trend_score": product.get("trend_score", 0),
            "estimated_margin": product.get("estimated_margin", 0),
            "competition_level": product.get("competition_level", "unknown"),
            "category": product.get("category", "Unknown"),
            
            # Event metadata
            "title": config["title"],
            "reason": reason,
            "color": config["color"],
            "icon": config["icon"],
            "confidence": round(confidence, 2),
            "data_source": product.get("data_source", "mixed"),
            "is_simulated": product.get("data_source") == "simulated",
            
            # Change details
            "change_data": change_data or {},
            
            # For future features
            "is_read": False,
            "user_id": None,  # For watchlist-specific events
            "notified": False,
            "notification_channels": []
        }
        
        # Insert into database (this mutates event and adds _id)
        await self.db.opportunity_feed.insert_one(event)
        
        logger.info(f"Created feed event: {event_type.value} for {product.get('product_name')}")
        
        # Remove _id before returning (ObjectId is not JSON serializable)
        event.pop('_id', None)
        return event
    
    async def _is_duplicate_event(self, event_type: FeedEventType, product_id: str) -> bool:
        """Check if a similar event was created recently"""
        cutoff = datetime.now(timezone.utc) - timedelta(
            hours=self.THRESHOLDS["min_hours_between_same_event"]
        )
        
        existing = await self.db.opportunity_feed.find_one({
            "event_type": event_type.value,
            "product_id": product_id,
            "created_at": {"$gte": cutoff.isoformat()}
        })
        
        return existing is not None
    
    async def get_feed(
        self,
        limit: int = 20,
        user_id: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get feed events sorted by priority and recency.
        
        Args:
            limit: Maximum events to return
            user_id: Filter by user (for watchlist events)
            event_types: Filter by event types
            hours: Only get events from last N hours
            
        Returns:
            List of feed events
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = {
            "created_at": {"$gte": cutoff.isoformat()}
        }
        
        if user_id:
            query["$or"] = [
                {"user_id": user_id},
                {"user_id": None}  # Include global events
            ]
        
        if event_types:
            query["event_type"] = {"$in": event_types}
        
        # Sort by priority (ascending) then by created_at (descending)
        cursor = self.db.opportunity_feed.find(
            query,
            {"_id": 0}
        ).sort([
            ("priority", 1),
            ("created_at", -1)
        ]).limit(limit)
        
        events = await cursor.to_list(limit)
        return events
    
    async def process_product_changes(
        self,
        product: Dict[str, Any],
        previous_state: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a product and generate appropriate feed events.
        Called during automation pipeline.
        
        Args:
            product: Current product data
            previous_state: Previous product state (if available)
            
        Returns:
            List of created events
        """
        events = []
        
        launch_score = product.get("launch_score", 0)
        prev_launch_score = previous_state.get("launch_score", 0) if previous_state else 0
        
        trend_score = product.get("trend_score", 0)
        prev_trend_score = previous_state.get("trend_score", 0) if previous_state else 0
        
        competition_level = product.get("competition_level", "unknown")
        prev_competition = previous_state.get("competition_level") if previous_state else None
        
        market_saturation = product.get("market_saturation", 0)
        
        # 1. Entered Strong Launch (crossed 80 threshold)
        if launch_score >= self.THRESHOLDS["strong_launch_score"] and prev_launch_score < 80:
            event = await self.create_event(
                FeedEventType.ENTERED_STRONG_LAUNCH,
                product,
                reason=f"Launch Score increased to {launch_score}, entering Strong Launch category",
                change_data={
                    "previous_score": prev_launch_score,
                    "new_score": launch_score,
                    "score_change": launch_score - prev_launch_score
                },
                confidence=0.9
            )
            if event:
                events.append(event)
        
        # 2. New High Score Product (first time seen with high score)
        elif launch_score >= self.THRESHOLDS["high_score_minimum"] and not previous_state:
            event = await self.create_event(
                FeedEventType.NEW_HIGH_SCORE,
                product,
                reason=f"New product detected with strong launch score of {launch_score}",
                change_data={"launch_score": launch_score},
                confidence=0.85
            )
            if event:
                events.append(event)
        
        # 3. Trend Spike
        if prev_trend_score > 0:
            trend_change = ((trend_score - prev_trend_score) / prev_trend_score) * 100
            if trend_change >= self.THRESHOLDS["trend_spike_percent"]:
                event = await self.create_event(
                    FeedEventType.TREND_SPIKE,
                    product,
                    reason=f"Trend momentum surged {trend_change:.0f}% - growing market interest",
                    change_data={
                        "previous_trend": prev_trend_score,
                        "new_trend": trend_score,
                        "change_percent": round(trend_change, 1)
                    },
                    confidence=0.8
                )
                if event:
                    events.append(event)
        
        # 4. Competition Increase
        competition_order = ["low", "medium", "high", "very_high"]
        if prev_competition and competition_level != prev_competition:
            try:
                prev_idx = competition_order.index(prev_competition)
                curr_idx = competition_order.index(competition_level)
                if curr_idx > prev_idx:
                    event = await self.create_event(
                        FeedEventType.COMPETITION_INCREASE,
                        product,
                        reason=f"Competition rose from {prev_competition} to {competition_level} - monitor closely",
                        change_data={
                            "previous_level": prev_competition,
                            "new_level": competition_level
                        },
                        confidence=0.75
                    )
                    if event:
                        events.append(event)
            except ValueError:
                pass  # Invalid competition level
        
        # 5. Approaching Saturation
        if market_saturation >= self.THRESHOLDS["saturation_warning_threshold"]:
            prev_saturation = previous_state.get("market_saturation", 0) if previous_state else 0
            if prev_saturation < self.THRESHOLDS["saturation_warning_threshold"]:
                event = await self.create_event(
                    FeedEventType.APPROACHING_SATURATION,
                    product,
                    reason=f"Market saturation reached {market_saturation}% - opportunity window narrowing",
                    change_data={
                        "previous_saturation": prev_saturation,
                        "new_saturation": market_saturation
                    },
                    confidence=0.7
                )
                if event:
                    events.append(event)
        
        return events
    
    async def cleanup_old_events(self, days: int = 7):
        """Remove feed events older than specified days"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.opportunity_feed.delete_many({
            "created_at": {"$lt": cutoff.isoformat()}
        })
        logger.info(f"Cleaned up {result.deleted_count} old feed events")
        return result.deleted_count
    
    async def mark_as_read(self, event_ids: List[str], user_id: str):
        """Mark events as read for a user"""
        await self.db.opportunity_feed.update_many(
            {"id": {"$in": event_ids}},
            {"$set": {"is_read": True}}
        )
    
    async def get_feed_stats(self) -> Dict[str, Any]:
        """Get statistics about the feed"""
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        
        total = await self.db.opportunity_feed.count_documents({})
        last_24h_count = await self.db.opportunity_feed.count_documents({
            "created_at": {"$gte": last_24h.isoformat()}
        })
        
        # Count by type
        pipeline = [
            {"$match": {"created_at": {"$gte": last_24h.isoformat()}}},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}}
        ]
        type_counts = await self.db.opportunity_feed.aggregate(pipeline).to_list(None)
        
        return {
            "total_events": total,
            "last_24h": last_24h_count,
            "by_type": {item["_id"]: item["count"] for item in type_counts}
        }


# Factory function to create service instance
def create_feed_service(db) -> OpportunityFeedService:
    return OpportunityFeedService(db)
