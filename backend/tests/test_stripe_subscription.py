"""
Test Stripe Subscription & Pricing Plans API Endpoints

Tests for:
- GET /api/stripe/plans - Returns all 3 plans with GBP pricing
- GET /api/stripe/subscription - Returns user subscription status (requires auth)
- GET /api/stripe/feature-access - Returns feature access (requires auth)
- POST /api/stripe/create-checkout-session - Creates Stripe checkout (requires auth)
- POST /api/stripe/create-portal-session - Creates billing portal (requires auth)
- POST /api/stripe/webhook - Handles subscription events
- POST /api/stripe/cancel-subscription - Cancels subscription (requires auth)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestStripePlansPublicEndpoint:
    """Tests for GET /api/stripe/plans - public endpoint"""
    
    def test_get_plans_returns_200(self):
        """Test plans endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        print(f"GET /api/stripe/plans - Status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_get_plans_returns_three_plans(self):
        """Test that 3 plans are returned (free, pro, elite)"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        assert "plans" in data, "Response should have 'plans' key"
        plans = data["plans"]
        assert len(plans) == 3, f"Expected 3 plans, got {len(plans)}"
        
        plan_ids = [p["id"] for p in plans]
        print(f"Plan IDs: {plan_ids}")
        assert "free" in plan_ids, "Free plan should exist"
        assert "pro" in plan_ids, "Pro plan should exist"
        assert "elite" in plan_ids, "Elite plan should exist"
    
    def test_plans_have_gbp_pricing(self):
        """Test plans use GBP currency"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        assert data.get("currency") == "gbp", f"Currency should be gbp, got {data.get('currency')}"
        assert data.get("currency_symbol") == "£", f"Currency symbol should be £"
        
        for plan in data["plans"]:
            assert plan.get("currency") == "gbp", f"Plan {plan.get('id')} should use gbp"
    
    def test_free_plan_is_zero(self):
        """Test free plan has £0 pricing"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        free_plan = next((p for p in data["plans"] if p["id"] == "free"), None)
        assert free_plan is not None, "Free plan not found"
        assert free_plan["price_monthly"] == 0, f"Free plan should be £0, got £{free_plan['price_monthly']}"
        print(f"Free plan price: £{free_plan['price_monthly']}/month")
    
    def test_pro_plan_is_39(self):
        """Test pro plan has £39 pricing"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        pro_plan = next((p for p in data["plans"] if p["id"] == "pro"), None)
        assert pro_plan is not None, "Pro plan not found"
        assert pro_plan["price_monthly"] == 39, f"Pro plan should be £39, got £{pro_plan['price_monthly']}"
        print(f"Pro plan price: £{pro_plan['price_monthly']}/month")
    
    def test_elite_plan_is_99(self):
        """Test elite plan has £99 pricing"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        elite_plan = next((p for p in data["plans"] if p["id"] == "elite"), None)
        assert elite_plan is not None, "Elite plan not found"
        assert elite_plan["price_monthly"] == 99, f"Elite plan should be £99, got £{elite_plan['price_monthly']}"
        print(f"Elite plan price: £{elite_plan['price_monthly']}/month")
    
    def test_plans_have_features(self):
        """Test all plans have features object"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        for plan in data["plans"]:
            assert "features" in plan, f"Plan {plan['id']} should have features"
            assert "feature_descriptions" in plan, f"Plan {plan['id']} should have feature_descriptions"
            print(f"{plan['name']} plan features: {list(plan['features'].keys())}")
    
    def test_elite_has_all_features_enabled(self):
        """Test elite plan has all premium features enabled"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        elite_plan = next((p for p in data["plans"] if p["id"] == "elite"), None)
        features = elite_plan["features"]
        
        assert features.get("early_trend_access") == True, "Elite should have early_trend_access"
        assert features.get("automation_insights") == True, "Elite should have automation_insights"
        assert features.get("advanced_opportunities") == True, "Elite should have advanced_opportunities"
        assert features.get("max_stores") == -1, "Elite should have unlimited stores (-1)"
        print(f"Elite features verified: {features}")


class TestStripeAuthenticatedEndpoints:
    """Tests for authenticated Stripe endpoints - expect 401/422 without auth"""
    
    def test_subscription_requires_auth(self):
        """Test subscription endpoint returns 401/422 without auth"""
        response = requests.get(f"{BASE_URL}/api/stripe/subscription")
        print(f"GET /api/stripe/subscription (no auth) - Status: {response.status_code}")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
    
    def test_feature_access_requires_auth(self):
        """Test feature-access endpoint returns 401/422 without auth"""
        response = requests.get(f"{BASE_URL}/api/stripe/feature-access")
        print(f"GET /api/stripe/feature-access (no auth) - Status: {response.status_code}")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
    
    def test_create_checkout_requires_auth(self):
        """Test create-checkout-session endpoint requires auth"""
        response = requests.post(f"{BASE_URL}/api/stripe/create-checkout-session", json={
            "plan": "pro",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        })
        print(f"POST /api/stripe/create-checkout-session (no auth) - Status: {response.status_code}")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
    
    def test_create_portal_requires_auth(self):
        """Test create-portal-session endpoint requires auth"""
        response = requests.post(f"{BASE_URL}/api/stripe/create-portal-session", json={
            "return_url": "https://example.com/pricing"
        })
        print(f"POST /api/stripe/create-portal-session (no auth) - Status: {response.status_code}")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
    
    def test_cancel_subscription_requires_auth(self):
        """Test cancel-subscription endpoint requires auth"""
        response = requests.post(f"{BASE_URL}/api/stripe/cancel-subscription")
        print(f"POST /api/stripe/cancel-subscription (no auth) - Status: {response.status_code}")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"


class TestStripeWebhookEndpoint:
    """Tests for webhook endpoint - public but requires proper payload"""
    
    def test_webhook_accepts_post(self):
        """Test webhook endpoint accepts POST requests"""
        # Webhook requires specific format but shouldn't crash
        response = requests.post(
            f"{BASE_URL}/api/stripe/webhook",
            json={"type": "test", "data": {"object": {}}},
            headers={"Content-Type": "application/json"}
        )
        print(f"POST /api/stripe/webhook - Status: {response.status_code}")
        # Could be 200 (demo mode) or 400 (invalid event)
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}"
    
    def test_webhook_handles_checkout_completed_event(self):
        """Test webhook handles checkout.session.completed event format"""
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "metadata": {
                        "user_id": "test_user_123",
                        "plan": "pro"
                    },
                    "subscription": "sub_test_123",
                    "customer": "cus_test_123"
                }
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/stripe/webhook",
            json=event,
            headers={"Content-Type": "application/json"}
        )
        print(f"Webhook checkout.session.completed - Status: {response.status_code}")
        # Should process without error or return demo mode
        if response.status_code == 200:
            data = response.json()
            print(f"Webhook response: {data}")


class TestPlanFeatureMapping:
    """Tests for verifying plan-to-feature mapping is correct"""
    
    def test_free_plan_has_correct_limits(self):
        """Test free plan has proper feature limitations"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        free_plan = next((p for p in data["plans"] if p["id"] == "free"), None)
        features = free_plan["features"]
        
        # Free should have limited access
        assert features.get("reports_access") == "preview", "Free should have preview reports only"
        assert features.get("max_stores") == 1, "Free should have 1 store limit"
        assert features.get("early_trend_access") == False, "Free should not have early trend access"
        print(f"Free plan limits verified: max_stores={features.get('max_stores')}")
    
    def test_pro_plan_has_correct_limits(self):
        """Test pro plan has proper features"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        pro_plan = next((p for p in data["plans"] if p["id"] == "pro"), None)
        features = pro_plan["features"]
        
        # Pro should have full basic access but not elite features
        assert features.get("reports_access") == "full", "Pro should have full reports"
        assert features.get("max_stores") == 5, "Pro should have 5 stores"
        assert features.get("early_trend_access") == False, "Pro should not have early trend access"
        print(f"Pro plan features verified: max_stores={features.get('max_stores')}")
    
    def test_elite_unlocks_all_features(self):
        """Test elite plan unlocks all premium features"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        elite_plan = next((p for p in data["plans"] if p["id"] == "elite"), None)
        features = elite_plan["features"]
        
        # Elite should have everything
        assert features.get("reports_access") == "full", "Elite should have full reports"
        assert features.get("product_insights") == "full", "Elite should have full insights"
        assert features.get("max_stores") == -1, "Elite should have unlimited stores"
        assert features.get("early_trend_access") == True, "Elite should have early trend access"
        assert features.get("automation_insights") == True, "Elite should have automation insights"
        assert features.get("advanced_opportunities") == True, "Elite should have advanced opportunities"
        print(f"Elite plan full access verified")


class TestSubscriptionServiceIntegration:
    """Integration tests for subscription service features"""
    
    def test_plans_endpoint_includes_all_required_fields(self):
        """Test plans response has all required fields"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        required_plan_fields = ["id", "name", "price_monthly", "currency", "features", "feature_descriptions"]
        
        for plan in data["plans"]:
            for field in required_plan_fields:
                assert field in plan, f"Plan {plan.get('id')} missing required field: {field}"
        
        print(f"All {len(data['plans'])} plans have required fields")
    
    def test_response_format_consistency(self):
        """Test API response format is consistent"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        
        # Top-level structure
        assert "plans" in data, "Response needs 'plans' key"
        assert "currency" in data, "Response needs 'currency' key"
        assert "currency_symbol" in data, "Response needs 'currency_symbol' key"
        
        # Plans should be a list
        assert isinstance(data["plans"], list), "Plans should be a list"
        
        print("Response format validated successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
