"""
Notification Service

Handles in-app and email notifications for product alerts.
Supports user preferences, quiet hours, deduplication, and watchlist priority.
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta, time
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Types of notifications"""
    STRONG_LAUNCH = "strong_launch"           # Product entered Strong Launch (score >= 80)
    EXPLODING_TREND = "exploding_trend"       # Product trend became "exploding"
    WATCHLIST_ALERT = "watchlist_alert"       # Watchlist item has significant change
    SCORE_MILESTONE = "score_milestone"       # Product crossed user's threshold
    RADAR_DETECTED = "radar_detected"         # Product crossed radar scoring thresholds


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    IN_APP = "in_app"
    EMAIL = "email"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    HIGH = "high"       # Watchlist items, very high scores
    MEDIUM = "medium"   # Strong launches, exploding trends
    LOW = "low"         # Other alerts


# Default user preferences
DEFAULT_PREFERENCES = {
    "email_enabled": True,
    "in_app_enabled": True,
    "alert_threshold": 80,
    "quiet_hours_enabled": False,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "08:00",
    "watchlist_priority_enabled": True,
    "notification_types": {
        "strong_launch": True,
        "exploding_trend": True,
        "watchlist_alert": True,
        "score_milestone": True,
        "radar_detected": True
    }
}


class NotificationService:
    """
    Service for managing user notifications.
    
    Features:
    - In-app notifications with bell icon
    - Email alerts via Resend
    - User preferences (threshold, quiet hours, etc.)
    - Watchlist priority
    - Deduplication (4-hour window for same product)
    """
    
    DEDUP_WINDOW_HOURS = 4  # Don't send same notification within this window
    
    def __init__(self, db):
        self.db = db
        self._email_service = None
    
    @property
    def email_service(self):
        """Lazy load email service"""
        if self._email_service is None:
            from services.email_service import EmailService
            self._email_service = EmailService()
        return self._email_service
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's notification preferences, create defaults if not exists"""
        prefs = await self.db.notification_preferences.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        if not prefs:
            prefs = {
                "user_id": user_id,
                **DEFAULT_PREFERENCES,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await self.db.notification_preferences.insert_one(prefs)
            prefs.pop("_id", None)
        
        return prefs
    
    async def update_user_preferences(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user's notification preferences"""
        # Validate updates
        valid_fields = {
            "email_enabled", "in_app_enabled", "alert_threshold",
            "quiet_hours_enabled", "quiet_hours_start", "quiet_hours_end",
            "watchlist_priority_enabled", "notification_types"
        }
        
        filtered_updates = {k: v for k, v in updates.items() if k in valid_fields}
        filtered_updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await self.db.notification_preferences.update_one(
            {"user_id": user_id},
            {"$set": filtered_updates},
            upsert=True
        )
        
        return await self.get_user_preferences(user_id)
    
    def _is_quiet_hours(self, prefs: Dict[str, Any]) -> bool:
        """Check if current time is within user's quiet hours"""
        if not prefs.get("quiet_hours_enabled"):
            return False
        
        try:
            now = datetime.now(timezone.utc).time()
            start_str = prefs.get("quiet_hours_start", "22:00")
            end_str = prefs.get("quiet_hours_end", "08:00")
            
            start = time.fromisoformat(start_str)
            end = time.fromisoformat(end_str)
            
            # Handle overnight quiet hours (e.g., 22:00 - 08:00)
            if start > end:
                return now >= start or now <= end
            else:
                return start <= now <= end
        except Exception as e:
            logger.error(f"Error checking quiet hours: {e}")
            return False
    
    async def _is_duplicate(
        self,
        user_id: str,
        notification_type: NotificationType,
        product_id: str
    ) -> bool:
        """Check if similar notification was sent recently"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.DEDUP_WINDOW_HOURS)
        
        existing = await self.db.notifications.find_one({
            "user_id": user_id,
            "notification_type": notification_type.value,
            "product_id": product_id,
            "created_at": {"$gte": cutoff.isoformat()}
        })
        
        return existing is not None
    
    async def _is_in_watchlist(self, user_id: str, product_id: str) -> bool:
        """Check if product is in user's watchlist"""
        item = await self.db.watchlist.find_one({
            "user_id": user_id,
            "product_id": product_id
        })
        return item is not None
    
    def _determine_priority(
        self,
        notification_type: NotificationType,
        product: Dict[str, Any],
        is_watchlist: bool
    ) -> NotificationPriority:
        """Determine notification priority based on signals"""
        launch_score = product.get("launch_score", 0)
        
        # Watchlist items always get high priority
        if is_watchlist:
            return NotificationPriority.HIGH
        
        # Very high scores get high priority
        if launch_score >= 90:
            return NotificationPriority.HIGH
        
        # Strong launches and exploding trends get medium priority
        if notification_type in [NotificationType.STRONG_LAUNCH, NotificationType.EXPLODING_TREND]:
            return NotificationPriority.MEDIUM
        
        return NotificationPriority.LOW
    
    def _generate_notification_reason(
        self,
        notification_type: NotificationType,
        product: Dict[str, Any],
        is_watchlist: bool
    ) -> str:
        """Generate human-readable reason for notification"""
        product_name = product.get("product_name", "Unknown Product")
        launch_score = product.get("launch_score", 0)
        trend_stage = product.get("early_trend_label", product.get("trend_stage", "unknown"))
        
        reasons = []
        
        if notification_type == NotificationType.STRONG_LAUNCH:
            reasons.append(f"Launch Score reached {launch_score} - Strong Launch opportunity")
        elif notification_type == NotificationType.EXPLODING_TREND:
            reasons.append(f"Trend is now exploding with high momentum")
        elif notification_type == NotificationType.WATCHLIST_ALERT:
            reasons.append(f"Significant changes detected on your watchlist item")
        elif notification_type == NotificationType.SCORE_MILESTONE:
            reasons.append(f"Crossed your alert threshold with score {launch_score}")
        
        if is_watchlist:
            reasons.append("This product is in your watchlist")
        
        return " | ".join(reasons)
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        product: Dict[str, Any],
        channels: List[NotificationChannel] = None,
        force: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a notification for a user.
        
        Args:
            user_id: Target user ID
            notification_type: Type of notification
            product: Product data
            channels: Override channels (default: use user preferences)
            force: Skip dedup and quiet hours checks
            
        Returns:
            Created notification or None if skipped
        """
        product_id = product.get("id")
        
        # Get user preferences
        prefs = await self.get_user_preferences(user_id)
        
        # Check if notification type is enabled
        type_enabled = prefs.get("notification_types", {}).get(notification_type.value, True)
        if not type_enabled and not force:
            logger.debug(f"Notification type {notification_type.value} disabled for user {user_id}")
            return None
        
        # Check quiet hours (skip for force or high priority watchlist items)
        is_watchlist = await self._is_in_watchlist(user_id, product_id)
        if not force and not is_watchlist and self._is_quiet_hours(prefs):
            logger.debug(f"Quiet hours active for user {user_id}")
            return None
        
        # Check deduplication
        if not force and await self._is_duplicate(user_id, notification_type, product_id):
            logger.debug(f"Duplicate notification skipped for {product_id}")
            return None
        
        # Check threshold
        launch_score = product.get("launch_score", 0)
        threshold = prefs.get("alert_threshold", 80)
        if notification_type == NotificationType.STRONG_LAUNCH and launch_score < threshold:
            logger.debug(f"Product score {launch_score} below threshold {threshold}")
            return None
        
        # Determine priority
        priority = self._determine_priority(notification_type, product, is_watchlist)
        
        # Generate reason
        reason = self._generate_notification_reason(notification_type, product, is_watchlist)
        
        # Create notification document
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "notification_type": notification_type.value,
            "priority": priority.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            
            # Product data
            "product_id": product_id,
            "product_name": product.get("product_name"),
            "launch_score": launch_score,
            "launch_score_label": product.get("launch_score_label", "unknown"),
            "trend_stage": product.get("early_trend_label", product.get("trend_stage", "unknown")),
            "estimated_margin": product.get("estimated_margin", 0),
            "category": product.get("category", "Unknown"),
            
            # Notification metadata
            "title": self._get_notification_title(notification_type, product),
            "reason": reason,
            "is_watchlist": is_watchlist,
            
            # Status
            "is_read": False,
            "read_at": None,
            "email_sent": False,
            "email_sent_at": None
        }
        
        # Save to database
        await self.db.notifications.insert_one(notification)
        notification.pop("_id", None)
        
        logger.info(f"Created notification: {notification_type.value} for user {user_id}, product {product.get('product_name')}")
        
        # Send through channels
        channels_to_use = channels or []
        
        # Use preferences if no override
        if not channels:
            if prefs.get("in_app_enabled", True):
                channels_to_use.append(NotificationChannel.IN_APP)
            if prefs.get("email_enabled", True):
                channels_to_use.append(NotificationChannel.EMAIL)
        
        # Send email if enabled
        if NotificationChannel.EMAIL in channels_to_use:
            await self._send_email_notification(user_id, notification, product)
        
        return notification
    
    def _get_notification_title(
        self,
        notification_type: NotificationType,
        product: Dict[str, Any]
    ) -> str:
        """Generate notification title"""
        product_name = product.get("product_name", "Unknown")[:40]
        launch_score = product.get("launch_score", 0)
        
        titles = {
            NotificationType.STRONG_LAUNCH: f"🚀 Strong Launch: {product_name} ({launch_score})",
            NotificationType.EXPLODING_TREND: f"🔥 Exploding Trend: {product_name}",
            NotificationType.WATCHLIST_ALERT: f"📌 Watchlist Alert: {product_name}",
            NotificationType.SCORE_MILESTONE: f"📈 Score Milestone: {product_name} ({launch_score})",
            NotificationType.RADAR_DETECTED: f"📡 Radar Detected: {product_name} (Score {launch_score})"
        }
        
        return titles.get(notification_type, f"Alert: {product_name}")
    
    async def _send_email_notification(
        self,
        user_id: str,
        notification: Dict[str, Any],
        product: Dict[str, Any]
    ):
        """Send email notification"""
        try:
            # Get user email from profiles
            profile = await self.db.profiles.find_one({"id": user_id}, {"_id": 0})
            if not profile or not profile.get("email"):
                logger.warning(f"No email found for user {user_id}")
                return
            
            email = profile.get("email")
            
            # Send alert email
            result = await self.email_service.send_product_alert_email(
                to_email=email,
                notification=notification,
                product=product
            )
            
            if result.get("success"):
                await self.db.notifications.update_one(
                    {"id": notification["id"]},
                    {"$set": {
                        "email_sent": True,
                        "email_sent_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                logger.info(f"Email notification sent to {email}")
            else:
                logger.error(f"Failed to send email: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def get_notifications(
        self,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False,
        notification_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user's notifications"""
        query = {"user_id": user_id}
        
        if unread_only:
            query["is_read"] = False
        
        if notification_types:
            query["notification_type"] = {"$in": notification_types}
        
        cursor = self.db.notifications.find(
            query,
            {"_id": 0}
        ).sort([
            ("is_read", 1),  # Unread first
            ("priority", 1),  # High priority first
            ("created_at", -1)  # Most recent first
        ]).limit(limit)
        
        return await cursor.to_list(limit)
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        return await self.db.notifications.count_documents({
            "user_id": user_id,
            "is_read": False
        })
    
    async def mark_as_read(self, user_id: str, notification_ids: List[str]) -> int:
        """Mark specific notifications as read"""
        result = await self.db.notifications.update_many(
            {
                "user_id": user_id,
                "id": {"$in": notification_ids}
            },
            {"$set": {
                "is_read": True,
                "read_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return result.modified_count
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        result = await self.db.notifications.update_many(
            {"user_id": user_id, "is_read": False},
            {"$set": {
                "is_read": True,
                "read_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return result.modified_count
    
    async def delete_notification(self, user_id: str, notification_id: str) -> bool:
        """Delete a specific notification"""
        result = await self.db.notifications.delete_one({
            "user_id": user_id,
            "id": notification_id
        })
        return result.deleted_count > 0
    
    async def cleanup_old_notifications(self, days: int = 30) -> int:
        """Remove notifications older than specified days"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.notifications.delete_many({
            "created_at": {"$lt": cutoff.isoformat()}
        })
        logger.info(f"Cleaned up {result.deleted_count} old notifications")
        return result.deleted_count
    
    async def process_strong_launch_alert(
        self,
        product: Dict[str, Any],
        previous_score: int = 0
    ):
        """
        Process a product that entered Strong Launch status.
        Sends notifications to relevant users.
        """
        launch_score = product.get("launch_score", 0)
        product_id = product.get("id")
        
        # Only process if score crossed 80 threshold
        if launch_score < 80 or previous_score >= 80:
            return
        
        # Get all users with watchlist containing this product
        watchlist_users = await self.db.watchlist.find(
            {"product_id": product_id},
            {"user_id": 1}
        ).to_list(None)
        
        watchlist_user_ids = {item["user_id"] for item in watchlist_users}
        
        # Get all users with email notifications enabled and matching threshold
        cursor = self.db.notification_preferences.find({
            "notification_types.strong_launch": True,
            "alert_threshold": {"$lte": launch_score}
        }, {"user_id": 1})
        
        all_prefs = await cursor.to_list(None)
        
        # Send to watchlist users first (priority)
        for user_id in watchlist_user_ids:
            await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.STRONG_LAUNCH,
                product=product
            )
        
        # Send to other subscribed users
        for pref in all_prefs:
            user_id = pref.get("user_id")
            if user_id and user_id not in watchlist_user_ids:
                await self.create_notification(
                    user_id=user_id,
                    notification_type=NotificationType.STRONG_LAUNCH,
                    product=product
                )
    
    async def process_exploding_trend_alert(
        self,
        product: Dict[str, Any],
        previous_label: str = None
    ):
        """
        Process a product that became an exploding trend.
        Sends notifications to relevant users.
        """
        current_label = product.get("early_trend_label", "stable")
        product_id = product.get("id")
        
        # Only process if trend changed to exploding
        if current_label != "exploding" or previous_label == "exploding":
            return
        
        # Get watchlist users first
        watchlist_users = await self.db.watchlist.find(
            {"product_id": product_id},
            {"user_id": 1}
        ).to_list(None)
        
        watchlist_user_ids = {item["user_id"] for item in watchlist_users}
        
        # Get users with exploding trend notifications enabled
        cursor = self.db.notification_preferences.find({
            "notification_types.exploding_trend": True
        }, {"user_id": 1})
        
        all_prefs = await cursor.to_list(None)
        
        # Send to watchlist users first
        for user_id in watchlist_user_ids:
            await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.EXPLODING_TREND,
                product=product
            )
        
        # Send to other subscribed users
        for pref in all_prefs:
            user_id = pref.get("user_id")
            if user_id and user_id not in watchlist_user_ids:
                await self.create_notification(
                    user_id=user_id,
                    notification_type=NotificationType.EXPLODING_TREND,
                    product=product
                )


def create_notification_service(db) -> NotificationService:
    """Factory function to create service instance"""
    return NotificationService(db)
