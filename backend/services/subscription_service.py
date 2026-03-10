"""
Subscription Service

Manages subscription plans, Stripe integration, and feature gating.
All prices in GBP (British Pounds).
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)

# Try to import stripe
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("Stripe not installed. Running in demo mode.")


class SubscriptionPlan(str, Enum):
    """Available subscription plans"""
    FREE = "free"
    PRO = "pro"
    ELITE = "elite"


class SubscriptionStatus(str, Enum):
    """Subscription status values"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"


# Plan configuration with GBP pricing
PLANS = {
    SubscriptionPlan.FREE: {
        "name": "Free",
        "price_monthly": 0,
        "currency": "gbp",
        "stripe_price_id": None,  # No Stripe for free tier
        "features": {
            "product_insights": "limited",
            "reports_access": "preview",
            "max_stores": 1,
            "watchlist_access": "limited",
            "alerts_access": "limited",
            "early_trend_access": False,
            "automation_insights": False,
            "advanced_opportunities": False,
        },
        "feature_descriptions": [
            "Limited product insights",
            "Report previews only",
            "1 store",
            "Limited watchlist access",
            "Limited alerts"
        ]
    },
    SubscriptionPlan.PRO: {
        "name": "Pro",
        "price_monthly": 39,
        "currency": "gbp",
        "stripe_price_id": os.environ.get("STRIPE_PRO_PRICE_ID"),
        "features": {
            "product_insights": "full",
            "reports_access": "full",
            "max_stores": 5,
            "watchlist_access": "full",
            "alerts_access": "full",
            "early_trend_access": False,
            "automation_insights": False,
            "advanced_opportunities": False,
        },
        "feature_descriptions": [
            "Full product insights",
            "Complete reports access",
            "Up to 5 stores",
            "Full watchlist access",
            "Full alerts access"
        ]
    },
    SubscriptionPlan.ELITE: {
        "name": "Elite",
        "price_monthly": 99,
        "currency": "gbp",
        "stripe_price_id": os.environ.get("STRIPE_ELITE_PRICE_ID"),
        "features": {
            "product_insights": "full",
            "reports_access": "full",
            "max_stores": -1,  # Unlimited
            "watchlist_access": "full",
            "alerts_access": "full",
            "early_trend_access": True,
            "automation_insights": True,
            "advanced_opportunities": True,
        },
        "feature_descriptions": [
            "Everything in Pro",
            "Early trend detection",
            "Advanced opportunity insights",
            "Automation insights",
            "Unlimited stores"
        ]
    }
}


class FeatureGate:
    """Utility class for checking feature access by plan"""
    
    @staticmethod
    def get_plan_features(plan: str) -> Dict[str, Any]:
        """Get features for a plan"""
        try:
            plan_enum = SubscriptionPlan(plan.lower())
            return PLANS.get(plan_enum, PLANS[SubscriptionPlan.FREE])["features"]
        except (ValueError, KeyError):
            return PLANS[SubscriptionPlan.FREE]["features"]
    
    @staticmethod
    def can_access_full_reports(plan: str) -> bool:
        """Check if user can access full reports"""
        features = FeatureGate.get_plan_features(plan)
        return features.get("reports_access") == "full"
    
    @staticmethod
    def can_access_full_insights(plan: str) -> bool:
        """Check if user can access full product insights"""
        features = FeatureGate.get_plan_features(plan)
        return features.get("product_insights") == "full"
    
    @staticmethod
    def can_access_watchlist(plan: str) -> bool:
        """Check if user has full watchlist access"""
        features = FeatureGate.get_plan_features(plan)
        return features.get("watchlist_access") == "full"
    
    @staticmethod
    def can_access_alerts(plan: str) -> bool:
        """Check if user has full alerts access"""
        features = FeatureGate.get_plan_features(plan)
        return features.get("alerts_access") == "full"
    
    @staticmethod
    def can_access_early_trends(plan: str) -> bool:
        """Check if user can access early trend features"""
        features = FeatureGate.get_plan_features(plan)
        return features.get("early_trend_access", False)
    
    @staticmethod
    def can_access_automation_insights(plan: str) -> bool:
        """Check if user can access automation insights"""
        features = FeatureGate.get_plan_features(plan)
        return features.get("automation_insights", False)
    
    @staticmethod
    def can_access_advanced_opportunities(plan: str) -> bool:
        """Check if user can access advanced opportunity features"""
        features = FeatureGate.get_plan_features(plan)
        return features.get("advanced_opportunities", False)
    
    @staticmethod
    def get_max_stores(plan: str) -> int:
        """Get maximum stores allowed for plan (-1 = unlimited)"""
        features = FeatureGate.get_plan_features(plan)
        return features.get("max_stores", 1)
    
    @staticmethod
    def can_create_store(plan: str, current_store_count: int) -> bool:
        """Check if user can create another store"""
        max_stores = FeatureGate.get_max_stores(plan)
        if max_stores == -1:  # Unlimited
            return True
        return current_store_count < max_stores


class SubscriptionService:
    """
    Manages subscriptions with Stripe integration.
    
    Free tier is app-managed.
    Pro and Elite are Stripe-managed subscriptions.
    """
    
    def __init__(self, db):
        self.db = db
        self._stripe_configured = False
        self._configure_stripe()
    
    def _configure_stripe(self):
        """Configure Stripe with API key"""
        if not STRIPE_AVAILABLE:
            logger.warning("Stripe package not available")
            return
        
        stripe_key = os.environ.get("STRIPE_SECRET_KEY")
        if stripe_key:
            stripe.api_key = stripe_key
            self._stripe_configured = True
            logger.info("Stripe configured successfully")
        else:
            logger.warning("STRIPE_SECRET_KEY not set")
    
    @property
    def is_stripe_configured(self) -> bool:
        return self._stripe_configured and STRIPE_AVAILABLE
    
    async def get_user_subscription(self, user_id: str) -> Dict[str, Any]:
        """Get user's current subscription status"""
        profile = await self.db.profiles.find_one(
            {"id": user_id},
            {"_id": 0}
        )
        
        if not profile:
            return {
                "plan": "free",
                "status": "active",
                "features": PLANS[SubscriptionPlan.FREE]["features"]
            }
        
        plan = profile.get("plan", "free").lower()
        status = profile.get("subscription_status", "active")
        
        # Get plan features
        try:
            plan_enum = SubscriptionPlan(plan)
            features = PLANS[plan_enum]["features"]
        except (ValueError, KeyError):
            features = PLANS[SubscriptionPlan.FREE]["features"]
        
        return {
            "plan": plan,
            "status": status,
            "stripe_customer_id": profile.get("stripe_customer_id"),
            "stripe_subscription_id": profile.get("stripe_subscription_id"),
            "current_period_end": profile.get("subscription_period_end"),
            "features": features
        }
    
    async def create_checkout_session(
        self,
        user_id: str,
        user_email: str,
        plan: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """Create Stripe checkout session for subscription"""
        
        if not self.is_stripe_configured:
            # Demo mode - return mock session
            return {
                "success": True,
                "demo_mode": True,
                "url": success_url,
                "session_id": f"cs_demo_{user_id}_{plan}",
                "message": "Stripe not configured. Demo mode active."
            }
        
        try:
            plan_enum = SubscriptionPlan(plan.lower())
        except ValueError:
            return {"success": False, "error": f"Invalid plan: {plan}"}
        
        if plan_enum == SubscriptionPlan.FREE:
            return {"success": False, "error": "Cannot checkout for free plan"}
        
        plan_config = PLANS[plan_enum]
        
        # Get or create Stripe customer
        profile = await self.db.profiles.find_one({"id": user_id}, {"_id": 0})
        stripe_customer_id = profile.get("stripe_customer_id") if profile else None
        
        try:
            if not stripe_customer_id:
                # Create new Stripe customer
                customer = stripe.Customer.create(
                    email=user_email,
                    metadata={"user_id": user_id}
                )
                stripe_customer_id = customer.id
                
                # Save customer ID to profile
                await self.db.profiles.update_one(
                    {"id": user_id},
                    {"$set": {"stripe_customer_id": stripe_customer_id}},
                    upsert=True
                )
            
            # Create checkout session
            # Note: We need to create prices in Stripe Dashboard first
            # For now, use price_data for dynamic pricing
            session = stripe.checkout.Session.create(
                customer=stripe_customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {
                            "name": f"ViralScout {plan_config['name']} Plan",
                            "description": ", ".join(plan_config["feature_descriptions"][:3])
                        },
                        "unit_amount": plan_config["price_monthly"] * 100,  # Convert to pence
                        "recurring": {"interval": "month"}
                    },
                    "quantity": 1
                }],
                mode="subscription",
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
                metadata={
                    "user_id": user_id,
                    "plan": plan
                },
                subscription_data={
                    "metadata": {
                        "user_id": user_id,
                        "plan": plan
                    }
                }
            )
            
            return {
                "success": True,
                "url": session.url,
                "session_id": session.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_portal_session(
        self,
        user_id: str,
        return_url: str
    ) -> Dict[str, Any]:
        """Create Stripe customer portal session for billing management"""
        
        if not self.is_stripe_configured:
            return {
                "success": False,
                "demo_mode": True,
                "error": "Stripe not configured. Demo mode active."
            }
        
        profile = await self.db.profiles.find_one({"id": user_id}, {"_id": 0})
        stripe_customer_id = profile.get("stripe_customer_id") if profile else None
        
        if not stripe_customer_id:
            return {"success": False, "error": "No Stripe customer found. Please subscribe first."}
        
        try:
            session = stripe.billing_portal.Session.create(
                customer=stripe_customer_id,
                return_url=return_url
            )
            
            return {
                "success": True,
                "url": session.url
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating portal: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        
        logger.info(f"Processing Stripe webhook: {event_type}")
        
        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return await handler(data)
        
        return {"status": "ignored", "event_type": event_type}
    
    async def _handle_checkout_completed(self, session: Dict) -> Dict:
        """Handle successful checkout"""
        user_id = session.get("metadata", {}).get("user_id")
        plan = session.get("metadata", {}).get("plan", "pro")
        subscription_id = session.get("subscription")
        customer_id = session.get("customer")
        
        if not user_id:
            logger.warning("Checkout completed without user_id in metadata")
            return {"status": "error", "message": "Missing user_id"}
        
        # Update user profile
        await self.db.profiles.update_one(
            {"id": user_id},
            {"$set": {
                "plan": plan,
                "subscription_status": "active",
                "stripe_customer_id": customer_id,
                "stripe_subscription_id": subscription_id,
                "subscription_updated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        logger.info(f"User {user_id} upgraded to {plan} plan")
        return {"status": "success", "user_id": user_id, "plan": plan}
    
    async def _handle_subscription_created(self, subscription: Dict) -> Dict:
        """Handle new subscription"""
        return await self._update_subscription_status(subscription)
    
    async def _handle_subscription_updated(self, subscription: Dict) -> Dict:
        """Handle subscription update"""
        return await self._update_subscription_status(subscription)
    
    async def _handle_subscription_deleted(self, subscription: Dict) -> Dict:
        """Handle subscription cancellation"""
        user_id = subscription.get("metadata", {}).get("user_id")
        
        if not user_id:
            # Try to find user by customer ID
            customer_id = subscription.get("customer")
            profile = await self.db.profiles.find_one(
                {"stripe_customer_id": customer_id},
                {"_id": 0}
            )
            user_id = profile.get("id") if profile else None
        
        if user_id:
            await self.db.profiles.update_one(
                {"id": user_id},
                {"$set": {
                    "plan": "free",
                    "subscription_status": "canceled",
                    "subscription_updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            logger.info(f"User {user_id} subscription canceled, downgraded to free")
            return {"status": "success", "user_id": user_id, "plan": "free"}
        
        return {"status": "error", "message": "User not found"}
    
    async def _update_subscription_status(self, subscription: Dict) -> Dict:
        """Update subscription status from Stripe subscription object"""
        user_id = subscription.get("metadata", {}).get("user_id")
        plan = subscription.get("metadata", {}).get("plan", "pro")
        status = subscription.get("status")
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        current_period_end = subscription.get("current_period_end")
        
        if not user_id:
            # Try to find user by customer ID
            profile = await self.db.profiles.find_one(
                {"stripe_customer_id": customer_id},
                {"_id": 0}
            )
            user_id = profile.get("id") if profile else None
        
        if user_id:
            update_data = {
                "subscription_status": status,
                "stripe_subscription_id": subscription_id,
                "subscription_updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if current_period_end:
                update_data["subscription_period_end"] = datetime.fromtimestamp(
                    current_period_end, tz=timezone.utc
                ).isoformat()
            
            # Only update plan if subscription is active
            if status == "active":
                update_data["plan"] = plan
            elif status in ["canceled", "unpaid"]:
                update_data["plan"] = "free"
            
            await self.db.profiles.update_one(
                {"id": user_id},
                {"$set": update_data}
            )
            
            logger.info(f"Updated subscription for user {user_id}: status={status}, plan={plan}")
            return {"status": "success", "user_id": user_id}
        
        return {"status": "error", "message": "User not found"}
    
    async def _handle_payment_succeeded(self, invoice: Dict) -> Dict:
        """Handle successful payment"""
        customer_id = invoice.get("customer")
        
        profile = await self.db.profiles.find_one(
            {"stripe_customer_id": customer_id},
            {"_id": 0}
        )
        
        if profile:
            await self.db.profiles.update_one(
                {"id": profile["id"]},
                {"$set": {
                    "subscription_status": "active",
                    "last_payment_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            return {"status": "success", "user_id": profile["id"]}
        
        return {"status": "ignored", "message": "Customer not found"}
    
    async def _handle_payment_failed(self, invoice: Dict) -> Dict:
        """Handle failed payment"""
        customer_id = invoice.get("customer")
        
        profile = await self.db.profiles.find_one(
            {"stripe_customer_id": customer_id},
            {"_id": 0}
        )
        
        if profile:
            await self.db.profiles.update_one(
                {"id": profile["id"]},
                {"$set": {
                    "subscription_status": "past_due",
                    "payment_failed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            logger.warning(f"Payment failed for user {profile['id']}")
            return {"status": "success", "user_id": profile["id"]}
        
        return {"status": "ignored", "message": "Customer not found"}
    
    async def downgrade_to_free(self, user_id: str) -> Dict[str, Any]:
        """Downgrade user to free plan (cancel subscription)"""
        
        profile = await self.db.profiles.find_one({"id": user_id}, {"_id": 0})
        
        if not profile:
            return {"success": False, "error": "User not found"}
        
        subscription_id = profile.get("stripe_subscription_id")
        
        if subscription_id and self.is_stripe_configured:
            try:
                # Cancel the subscription at period end
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                
                await self.db.profiles.update_one(
                    {"id": user_id},
                    {"$set": {
                        "subscription_status": "canceled",
                        "subscription_updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                return {"success": True, "message": "Subscription will be canceled at period end"}
                
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error canceling subscription: {e}")
                return {"success": False, "error": str(e)}
        
        # No active subscription, just update plan
        await self.db.profiles.update_one(
            {"id": user_id},
            {"$set": {
                "plan": "free",
                "subscription_status": "active"
            }}
        )
        
        return {"success": True, "plan": "free"}


def create_subscription_service(db) -> SubscriptionService:
    """Factory function"""
    return SubscriptionService(db)


def get_all_plans() -> List[Dict[str, Any]]:
    """Get all available plans with details"""
    return [
        {
            "id": plan.value,
            "name": config["name"],
            "price_monthly": config["price_monthly"],
            "currency": config["currency"],
            "features": config["features"],
            "feature_descriptions": config["feature_descriptions"]
        }
        for plan, config in PLANS.items()
    ]
