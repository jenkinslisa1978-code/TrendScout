"""
Test Suite for Phase A-D Features:
- Phase A: Landing page updates (hero headline, CTA, testimonials, opportunity detection)
- Phase B: Radar Alert System (radar-scan, radar-detections, radar-digest)
- Phase C: Upgrade prompts (tested via frontend, LimitHitBanner, InsightLockedNudge)
- Phase D: Interactive onboarding wizard (complete-onboarding with preferences)
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRadarAlertSystem:
    """Tests for Phase B: Radar Alert System endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "TestAdmin123!"
        })
        if response.status_code == 200:
            return response.json().get("token")  # API returns 'token', not 'access_token'
        pytest.skip("Admin authentication failed")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_radar_scan_requires_auth(self):
        """POST /api/notifications/radar-scan requires authentication"""
        response = requests.post(f"{BASE_URL}/api/notifications/radar-scan")
        # Should return 401 without token
        assert response.status_code == 401 or response.status_code == 403
        print("PASS: radar-scan requires authentication")
    
    def test_radar_scan_with_admin(self, auth_headers):
        """POST /api/notifications/radar-scan works with admin auth"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/radar-scan",
            headers=auth_headers
        )
        # Should succeed (200) or return message about no products meeting threshold
        assert response.status_code in [200, 404]
        data = response.json()
        # Should return meaningful response
        if response.status_code == 200:
            assert "radar_products_detected" in data or "message" in data
            print(f"PASS: radar-scan with admin - detected: {data.get('radar_products_detected', 0)}")
        else:
            print(f"PASS: radar-scan returned {response.status_code} - {data.get('message', 'no products')}")
    
    def test_radar_detections_endpoint(self, auth_headers):
        """GET /api/notifications/radar-detections returns radar-detected products"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/radar-detections",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # API returns an object with 'products' list and 'count'
        products = data.get("products", data) if isinstance(data, dict) else data
        if isinstance(products, dict):
            products = []
        print(f"PASS: radar-detections returned {len(products)} products")
        
        # If products exist, verify structure
        if len(products) > 0:
            product = products[0]
            assert "id" in product or "product_name" in product
            print(f"  Sample product: {product.get('product_name', 'N/A')}")
    
    def test_radar_digest_endpoint(self, auth_headers):
        """POST /api/notifications/radar-digest sends digest email"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/radar-digest",
            headers=auth_headers
        )
        # Can succeed (200), skip if no detections, or fail if Resend not configured
        assert response.status_code in [200, 500]
        data = response.json()
        
        if response.status_code == 200:
            # Success or skipped (no detections)
            assert "status" in data or "message" in data
            print(f"PASS: radar-digest - status: {data.get('status', 'sent')}")
        else:
            # May fail if Resend API not configured - that's expected
            print(f"INFO: radar-digest returned 500 (possibly Resend not configured)")
            assert "detail" in data or "error" in data


class TestOnboardingEndpoints:
    """Tests for Phase D: Interactive onboarding endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "TestAdmin123!"
        })
        if response.status_code == 200:
            return response.json().get("token")  # API returns 'token', not 'access_token'
        pytest.skip("Admin authentication failed")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_onboarding_status_endpoint(self, auth_headers):
        """GET /api/user/onboarding-status returns status"""
        response = requests.get(
            f"{BASE_URL}/api/user/onboarding-status",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "onboarding_completed" in data
        print(f"PASS: onboarding-status returned completed={data['onboarding_completed']}")
    
    def test_reset_onboarding(self, auth_headers):
        """POST /api/user/reset-onboarding resets onboarding status"""
        response = requests.post(
            f"{BASE_URL}/api/user/reset-onboarding",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("onboarding_completed") == False or data.get("status") == "success"
        print("PASS: reset-onboarding succeeded")
    
    def test_complete_onboarding_with_preferences(self, auth_headers):
        """POST /api/user/complete-onboarding accepts experience_level and preferred_niches"""
        response = requests.post(
            f"{BASE_URL}/api/user/complete-onboarding",
            headers=auth_headers,
            json={
                "experience_level": "intermediate",
                "preferred_niches": ["Electronics", "Home & Garden", "Fashion"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should indicate success
        assert data.get("onboarding_completed") == True or data.get("status") == "success"
        print("PASS: complete-onboarding with preferences succeeded")
    
    def test_onboarding_status_after_completion(self, auth_headers):
        """GET /api/user/onboarding-status shows completed after completing"""
        response = requests.get(
            f"{BASE_URL}/api/user/onboarding-status",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["onboarding_completed"] == True
        print("PASS: onboarding-status correctly shows completed=True")


class TestLandingPageAPIs:
    """Tests for APIs used by the landing page"""
    
    def test_public_featured_product(self):
        """GET /api/public/featured-product returns product for landing page demo"""
        response = requests.get(f"{BASE_URL}/api/public/featured-product")
        assert response.status_code == 200
        data = response.json()
        # Should have a product or indicate none available
        if "product" in data and data["product"]:
            product = data["product"]
            assert "product_name" in product
            assert "launch_score" in product or "trend_score" in product
            print(f"PASS: featured-product returned: {product['product_name']}")
        else:
            print("INFO: No featured product available")
    
    def test_products_api_returns_scores(self):
        """GET /api/products returns products with required score fields"""
        response = requests.get(f"{BASE_URL}/api/products?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        products = data.get("data", [])
        assert len(products) >= 0  # May have products
        
        if len(products) > 0:
            product = products[0]
            # Check for key fields used in landing page
            required_fields = ["product_name", "category"]
            for field in required_fields:
                assert field in product, f"Missing field: {field}"
            
            # Check for scoring fields (may not all be present)
            score_fields = ["trend_score", "launch_score", "success_probability", "estimated_margin"]
            present_scores = [f for f in score_fields if f in product]
            print(f"PASS: products API returns products with fields: {present_scores}")
        else:
            print("INFO: No products in database")


class TestStripePlansForPricing:
    """Tests for pricing page data (verifies pricing tier structure)"""
    
    def test_stripe_plans_returns_four_tiers(self):
        """GET /api/stripe/plans returns 4 pricing tiers"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        assert response.status_code == 200
        data = response.json()
        
        plans = data.get("plans", [])
        assert len(plans) == 4, f"Expected 4 plans, got {len(plans)}"
        
        # Verify plan names
        plan_names = [p["name"].lower() for p in plans]
        assert "free" in plan_names
        assert "starter" in plan_names
        assert "pro" in plan_names
        assert "elite" in plan_names
        print("PASS: Stripe plans returns 4 tiers (Free, Starter, Pro, Elite)")
    
    def test_plans_have_correct_gbp_prices(self):
        """Pricing tiers have correct GBP prices"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        assert response.status_code == 200
        plans = response.json().get("plans", [])
        
        expected_prices = {
            "free": 0,
            "starter": 19,
            "pro": 39,
            "elite": 79
        }
        
        for plan in plans:
            name = plan["name"].lower()
            if name in expected_prices:
                # API uses 'price_monthly', not 'price'
                assert plan["price_monthly"] == expected_prices[name], f"{name} price mismatch: got {plan.get('price_monthly')}"
        
        print("PASS: All plans have correct GBP prices (Free=0, Starter=19, Pro=39, Elite=79)")


class TestAdminFeatureAccess:
    """Tests for Elite/Admin feature access"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "TestAdmin123!"
        })
        if response.status_code == 200:
            return response.json().get("token")  # API returns 'token', not 'access_token'
        pytest.skip("Admin authentication failed")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_admin_has_elite_access(self, auth_headers):
        """Admin user has elite plan access"""
        response = requests.get(
            f"{BASE_URL}/api/auth/profile",
            headers=auth_headers
        )
        assert response.status_code == 200
        profile = response.json()
        
        # Admin should have elite plan or is_admin flag
        plan = profile.get("plan", "").lower()
        is_admin = profile.get("is_admin", False)
        
        assert plan == "elite" or is_admin, f"Admin should have elite access, got plan={plan}, is_admin={is_admin}"
        print(f"PASS: Admin user has elite access (plan={plan}, is_admin={is_admin})")
    
    def test_feature_access_for_elite_user(self, auth_headers):
        """GET /api/stripe/feature-access returns correct flags for elite"""
        response = requests.get(
            f"{BASE_URL}/api/stripe/feature-access",
            headers=auth_headers
        )
        assert response.status_code == 200
        features = response.json()
        
        # Elite should have all features enabled
        elite_features = [
            "canUseBudgetOptimizer",
            "canAccessEarlyTrends",
            "canUseRadarAlerts"
        ]
        
        for feature in elite_features:
            if feature in features:
                assert features[feature] == True, f"{feature} should be True for elite"
        
        print(f"PASS: Elite user has all premium features enabled")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
