"""
Test suite for TrendScout UK new features:
- Product Validator (public)
- Profit Simulator (public)
- Quick Launch (authenticated)
- CJ Sync (authenticated)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "reviewer@trendscout.click"
ADMIN_PASSWORD = "ShopifyReview2026!"
DEMO_EMAIL = "demo@trendscout.click"
DEMO_PASSWORD = "DemoReview2026!"
AUTOMATION_API_KEY = "vs_automation_key_2024"


class TestPublicProductValidator:
    """Tests for POST /api/public/validate-product - no auth required"""
    
    def test_validate_product_success(self):
        """Test product validation with valid query"""
        response = requests.post(
            f"{BASE_URL}/api/public/validate-product",
            json={"query": "phone case"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "product_name" in data
        assert "launch_score" in data
        assert "launch_label" in data
        assert "signals" in data
        assert "reasoning" in data
        
        # Verify signals structure
        signals = data.get("signals", {})
        assert "trend_momentum" in signals
        assert "profit_margins" in signals
        assert "competition" in signals
        print(f"PASS: Product validation returned score {data['launch_score']} with label '{data['launch_label']}'")
    
    def test_validate_product_led_lights(self):
        """Test product validation with LED lights query"""
        response = requests.post(
            f"{BASE_URL}/api/public/validate-product",
            json={"query": "LED lights"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "launch_score" in data
        assert isinstance(data["launch_score"], (int, float))
        print(f"PASS: LED lights validation returned score {data['launch_score']}")
    
    def test_validate_product_short_query(self):
        """Test validation with too short query"""
        response = requests.post(
            f"{BASE_URL}/api/public/validate-product",
            json={"query": "a"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("PASS: Short query correctly rejected with 400")
    
    def test_validate_product_empty_query(self):
        """Test validation with empty query"""
        response = requests.post(
            f"{BASE_URL}/api/public/validate-product",
            json={"query": ""},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("PASS: Empty query correctly rejected with 400")


class TestPublicProfitSimulator:
    """Tests for POST /api/public/profit-simulator - no auth required"""
    
    def test_profit_simulator_basic(self):
        """Test profit simulator with basic inputs"""
        response = requests.post(
            f"{BASE_URL}/api/public/profit-simulator",
            json={
                "product_cost": 8,
                "selling_price": 25,
                "shipping_cost": 3,
                "monthly_ad_budget": 500,
                "cpm": 15,
                "conversion_rate": 2,
                "competition_level": "medium",
                "include_vat": True
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify unit economics
        assert "unit_economics" in data
        ue = data["unit_economics"]
        assert "margin_per_unit" in ue
        assert "margin_percent" in ue
        assert "vat_per_unit" in ue
        assert "estimated_cpa" in ue
        assert "break_even_cpa" in ue
        
        # Verify projections (30/60/90 days)
        assert "projections" in data
        projections = data["projections"]
        assert len(projections) == 3, f"Expected 3 projections, got {len(projections)}"
        
        for proj in projections:
            assert "month" in proj
            assert "revenue" in proj
            assert "profit" in proj
            assert "roas" in proj
            assert "cumulative_profit" in proj
        
        # Verify verdict
        assert "verdict" in data
        assert "verdict_detail" in data
        
        print(f"PASS: Profit simulator returned verdict '{data['verdict']}'")
        print(f"  - Month 1 profit: £{projections[0]['profit']}")
        print(f"  - Month 2 profit: £{projections[1]['profit']}")
        print(f"  - Month 3 profit: £{projections[2]['profit']}")
    
    def test_profit_simulator_no_vat(self):
        """Test profit simulator without VAT"""
        response = requests.post(
            f"{BASE_URL}/api/public/profit-simulator",
            json={
                "product_cost": 10,
                "selling_price": 30,
                "shipping_cost": 4,
                "monthly_ad_budget": 1000,
                "cpm": 12,
                "conversion_rate": 2.5,
                "competition_level": "low",
                "include_vat": False
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["unit_economics"]["vat_per_unit"] == 0
        print("PASS: Profit simulator without VAT works correctly")
    
    def test_profit_simulator_high_competition(self):
        """Test profit simulator with high competition"""
        response = requests.post(
            f"{BASE_URL}/api/public/profit-simulator",
            json={
                "product_cost": 5,
                "selling_price": 15,
                "shipping_cost": 2,
                "monthly_ad_budget": 300,
                "cpm": 20,
                "conversion_rate": 1.5,
                "competition_level": "high",
                "include_vat": True
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["competition_level"] == "high"
        print(f"PASS: High competition simulation returned verdict '{data['verdict']}'")
    
    def test_profit_simulator_invalid_price(self):
        """Test profit simulator with zero selling price"""
        response = requests.post(
            f"{BASE_URL}/api/public/profit-simulator",
            json={
                "product_cost": 10,
                "selling_price": 0,
                "shipping_cost": 3,
                "monthly_ad_budget": 500,
                "cpm": 15,
                "conversion_rate": 2,
                "competition_level": "medium",
                "include_vat": True
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("PASS: Zero selling price correctly rejected with 400")


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_login_admin(self):
        """Test admin login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        
        data = response.json()
        assert "token" in data or "access_token" in data
        print("PASS: Admin login successful")
        return data.get("token") or data.get("access_token")
    
    def test_login_demo(self):
        """Test demo user login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Demo login failed: {response.text}"
        
        data = response.json()
        assert "token" in data or "access_token" in data
        print("PASS: Demo user login successful")
        return data.get("token") or data.get("access_token")


class TestQuickLaunch:
    """Tests for POST /api/products/{id}/quick-launch - requires auth"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code != 200:
            pytest.skip("Authentication failed")
        data = response.json()
        return data.get("token") or data.get("access_token")
    
    @pytest.fixture
    def product_id(self, auth_token):
        """Get a valid product ID for testing"""
        response = requests.get(
            f"{BASE_URL}/api/products?limit=1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code != 200:
            pytest.skip("Could not fetch products")
        data = response.json()
        products = data.get("data", [])
        if not products:
            pytest.skip("No products available")
        return products[0].get("id")
    
    def test_quick_launch_success(self, auth_token, product_id):
        """Test quick launch endpoint returns full launch pack"""
        response = requests.post(
            f"{BASE_URL}/api/products/{product_id}/quick-launch",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            timeout=30  # AI generation may take time
        )
        assert response.status_code == 200, f"Quick launch failed: {response.text}"
        
        data = response.json()
        
        # Verify success
        assert data.get("success") == True
        assert "launch_id" in data
        
        # Verify product info
        assert "product" in data
        product = data["product"]
        assert "id" in product
        assert "name" in product
        assert "retail_price" in product
        assert "margin" in product
        assert "launch_score" in product
        
        # Verify AI content
        assert "ai_content" in data
        ai = data["ai_content"]
        # AI content should have at least some fields (may have error if AI fails)
        if "error" not in ai:
            assert "headline" in ai or "product_description" in ai
        
        # Verify projections (30/60/90 days)
        assert "projections" in data
        projections = data["projections"]
        assert len(projections) == 3
        for proj in projections:
            assert "month" in proj
            assert "revenue" in proj
            assert "profit" in proj
        
        # Verify platform exports
        assert "platform_exports" in data
        exports = data["platform_exports"]
        assert "shopify" in exports
        assert "woocommerce" in exports
        assert "etsy" in exports
        
        # Verify Shopify export structure
        shopify = exports["shopify"]
        assert "title" in shopify
        assert "body_html" in shopify
        assert "variants" in shopify
        assert "status" in shopify
        
        # Verify WooCommerce export structure
        woo = exports["woocommerce"]
        assert "name" in woo
        assert "regular_price" in woo
        assert "description" in woo
        
        # Verify Etsy export structure
        etsy = exports["etsy"]
        assert "title" in etsy
        assert "price" in etsy
        assert "tags" in etsy
        
        print(f"PASS: Quick launch returned full pack for product '{product['name']}'")
        print(f"  - Launch ID: {data['launch_id']}")
        print(f"  - Projections: 3 months")
        print(f"  - Platform exports: Shopify, WooCommerce, Etsy")
    
    def test_quick_launch_no_auth(self, product_id):
        """Test quick launch without auth returns 401/403"""
        response = requests.post(
            f"{BASE_URL}/api/products/{product_id}/quick-launch",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Quick launch without auth correctly rejected")
    
    def test_quick_launch_invalid_product(self, auth_token):
        """Test quick launch with invalid product ID"""
        response = requests.post(
            f"{BASE_URL}/api/products/invalid-product-id-12345/quick-launch",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 404
        print("PASS: Quick launch with invalid product ID returns 404")


class TestCJSync:
    """Tests for CJ Dropshipping sync endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code != 200:
            pytest.skip("Authentication failed")
        data = response.json()
        return data.get("token") or data.get("access_token")
    
    def test_cj_sync_success(self, auth_token):
        """Test CJ sync endpoint returns counts"""
        response = requests.post(
            f"{BASE_URL}/api/cj/sync",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            timeout=60  # CJ sync can take time due to rate limiting
        )
        assert response.status_code == 200, f"CJ sync failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        
        # Data may be at top level or nested in details
        details = data.get("details", data)
        assert "fetched" in details or "products_fetched" in details
        assert "created" in details or "products_created" in details
        
        fetched = details.get('fetched', details.get('products_fetched', 0))
        created = details.get('created', details.get('products_created', 0))
        skipped = details.get('skipped', details.get('products_skipped', 0))
        
        print(f"PASS: CJ sync returned counts")
        print(f"  - Fetched: {fetched}")
        print(f"  - Created: {created}")
        print(f"  - Skipped: {skipped}")


class TestPublicEndpoints:
    """Tests for other public endpoints"""
    
    def test_trending_products(self):
        """Test public trending products endpoint"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "products" in data
        assert "total" in data
        print(f"PASS: Trending products returned {len(data['products'])} products")
    
    def test_daily_picks(self):
        """Test daily picks endpoint"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200
        
        data = response.json()
        assert "picks" in data
        assert "date" in data
        print(f"PASS: Daily picks returned {len(data['picks'])} picks")
    
    def test_platform_stats(self):
        """Test platform stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/public/platform-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "products_analysed" in data
        print(f"PASS: Platform stats returned {data['products_analysed']} products analysed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
