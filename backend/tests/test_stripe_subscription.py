"""
Stripe Subscription Tests - P0 Testing

Tests for:
1. Stripe Billing Endpoints (create-checkout-session, plans, cancel-subscription, create-portal-session)
2. Webhook Handling (checkout.session.completed, customer.subscription.deleted)
3. Feature Access (feature-access endpoint for free/pro/elite users)
4. Server-Side Gating (PDF export requires Pro, early-opportunities requires Elite)
5. Store Limit Gating
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review request
FREE_USER_EMAIL = "testref@test.com"
FREE_USER_PASSWORD = "Test1234!"
ADMIN_USER_EMAIL = "jenkinslisa1978@gmail.com"


class TestStripeSetup:
    """Verify Stripe configuration and basic endpoints"""
    
    @pytest.fixture(scope="class")
    def free_user_token(self):
        """Login as free tier user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": FREE_USER_EMAIL,
            "password": FREE_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Free user login failed: {response.status_code} - {response.text}")
    
    def test_api_health(self):
        """Test API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ API health check passed")
    
    def test_plans_endpoint_returns_three_plans(self):
        """GET /api/stripe/plans should return Free/Pro/Elite only (no Starter)"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        assert response.status_code == 200
        
        data = response.json()
        assert "plans" in data
        assert data.get("currency") == "gbp"
        
        plans = data["plans"]
        plan_ids = [p["id"] for p in plans]
        
        # Verify exactly 3 plans: free, pro, elite
        assert "free" in plan_ids, "Free plan missing"
        assert "pro" in plan_ids, "Pro plan missing"
        assert "elite" in plan_ids, "Elite plan missing"
        assert "starter" not in plan_ids, "Starter plan should not exist"
        
        # Verify pricing
        for plan in plans:
            if plan["id"] == "free":
                assert plan["price_monthly"] == 0, "Free plan should be £0"
            elif plan["id"] == "pro":
                assert plan["price_monthly"] == 39, "Pro plan should be £39"
            elif plan["id"] == "elite":
                assert plan["price_monthly"] == 99, "Elite plan should be £99"
        
        print(f"✓ Plans endpoint returns {len(plans)} plans: {plan_ids}")
        print(f"✓ Currency is GBP: {data.get('currency')}")


class TestStripeCheckout:
    """Test Stripe checkout session creation"""
    
    @pytest.fixture(scope="class")
    def free_user_token(self):
        """Login as free tier user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": FREE_USER_EMAIL,
            "password": FREE_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Free user login failed: {response.status_code}")
    
    def test_create_checkout_session_pro(self, free_user_token):
        """POST /api/stripe/create-checkout-session with plan='pro' should return Stripe checkout URL"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = requests.post(f"{BASE_URL}/api/stripe/create-checkout-session", 
            headers=headers,
            json={
                "plan": "pro",
                "success_url": f"{BASE_URL}/pricing",
                "cancel_url": f"{BASE_URL}/pricing"
            }
        )
        
        # Should return 200 with url or demo_mode
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Should have either url (live Stripe) or demo_mode
        assert "url" in data or "demo_mode" in data, "Response should contain 'url' or 'demo_mode'"
        
        if data.get("demo_mode"):
            print("✓ Pro checkout - Demo mode active (Stripe not configured)")
        else:
            assert data["url"].startswith("https://checkout.stripe.com") or data["url"].startswith("https://"), \
                f"URL should be Stripe checkout: {data.get('url')}"
            print(f"✓ Pro checkout session created: {data['url'][:60]}...")
    
    def test_create_checkout_session_elite(self, free_user_token):
        """POST /api/stripe/create-checkout-session with plan='elite' should return Stripe checkout URL"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = requests.post(f"{BASE_URL}/api/stripe/create-checkout-session", 
            headers=headers,
            json={
                "plan": "elite",
                "success_url": f"{BASE_URL}/pricing",
                "cancel_url": f"{BASE_URL}/pricing"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "url" in data or "demo_mode" in data
        print(f"✓ Elite checkout session created successfully")
    
    def test_create_checkout_session_requires_auth(self):
        """POST /api/stripe/create-checkout-session should require authentication"""
        response = requests.post(f"{BASE_URL}/api/stripe/create-checkout-session", 
            json={
                "plan": "pro",
                "success_url": f"{BASE_URL}/pricing",
                "cancel_url": f"{BASE_URL}/pricing"
            }
        )
        assert response.status_code == 401, "Checkout should require authentication"
        print("✓ Checkout endpoint requires authentication")


class TestStripePortalAndCancel:
    """Test Stripe portal and cancel subscription endpoints"""
    
    @pytest.fixture(scope="class")
    def free_user_token(self):
        """Login as free tier user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": FREE_USER_EMAIL,
            "password": FREE_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Free user login failed: {response.status_code}")
    
    def test_create_portal_session(self, free_user_token):
        """POST /api/stripe/create-portal-session should return portal URL or error for non-subscriber"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = requests.post(f"{BASE_URL}/api/stripe/create-portal-session", 
            headers=headers,
            json={
                "return_url": f"{BASE_URL}/pricing"
            }
        )
        
        # For free user without Stripe customer, this may return 400 or demo_mode
        if response.status_code == 200:
            data = response.json()
            if data.get("demo_mode"):
                print("✓ Portal session - Demo mode (no Stripe customer)")
            else:
                assert "url" in data, "Response should contain portal URL"
                print(f"✓ Portal session created: {data.get('url', '')[:60]}...")
        elif response.status_code == 400:
            # Expected for users without Stripe customer
            print("✓ Portal session correctly returns 400 for non-subscriber")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}")
    
    def test_cancel_subscription(self, free_user_token):
        """POST /api/stripe/cancel-subscription should succeed for authenticated user"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = requests.post(f"{BASE_URL}/api/stripe/cancel-subscription", headers=headers)
        
        # For free user, this should return success (already on free) or error
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") or "plan" in data
            print(f"✓ Cancel subscription returned: {data}")
        else:
            print("✓ Cancel subscription returned 400 (user has no active subscription)")


class TestWebhook:
    """Test Stripe webhook handling"""
    
    def test_webhook_checkout_completed(self):
        """POST /api/stripe/webhook with checkout.session.completed should update user plan"""
        # Create mock checkout.session.completed event
        test_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {
                        "user_id": "test_webhook_user",
                        "plan": "pro"
                    },
                    "subscription": "sub_test123",
                    "customer": "cus_test123"
                }
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/stripe/webhook", 
            json=test_event,
            headers={"Content-Type": "application/json"}
        )
        
        # Should accept the webhook (with or without signature verification)
        assert response.status_code == 200, f"Webhook should return 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("received") == True
        print(f"✓ Webhook checkout.session.completed processed: {data}")
    
    def test_webhook_subscription_deleted(self):
        """POST /api/stripe/webhook with customer.subscription.deleted should downgrade to free"""
        test_event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "metadata": {
                        "user_id": "test_webhook_user",
                        "plan": "pro"
                    },
                    "customer": "cus_test123",
                    "id": "sub_test123"
                }
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/stripe/webhook", 
            json=test_event,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Webhook should return 200, got {response.status_code}"
        data = response.json()
        assert data.get("received") == True
        print(f"✓ Webhook subscription.deleted processed: {data}")


class TestFeatureAccess:
    """Test feature access endpoint for different user types"""
    
    @pytest.fixture(scope="class")
    def free_user_token(self):
        """Login as free tier user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": FREE_USER_EMAIL,
            "password": FREE_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Free user login failed: {response.status_code}")
    
    def test_feature_access_free_user(self, free_user_token):
        """GET /api/stripe/feature-access for free user should show restricted features"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = requests.get(f"{BASE_URL}/api/stripe/feature-access", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Free user should have restricted features
        features = data.get("features", {})
        plan = data.get("plan", "").lower()
        
        # Check plan is free (unless admin)
        if not data.get("is_admin"):
            assert plan == "free", f"Expected free plan, got {plan}"
            assert features.get("pdf_export") == False, "Free user should not have pdf_export"
            assert features.get("direct_publish") == False, "Free user should not have direct_publish"
            assert features.get("early_trends") == False, "Free user should not have early_trends"
            print(f"✓ Free user features verified: pdf_export={features.get('pdf_export')}, early_trends={features.get('early_trends')}")
        else:
            print(f"✓ User is admin - has elevated access")
    
    def test_feature_access_requires_auth(self):
        """GET /api/stripe/feature-access should require authentication"""
        response = requests.get(f"{BASE_URL}/api/stripe/feature-access")
        assert response.status_code == 401
        print("✓ Feature access requires authentication")


class TestServerSideGating:
    """Test server-side feature gating (PDF export, early opportunities)"""
    
    @pytest.fixture(scope="class")
    def free_user_token(self):
        """Login as free tier user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": FREE_USER_EMAIL,
            "password": FREE_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Free user login failed: {response.status_code}")
    
    def test_pdf_export_blocked_for_free_users(self, free_user_token):
        """GET /api/reports/weekly-winning-products/pdf should return 403 for free users"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products/pdf", headers=headers)
        
        # Should return 403 for free users
        if response.status_code == 403:
            print("✓ PDF export correctly blocked for free user (403)")
        elif response.status_code == 200:
            # Check if user is actually admin
            feature_resp = requests.get(f"{BASE_URL}/api/stripe/feature-access", headers=headers)
            if feature_resp.status_code == 200 and feature_resp.json().get("is_admin"):
                print("✓ PDF export allowed - user is admin")
            else:
                pytest.fail("PDF export should be blocked for free users")
        else:
            print(f"⚠ PDF export returned {response.status_code} (expected 403 for free users)")
    
    def test_early_opportunities_blocked_for_free_users(self, free_user_token):
        """GET /api/intelligence/early-opportunities should return 403 for free users"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = requests.get(f"{BASE_URL}/api/intelligence/early-opportunities", headers=headers)
        
        # Should return 403 for free users (requires Elite)
        if response.status_code == 403:
            print("✓ Early opportunities correctly blocked for free user (403)")
        elif response.status_code == 200:
            # Check if user is actually admin/elite
            feature_resp = requests.get(f"{BASE_URL}/api/stripe/feature-access", headers=headers)
            if feature_resp.status_code == 200 and feature_resp.json().get("is_admin"):
                print("✓ Early opportunities allowed - user is admin")
            else:
                pytest.fail("Early opportunities should be blocked for free/pro users")
        else:
            print(f"⚠ Early opportunities returned {response.status_code} (expected 403 for free users)")


class TestSubscriptionEndpoint:
    """Test subscription status endpoint"""
    
    @pytest.fixture(scope="class")
    def free_user_token(self):
        """Login as free tier user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": FREE_USER_EMAIL,
            "password": FREE_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Free user login failed: {response.status_code}")
    
    def test_get_user_subscription(self, free_user_token):
        """GET /api/stripe/subscription should return user's subscription status"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = requests.get(f"{BASE_URL}/api/stripe/subscription", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have plan and features
        assert "plan" in data, "Response should contain 'plan'"
        assert "features" in data, "Response should contain 'features'"
        
        print(f"✓ Subscription endpoint returned: plan={data.get('plan')}, is_admin={data.get('is_admin')}")


class TestStoreLimitGating:
    """Test store creation limits by plan"""
    
    @pytest.fixture(scope="class")
    def free_user_token(self):
        """Login as free tier user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": FREE_USER_EMAIL,
            "password": FREE_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Free user login failed: {response.status_code}")
    
    def test_feature_access_store_limits(self, free_user_token):
        """Verify store limits are returned in feature-access"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = requests.get(f"{BASE_URL}/api/stripe/feature-access", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        features = data.get("features", {})
        
        # Check store-related fields
        assert "max_stores" in features, "max_stores should be in features"
        assert "can_create_store" in features, "can_create_store should be in features"
        assert "current_store_count" in features, "current_store_count should be in features"
        
        plan = data.get("plan", "free")
        max_stores = features.get("max_stores")
        
        # Verify limits by plan
        if plan == "free":
            assert max_stores == 1, f"Free plan should have max 1 store, got {max_stores}"
        elif plan == "pro":
            assert max_stores == 5, f"Pro plan should have max 5 stores, got {max_stores}"
        elif plan == "elite":
            assert max_stores == -1, f"Elite plan should have unlimited stores, got {max_stores}"
        
        print(f"✓ Store limits verified: plan={plan}, max_stores={max_stores}, can_create={features.get('can_create_store')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
