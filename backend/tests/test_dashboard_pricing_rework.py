"""
Dashboard & Pricing Rework Tests - Phase 39
Tests for: 3-tier pricing model, auth, feature access, stripe plans
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials from context
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "TestAdmin123!"


class TestAuth:
    """Authentication endpoint tests"""
    
    def test_login_success(self):
        """Test login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        # Status code assertion
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        # Data assertions - validate response structure
        data = response.json()
        assert "token" in data, "Missing token in response"
        assert "user" in data, "Missing user in response"
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"✓ Login successful - token received")
    
    def test_profile_with_auth(self):
        """Test profile endpoint returns user with plan and admin status"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        
        assert response.status_code == 200, f"Profile failed: {response.text}"
        
        data = response.json()
        assert "email" in data, "Missing email in profile"
        assert "id" in data, "Missing id in profile"
        print(f"✓ Profile retrieved - email: {data.get('email')}, plan: {data.get('plan')}, is_admin: {data.get('is_admin')}")


class TestStripePlans:
    """Stripe plans endpoint tests - GBP pricing verification"""
    
    def test_get_plans_returns_four_tiers(self):
        """Test /api/stripe/plans returns 4 tiers: Free, Starter, Pro, Elite"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        
        assert response.status_code == 200, f"Plans endpoint failed: {response.text}"
        
        data = response.json()
        assert "plans" in data, "Missing plans in response"
        assert "currency" in data, "Missing currency in response"
        
        plans = data["plans"]
        assert len(plans) >= 4, f"Expected 4 plans, got {len(plans)}"
        
        plan_names = [p["name"].lower() for p in plans]
        assert "free" in plan_names, "Missing Free plan"
        assert "starter" in plan_names, "Missing Starter plan"
        assert "pro" in plan_names, "Missing Pro plan"
        assert "elite" in plan_names, "Missing Elite plan"
        
        print(f"✓ Found {len(plans)} plans: {plan_names}")
    
    def test_plans_have_correct_gbp_pricing(self):
        """Test pricing: Free=0, Starter=19, Pro=39, Elite=79 GBP"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        
        assert response.status_code == 200, f"Plans endpoint failed: {response.text}"
        
        data = response.json()
        assert data.get("currency") == "gbp", f"Expected currency=gbp, got {data.get('currency')}"
        
        plans_by_name = {p["name"].lower(): p for p in data["plans"]}
        
        # Verify prices
        assert plans_by_name["free"]["price_monthly"] == 0, "Free should be £0"
        assert plans_by_name["starter"]["price_monthly"] == 19, "Starter should be £19"
        assert plans_by_name["pro"]["price_monthly"] == 39, "Pro should be £39"
        assert plans_by_name["elite"]["price_monthly"] == 79, "Elite should be £79"
        
        print("✓ Pricing verified: Free=£0, Starter=£19, Pro=£39, Elite=£79")
    
    def test_plans_have_features(self):
        """Test each plan has features object"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        
        assert response.status_code == 200
        
        data = response.json()
        for plan in data["plans"]:
            assert "features" in plan, f"Plan {plan['name']} missing features"
            assert isinstance(plan["features"], dict), f"Plan {plan['name']} features should be dict"
        
        print("✓ All plans have features object")


class TestFeatureAccess:
    """Feature access endpoint tests for admin/elite user"""
    
    def test_feature_access_for_admin(self):
        """Test /api/stripe/feature-access returns correct flags for admin"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["token"]
        
        # Get feature access
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/stripe/feature-access", headers=headers)
        
        assert response.status_code == 200, f"Feature access failed: {response.text}"
        
        data = response.json()
        
        # Admin should have elite plan
        assert data.get("plan") == "elite", f"Admin should have elite plan, got {data.get('plan')}"
        assert data.get("is_admin") == True, "Admin flag should be True"
        
        # Check features object
        assert "features" in data, "Missing features in response"
        features = data["features"]
        
        # Elite features should all be enabled
        assert features.get("full_reports") == True, "Elite should have full_reports"
        assert features.get("full_insights") == True, "Elite should have full_insights"
        assert features.get("early_trends") == True, "Elite should have early_trends"
        assert features.get("advanced_opportunities") == True, "Elite should have advanced_opportunities"
        
        print(f"✓ Feature access verified for admin - plan: {data.get('plan')}, features enabled")


class TestProducts:
    """Product endpoints for dashboard widgets"""
    
    def test_get_products(self):
        """Test GET /api/products returns products for dashboard"""
        response = requests.get(f"{BASE_URL}/api/products?limit=10&sortBy=trend_score&sortOrder=desc")
        
        assert response.status_code == 200, f"Products endpoint failed: {response.text}"
        
        data = response.json()
        assert "data" in data, "Missing data in response"
        
        products = data["data"]
        print(f"✓ Got {len(products)} products")
        
        if len(products) > 0:
            # Check product structure
            product = products[0]
            assert "id" in product, "Product missing id"
            assert "product_name" in product, "Product missing product_name"
            print(f"✓ First product: {product.get('product_name')}")
    
    def test_products_have_launch_score_fields(self):
        """Test products have win_score and early_trend_label for radar"""
        response = requests.get(f"{BASE_URL}/api/products?limit=10")
        
        assert response.status_code == 200
        
        data = response.json()
        products = data.get("data", [])
        
        if len(products) > 0:
            product = products[0]
            # Check for fields used by WhileYouWereAway and TrendScout Radar
            print(f"  - trend_score: {product.get('trend_score')}")
            print(f"  - early_trend_score: {product.get('early_trend_score')}")
            print(f"  - early_trend_label: {product.get('early_trend_label')}")
            print(f"  - supplier_cost: {product.get('supplier_cost')}")
            print(f"  - estimated_retail_price: {product.get('estimated_retail_price')}")


class TestDashboardWidgetData:
    """Test data for dashboard widgets"""
    
    def test_while_you_were_away_data(self):
        """Test data availability for WhileYouWereAway widget"""
        response = requests.get(f"{BASE_URL}/api/products?sortBy=trend_score&sortOrder=desc&limit=50")
        
        assert response.status_code == 200
        
        data = response.json()
        products = data.get("data", [])
        
        # Count products by early_trend_label
        exploding = len([p for p in products if p.get('early_trend_label') == 'exploding'])
        emerging = len([p for p in products if p.get('early_trend_label') in ['emerging', 'rising']])
        
        # Count high margin products (>60% margin)
        high_margin = 0
        for p in products:
            cost = p.get('supplier_cost', 0)
            retail = p.get('estimated_retail_price', 0) or p.get('recommended_price', 0)
            if cost > 0 and retail > 0 and ((retail - cost) / retail) > 0.6:
                high_margin += 1
        
        print(f"✓ WhileYouWereAway data: {exploding} exploding, {emerging} emerging, {high_margin} high margin")
    
    def test_trendscout_radar_data(self):
        """Test products have data for TrendScout Radar (Launch Score, etc)"""
        response = requests.get(f"{BASE_URL}/api/products?sortBy=trend_score&sortOrder=desc&limit=5")
        
        assert response.status_code == 200
        
        data = response.json()
        products = data.get("data", [])
        
        print(f"✓ TrendScout Radar - {len(products)} products")
        for p in products[:3]:
            # Calculate win_score like frontend does
            win_score = round(
                (p.get('trend_score', 0) * 0.3) +
                (p.get('early_trend_score', 0) * 0.3) +
                (p.get('success_probability', 0) * 0.4)
            )
            print(f"  - {p.get('product_name', 'Unknown')[:30]}: Launch Score={win_score}, Category={p.get('category')}")


class TestHealthEndpoints:
    """Basic health checks"""
    
    def test_api_health(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200, f"Health check failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "healthy", f"API not healthy: {data}"
        print("✓ API health check passed")
    
    def test_api_root(self):
        """Test /api/ root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        
        assert response.status_code == 200
        print("✓ API root endpoint accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
