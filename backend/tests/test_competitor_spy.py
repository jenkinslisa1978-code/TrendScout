"""
Test suite for Competitor Store Spy feature
- POST /api/competitor-spy/scan (PUBLIC - no auth required)
- POST /api/competitor-spy/deep-analysis (PREMIUM - auth required)
- Regression tests for previous features
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "reviewer@trendscout.click"
ADMIN_PASSWORD = "ShopifyReview2026!"
DEMO_EMAIL = "demo@trendscout.click"
DEMO_PASSWORD = "DemoReview2026!"


class TestCompetitorSpyScan:
    """Tests for PUBLIC /api/competitor-spy/scan endpoint"""
    
    def test_scan_valid_shopify_store(self):
        """Test scanning a valid Shopify store (gymshark.com)"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-spy/scan",
            json={"url": "gymshark.com"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Scan response status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Scan response keys: {data.keys()}")
        
        # Verify required fields in response
        assert data.get("success") == True, "Expected success=True"
        assert "store_url" in data, "Missing store_url"
        assert "domain" in data, "Missing domain"
        assert "product_count" in data, "Missing product_count"
        assert "store_size" in data, "Missing store_size"
        assert "pricing" in data, "Missing pricing"
        assert "revenue_estimate" in data, "Missing revenue_estimate"
        assert "velocity" in data, "Missing velocity"
        assert "threat" in data, "Missing threat"
        assert "categories" in data, "Missing categories"
        assert "best_sellers" in data, "Missing best_sellers"
        assert "newest_products" in data, "Missing newest_products"
        
        # Verify pricing structure
        pricing = data.get("pricing", {})
        assert "min" in pricing, "Missing pricing.min"
        assert "max" in pricing, "Missing pricing.max"
        assert "avg" in pricing, "Missing pricing.avg"
        assert "strategy" in pricing, "Missing pricing.strategy"
        
        # Verify threat structure
        threat = data.get("threat", {})
        assert "level" in threat, "Missing threat.level"
        assert threat["level"] in ["High", "Medium", "Low"], f"Invalid threat level: {threat['level']}"
        
        # Verify velocity structure
        velocity = data.get("velocity", {})
        assert "level" in velocity, "Missing velocity.level"
        
        print(f"PASS: Scanned {data['domain']} - {data['product_count']} products, Threat: {threat['level']}")
    
    def test_scan_with_https_prefix(self):
        """Test scanning with full https:// URL"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-spy/scan",
            json={"url": "https://gymshark.com"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("PASS: Scan with https:// prefix works")
    
    def test_scan_invalid_url_format(self):
        """Test scanning with invalid URL format"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-spy/scan",
            json={"url": "not-a-valid-url"},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        # Should return 400 for non-Shopify or unreachable stores
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Invalid URL returns 400")
    
    def test_scan_empty_url(self):
        """Test scanning with empty URL"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-spy/scan",
            json={"url": ""},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Empty URL returns 400")
    
    def test_scan_missing_url(self):
        """Test scanning without URL field"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-spy/scan",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Missing URL returns 400")
    
    def test_scan_non_shopify_store(self):
        """Test scanning a non-Shopify store"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-spy/scan",
            json={"url": "google.com"},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        # Should return 400 as google.com doesn't have /products.json
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Non-Shopify store returns 400")


class TestCompetitorSpyDeepAnalysis:
    """Tests for PREMIUM /api/competitor-spy/deep-analysis endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for authenticated requests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Could not authenticate - skipping authenticated tests")
    
    def test_deep_analysis_without_auth(self):
        """Test deep analysis without authentication - should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-spy/deep-analysis",
            json={"url": "gymshark.com"},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Deep analysis without auth returns 401/403")
    
    def test_deep_analysis_with_auth(self, auth_token):
        """Test deep analysis with authentication - should return AI analysis"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-spy/deep-analysis",
            json={"url": "gymshark.com"},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            },
            timeout=60  # AI analysis takes longer
        )
        print(f"Deep analysis response status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Deep analysis response keys: {data.keys()}")
        
        # Verify required fields
        assert data.get("success") == True, "Expected success=True"
        assert "domain" in data, "Missing domain"
        assert "product_count" in data, "Missing product_count"
        assert "ai_analysis" in data, "Missing ai_analysis"
        
        # Verify AI analysis structure
        ai = data.get("ai_analysis", {})
        print(f"AI analysis keys: {ai.keys()}")
        
        # Check for expected AI analysis fields
        expected_fields = ["strengths", "weaknesses", "how_to_compete"]
        for field in expected_fields:
            if field in ai:
                print(f"  - {field}: present")
        
        print(f"PASS: Deep analysis returned AI insights for {data['domain']}")
    
    def test_deep_analysis_empty_url(self, auth_token):
        """Test deep analysis with empty URL"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-spy/deep-analysis",
            json={"url": ""},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            },
            timeout=15
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Deep analysis with empty URL returns 400")


class TestRegressionPreviousFeatures:
    """Regression tests for features from iteration_130"""
    
    def test_product_validator_public(self):
        """Test POST /api/public/validate-product still works"""
        response = requests.post(
            f"{BASE_URL}/api/public/validate-product",
            json={"query": "phone case"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        assert "launch_score" in data or "score" in data, "Missing score field"
        print("PASS: Product validator still works")
    
    def test_profit_simulator_public(self):
        """Test POST /api/public/profit-simulator still works"""
        response = requests.post(
            f"{BASE_URL}/api/public/profit-simulator",
            json={
                "selling_price": 29.99,
                "cost_price": 10.00,
                "shipping_cost": 3.00,
                "monthly_units": 100,
                "ad_spend_percent": 30,
                "include_vat": True,
                "competition_level": "medium"
            },
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "unit_economics" in data or "projections" in data, "Missing expected fields"
        print("PASS: Profit simulator still works")
    
    def test_auth_login(self):
        """Test POST /api/auth/login still works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "token" in data, "Missing token in response"
        print("PASS: Auth login still works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
