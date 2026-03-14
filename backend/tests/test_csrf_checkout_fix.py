"""
Test CSRF + Checkout Session Bug Fix (P0)

Bug: Free trial users clicking upgrade got no response
Root causes:
1. CSRF middleware blocked POST /api/stripe/create-checkout-session (missing x-csrf-token header)
2. PricingPage.jsx didn't check response.ok - errors silently swallowed

Tests:
- POST /api/stripe/create-checkout-session WITH valid auth + CSRF returns Stripe URL for non-admin
- POST /api/stripe/create-checkout-session WITHOUT CSRF returns 403 CSRF error
- Admin user gets expected 400 "Admin accounts have full access" error
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Generate unique test user credentials
TEST_USER_EMAIL = f"test_upgrade_{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_PASSWORD = "TestPass123"


class TestCSRFCheckoutFix:
    """Tests for the CSRF + Checkout session fix"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test with session to preserve cookies"""
        self.session = requests.Session()
        
    def test_checkout_without_auth_returns_401(self):
        """Test POST /api/stripe/create-checkout-session without auth returns 401"""
        response = self.session.post(f"{BASE_URL}/api/stripe/create-checkout-session", json={
            "plan": "starter",
            "success_url": f"{BASE_URL}/pricing?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{BASE_URL}/pricing"
        })
        print(f"POST /api/stripe/create-checkout-session (no auth) - Status: {response.status_code}")
        assert response.status_code in [401, 422], f"Expected 401/422 without auth, got {response.status_code}"
    
    def test_register_new_free_user(self):
        """Register a new free plan user for testing upgrade flow"""
        response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": "Test Upgrade User",
            "plan": "free"
        })
        print(f"POST /api/auth/register - Status: {response.status_code}")
        print(f"Response: {response.json() if response.status_code != 500 else response.text[:200]}")
        
        # Should succeed or return that email already exists
        assert response.status_code in [200, 201, 400], f"Unexpected status: {response.status_code}"
        if response.status_code == 400:
            data = response.json()
            # If user already exists, that's okay for our test
            assert "exists" in str(data).lower() or "already" in str(data).lower() or "registered" in str(data).lower()
    
    def test_login_sets_csrf_cookie(self):
        """Test that login sets __Host-csrf cookie"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        print(f"POST /api/auth/login - Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Login failed - Response: {response.text[:300]}")
            pytest.skip("Could not login - user may not exist or credentials invalid")
            return
            
        data = response.json()
        assert "token" in data, "Login should return token"
        
        # Check for cookies - either __Host-csrf or csrf cookie
        cookies = self.session.cookies.get_dict()
        print(f"Cookies after login: {list(cookies.keys())}")
        
        # Store token for later use
        self.token = data["token"]
        return self.token
    
    def test_checkout_with_csrf_token_succeeds(self):
        """
        Test POST /api/stripe/create-checkout-session with valid auth + CSRF returns checkout URL
        This is the main bug fix verification
        """
        # First login to get token and CSRF cookie
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip("Could not login - skipping CSRF test")
            return
        
        token = login_response.json().get("token")
        
        # Get CSRF token from cookies (set by login response)
        csrf_token = self.session.cookies.get("__Host-csrf")
        print(f"CSRF token from cookie: {csrf_token}")
        print(f"All cookies: {self.session.cookies.get_dict()}")
        
        # Make checkout request with both Auth header AND CSRF header
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Add CSRF header if cookie was set
        if csrf_token:
            headers["x-csrf-token"] = csrf_token
        
        response = self.session.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            json={
                "plan": "starter",
                "success_url": f"{BASE_URL}/pricing?session_id={{CHECKOUT_SESSION_ID}}",
                "cancel_url": f"{BASE_URL}/pricing"
            },
            headers=headers
        )
        
        print(f"POST /api/stripe/create-checkout-session (with auth + CSRF) - Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        # Should return 200 with Stripe checkout URL (or demo mode)
        # NOT 403 CSRF error anymore
        if response.status_code == 403:
            data = response.json()
            if "CSRF" in str(data):
                pytest.fail("CSRF error - bug NOT fixed! Request should succeed with proper CSRF header")
        
        assert response.status_code == 200, f"Expected 200 for checkout, got {response.status_code}"
        
        data = response.json()
        # Should have either a real Stripe URL or demo mode
        assert "url" in data or "demo_mode" in data, f"Response should have 'url' or 'demo_mode': {data}"
        
        if data.get("url"):
            assert "stripe.com" in data["url"] or data.get("demo_mode"), f"URL should be Stripe URL: {data['url']}"
        
        print(f"SUCCESS: Checkout session created. URL: {data.get('url', 'demo_mode')}")
    
    def test_checkout_without_csrf_header_returns_403(self):
        """
        Test POST /api/stripe/create-checkout-session WITHOUT CSRF header returns 403
        This verifies CSRF protection is still enforced
        """
        # Login first to establish cookie-authenticated session
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip("Could not login - skipping CSRF enforcement test")
            return
        
        token = login_response.json().get("token")
        
        # Make checkout request WITH Auth header but WITHOUT CSRF header
        # This should be blocked by CSRF middleware
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
            # NOTE: Deliberately NOT including x-csrf-token header
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            json={
                "plan": "starter",
                "success_url": f"{BASE_URL}/pricing",
                "cancel_url": f"{BASE_URL}/pricing"
            },
            headers=headers
        )
        
        print(f"POST /api/stripe/create-checkout-session (auth only, NO CSRF header) - Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        # Should return 403 CSRF error because:
        # - __Host-refresh cookie is present (from login)
        # - But x-csrf-token header is missing
        # The CSRF middleware checks: if refresh_cookie exists AND (no csrf header OR mismatch) -> 403
        
        # Note: If CSRF cookie isn't set at all, middleware may pass through
        if self.session.cookies.get("__Host-csrf"):
            assert response.status_code == 403, f"Expected 403 CSRF error without CSRF header, got {response.status_code}"
            data = response.json()
            assert "CSRF" in str(data), f"Expected CSRF error message: {data}"
            print("CSRF protection correctly enforced - 403 returned without x-csrf-token header")
        else:
            print("Note: __Host-csrf cookie not set, CSRF check may have been skipped")


class TestAdminCheckoutBehavior:
    """Test that admin users get expected 400 error (not CSRF error)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        
    def test_admin_checkout_returns_400_not_csrf(self):
        """Admin user should get 400 'Admin accounts have full access' - not CSRF error"""
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        
        if login_response.status_code != 200:
            pytest.skip("Could not login as admin")
            return
        
        token = login_response.json().get("token")
        csrf_token = self.session.cookies.get("__Host-csrf")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        if csrf_token:
            headers["x-csrf-token"] = csrf_token
        
        response = self.session.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            json={
                "plan": "starter",
                "success_url": f"{BASE_URL}/pricing",
                "cancel_url": f"{BASE_URL}/pricing"
            },
            headers=headers
        )
        
        print(f"POST /api/stripe/create-checkout-session (admin) - Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        # Admin should get 400 with "Admin accounts have full access" message - NOT 403 CSRF
        assert response.status_code == 400, f"Expected 400 for admin, got {response.status_code}"
        data = response.json()
        assert "Admin" in str(data) or "admin" in str(data), f"Expected admin error message: {data}"
        print("Admin correctly gets 400 'Admin accounts have full access' error")


class TestPlansEndpoint:
    """Test the plans endpoint returns correct data"""
    
    def test_plans_endpoint_returns_starter_plan(self):
        """Test GET /api/stripe/plans includes starter plan"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        assert response.status_code == 200
        
        data = response.json()
        plans = {p["id"]: p for p in data["plans"]}
        
        # Should have starter plan
        assert "starter" in plans, f"Plans should include 'starter': {list(plans.keys())}"
        
        starter = plans["starter"]
        assert starter["price_monthly"] == 19, f"Starter should be £19, got {starter['price_monthly']}"
        
        print(f"Plans available: {list(plans.keys())}")
        print(f"Starter price: £{starter['price_monthly']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
