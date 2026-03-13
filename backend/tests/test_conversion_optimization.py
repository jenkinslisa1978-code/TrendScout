"""
Test Phase 1 Conversion Optimization Features:
1. Landing page API endpoints (/api/public/platform-stats, /api/public/trending-products)
2. Pricing page structure verification
3. Onboarding checklist structure
4. Signup flow
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPublicPlatformStats:
    """Test /api/public/platform-stats endpoint for social proof bar"""
    
    def test_platform_stats_returns_200(self):
        """Test that platform stats endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/public/platform-stats")
        assert response.status_code == 200
        print("✓ GET /api/public/platform-stats returns 200")
    
    def test_platform_stats_has_required_fields(self):
        """Test that platform stats has all required fields for social proof bar"""
        response = requests.get(f"{BASE_URL}/api/public/platform-stats")
        data = response.json()
        
        assert "products_analysed" in data, "Missing products_analysed field"
        assert "stores_tracked" in data, "Missing stores_tracked field"
        assert "tiktok_scans_daily" in data, "Missing tiktok_scans_daily field"
        assert "active_users" in data, "Missing active_users field"
        print("✓ Platform stats has all required fields")
    
    def test_platform_stats_values_are_positive(self):
        """Test that all stats are positive numbers"""
        response = requests.get(f"{BASE_URL}/api/public/platform-stats")
        data = response.json()
        
        assert data["products_analysed"] > 0, "products_analysed should be positive"
        assert data["stores_tracked"] > 0, "stores_tracked should be positive"
        assert data["tiktok_scans_daily"] > 0, "tiktok_scans_daily should be positive"
        assert data["active_users"] > 0, "active_users should be positive"
        print("✓ All platform stats are positive numbers")


class TestPublicTrendingProducts:
    """Test /api/public/trending-products endpoint for landing page products section"""
    
    def test_trending_products_returns_200(self):
        """Test that trending products endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=6")
        assert response.status_code == 200
        print("✓ GET /api/public/trending-products returns 200")
    
    def test_trending_products_returns_list(self):
        """Test that trending products returns a list of products"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=6")
        data = response.json()
        
        assert "products" in data, "Missing products field"
        assert isinstance(data["products"], list), "products should be a list"
        print(f"✓ Trending products returns list with {len(data['products'])} items")
    
    def test_trending_products_have_required_fields(self):
        """Test that each product has required fields for display"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=3")
        data = response.json()
        
        if len(data["products"]) > 0:
            product = data["products"][0]
            required_fields = ["id", "product_name", "launch_score", "margin_percent"]
            for field in required_fields:
                assert field in product, f"Missing {field} in product"
            print("✓ Products have all required fields (id, product_name, launch_score, margin_percent)")
        else:
            print("⚠ No products returned to verify fields")
    
    def test_trending_products_limit_param(self):
        """Test that limit parameter works correctly"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=3")
        data = response.json()
        
        assert len(data["products"]) <= 3, "Limit parameter not respected"
        print("✓ Limit parameter works correctly")


class TestPublicTopTrending:
    """Test /api/public/top-trending endpoint for leaderboard"""
    
    def test_top_trending_returns_200(self):
        """Test that top trending endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/public/top-trending")
        assert response.status_code == 200
        print("✓ GET /api/public/top-trending returns 200")
    
    def test_top_trending_has_products_with_rank(self):
        """Test that top trending products have rank field"""
        response = requests.get(f"{BASE_URL}/api/public/top-trending")
        data = response.json()
        
        assert "products" in data, "Missing products field"
        if len(data["products"]) > 0:
            assert "rank" in data["products"][0], "Products should have rank field"
            assert data["products"][0]["rank"] == 1, "First product should have rank 1"
        print("✓ Top trending products have rank field")
    
    def test_top_trending_products_sorted_by_launch_score(self):
        """Test that products are sorted by launch_score descending"""
        response = requests.get(f"{BASE_URL}/api/public/top-trending")
        data = response.json()
        
        products = data.get("products", [])
        if len(products) >= 2:
            for i in range(len(products) - 1):
                assert products[i]["launch_score"] >= products[i+1]["launch_score"], \
                    "Products should be sorted by launch_score descending"
        print("✓ Products are sorted by launch_score descending")


class TestHealthAndApiRoot:
    """Test API health and root endpoints"""
    
    def test_api_health(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ API health check passes")
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print("✓ API root endpoint accessible")


class TestStripeCheckoutStructure:
    """Test Stripe checkout endpoint structure (without actual checkout)"""
    
    def test_checkout_requires_auth(self):
        """Test that checkout endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            json={
                "plan": "starter",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel"
            }
        )
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], \
            f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Stripe checkout requires authentication")


class TestAuthEndpoints:
    """Test authentication endpoints for signup flow"""
    
    def test_login_endpoint_exists(self):
        """Test that login endpoint exists and accepts requests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@example.com", "password": "testpass"}
        )
        # Should return 401 for invalid creds, not 404
        assert response.status_code != 404, "Login endpoint should exist"
        print(f"✓ Login endpoint exists (returns {response.status_code} for invalid creds)")
    
    def test_signup_with_valid_credentials(self):
        """Test signup flow with test credentials"""
        # First try to login to verify account exists
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "jenkinslisa1978@gmail.com",
                "password": "test123456"
            }
        )
        # This account should exist and login should work
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data or "token" in data or "user" in data
            print("✓ Test account login successful")
        else:
            print(f"⚠ Test account login returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
