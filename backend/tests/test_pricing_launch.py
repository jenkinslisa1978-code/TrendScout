"""
Pricing Launch Tests - TrendScout Production Readiness
Tests for Starter (£19), Pro (£39), Elite (£79) pricing alignment
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthCheck:
    """Backend health check tests"""
    
    def test_api_health(self):
        """GET /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        print(f"Health check passed: {data}")


class TestPricingPlans:
    """Tests for /api/stripe/plans endpoint - pricing data verification"""
    
    def test_plans_endpoint_returns_correct_plans(self):
        """GET /api/stripe/plans returns all 4 plans"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "plans" in data
        assert "currency" in data
        assert data["currency"] == "gbp"
        assert data["currency_symbol"] == "£"
        
        plans = data["plans"]
        assert len(plans) == 4
        print(f"Found {len(plans)} plans")
    
    def test_free_plan_pricing(self):
        """Free plan is £0"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        free_plan = next((p for p in data["plans"] if p["id"] == "free"), None)
        
        assert free_plan is not None
        assert free_plan["name"] == "Free"
        assert free_plan["price_monthly"] == 0
        assert free_plan["currency"] == "gbp"
        print("Free plan verified: £0/month")
    
    def test_starter_plan_pricing(self):
        """Starter plan is £19/month"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        starter_plan = next((p for p in data["plans"] if p["id"] == "starter"), None)
        
        assert starter_plan is not None
        assert starter_plan["name"] == "Starter"
        assert starter_plan["price_monthly"] == 19
        assert starter_plan["currency"] == "gbp"
        print("Starter plan verified: £19/month")
    
    def test_pro_plan_pricing(self):
        """Pro plan is £39/month"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        pro_plan = next((p for p in data["plans"] if p["id"] == "pro"), None)
        
        assert pro_plan is not None
        assert pro_plan["name"] == "Pro"
        assert pro_plan["price_monthly"] == 39
        assert pro_plan["currency"] == "gbp"
        print("Pro plan verified: £39/month")
    
    def test_elite_plan_pricing(self):
        """Elite plan is £79/month"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        elite_plan = next((p for p in data["plans"] if p["id"] == "elite"), None)
        
        assert elite_plan is not None
        assert elite_plan["name"] == "Elite"
        assert elite_plan["price_monthly"] == 79
        assert elite_plan["currency"] == "gbp"
        print("Elite plan verified: £79/month")
    
    def test_no_growth_plan_exists(self):
        """Ensure old 'Growth' plan is not present"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        data = response.json()
        plan_names = [p["name"] for p in data["plans"]]
        plan_ids = [p["id"] for p in data["plans"]]
        
        assert "Growth" not in plan_names
        assert "growth" not in plan_ids
        print("Confirmed: No 'Growth' plan in backend")


class TestAuthLogin:
    """Authentication tests"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login works with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == "jenkinslisa1978@gmail.com"
        print(f"Admin login successful: {data['user']['email']}")
    
    def test_test_user_login_success(self):
        """POST /api/auth/login works with test user credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test_refactor@test.com",
            "password": "test123456"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        print(f"Test user login successful: {data['user']['email']}")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login rejects invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("Invalid credentials correctly rejected")


class TestFeatureAccess:
    """Tests for /api/stripe/feature-access endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        return response.json()["token"]
    
    @pytest.fixture
    def test_user_token(self):
        """Get test user auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test_refactor@test.com",
            "password": "test123456"
        })
        return response.json()["token"]
    
    def test_admin_gets_elite_access(self, admin_token):
        """Admin user gets elite plan access"""
        response = requests.get(
            f"{BASE_URL}/api/stripe/feature-access",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["plan"] == "elite"
        assert data["is_admin"] == True
        assert data["admin_bypass"] == True
        assert data["features"]["full_reports"] == True
        assert data["features"]["full_insights"] == True
        assert data["features"]["pdf_export"] == True
        print("Admin feature access verified: elite plan with all features")
    
    def test_feature_access_requires_auth(self):
        """Feature access endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/stripe/feature-access")
        assert response.status_code == 401
        print("Feature access correctly requires authentication")


class TestCheckoutSession:
    """Tests for /api/stripe/create-checkout-session endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        return response.json()["token"]
    
    @pytest.fixture
    def test_user_token(self):
        """Get test user auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test_refactor@test.com",
            "password": "test123456"
        })
        return response.json()["token"]
    
    def test_admin_cannot_checkout(self, admin_token):
        """Admin accounts don't need checkout (have full access)"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "plan": "starter",
                "success_url": "https://product-scout-80.preview.emergentagent.com/pricing",
                "cancel_url": "https://product-scout-80.preview.emergentagent.com/pricing"
            }
        )
        # Admin should be blocked from checkout
        assert response.status_code == 400
        data = response.json()
        assert "Admin accounts have full access" in data["detail"]
        print("Admin checkout correctly blocked")
    
    def test_starter_checkout_session(self, test_user_token):
        """Create checkout session for starter plan"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "plan": "starter",
                "success_url": "https://product-scout-80.preview.emergentagent.com/pricing",
                "cancel_url": "https://product-scout-80.preview.emergentagent.com/pricing"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "url" in data or "demo_mode" in data
        print("Starter checkout session created successfully")
    
    def test_pro_checkout_session(self, test_user_token):
        """Create checkout session for pro plan"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "plan": "pro",
                "success_url": "https://product-scout-80.preview.emergentagent.com/pricing",
                "cancel_url": "https://product-scout-80.preview.emergentagent.com/pricing"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("Pro checkout session created successfully")
    
    def test_elite_checkout_session(self, test_user_token):
        """Create checkout session for elite plan"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "plan": "elite",
                "success_url": "https://product-scout-80.preview.emergentagent.com/pricing",
                "cancel_url": "https://product-scout-80.preview.emergentagent.com/pricing"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("Elite checkout session created successfully")
    
    def test_free_plan_checkout_rejected(self, test_user_token):
        """Cannot create checkout session for free plan"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "plan": "free",
                "success_url": "https://product-scout-80.preview.emergentagent.com/pricing",
                "cancel_url": "https://product-scout-80.preview.emergentagent.com/pricing"
            }
        )
        assert response.status_code == 400
        print("Free plan checkout correctly rejected")
    
    def test_invalid_plan_checkout_rejected(self, test_user_token):
        """Cannot create checkout session for invalid plan"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "plan": "growth",  # Old plan name that shouldn't exist
                "success_url": "https://product-scout-80.preview.emergentagent.com/pricing",
                "cancel_url": "https://product-scout-80.preview.emergentagent.com/pricing"
            }
        )
        assert response.status_code == 400
        print("Invalid plan 'growth' correctly rejected")
    
    def test_checkout_requires_auth(self):
        """Checkout endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            json={
                "plan": "pro",
                "success_url": "https://product-scout-80.preview.emergentagent.com/pricing",
                "cancel_url": "https://product-scout-80.preview.emergentagent.com/pricing"
            }
        )
        assert response.status_code == 401
        print("Checkout correctly requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
