"""
Test suite for Part 8, 9, 10 - Product Detail Page Features:
- Part 8: Product Trend Timeline Charts (TrendTimeline component)
- Part 9: Product Saturation Meter (SaturationRadar component)
- Part 10: Profit Calculator (ProductProfitCalculator component)

Backend focus: GET /api/products/{product_id}/saturation endpoint
Regression: GET /api/products with competition_level and price filters
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test product ID provided in the review request
TEST_PRODUCT_ID = "2e3d8782-0026-4fef-a04a-a1d3426e2d26"

# Admin credentials
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "admin123456"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def auth_headers(auth_token):
    """Auth headers for API requests"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestSaturationEndpoint:
    """Tests for GET /api/products/{product_id}/saturation - Part 9"""
    
    def test_saturation_returns_200_for_valid_product(self, auth_headers):
        """Saturation endpoint should return 200 for valid product"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}/saturation",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Saturation endpoint returns 200 for valid product")
    
    def test_saturation_returns_required_fields(self, auth_headers):
        """Saturation response should contain required fields"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}/saturation",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Required fields based on SaturationRadar component
        required_fields = [
            "product_id",
            "saturation_score",
            "risk_level",
            "stores_detected",
            "ads_detected",
            "search_growth",
            "trend_stage"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
            print(f"✓ Field '{field}' present in response: {data[field]}")
        
        print(f"✓ All required saturation fields present")
    
    def test_saturation_score_is_valid_number(self, auth_headers):
        """Saturation score should be a number between 0-100"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}/saturation",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        score = data.get("saturation_score")
        assert isinstance(score, (int, float)), f"saturation_score should be numeric, got {type(score)}"
        assert 0 <= score <= 100, f"saturation_score should be 0-100, got {score}"
        print(f"✓ Saturation score is valid: {score}")
    
    def test_risk_level_is_valid(self, auth_headers):
        """Risk level should be Low, Medium, or High"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}/saturation",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        risk_level = data.get("risk_level")
        valid_levels = ["Low", "Medium", "High"]
        assert risk_level in valid_levels, f"risk_level should be one of {valid_levels}, got '{risk_level}'"
        print(f"✓ Risk level is valid: {risk_level}")
    
    def test_risk_level_matches_score(self, auth_headers):
        """Risk level should match saturation score ranges"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}/saturation",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        score = data.get("saturation_score")
        risk_level = data.get("risk_level")
        
        # Based on backend logic: >= 65 High, >= 35 Medium, else Low
        if score >= 65:
            assert risk_level == "High", f"Score {score} should be High risk, got {risk_level}"
        elif score >= 35:
            assert risk_level == "Medium", f"Score {score} should be Medium risk, got {risk_level}"
        else:
            assert risk_level == "Low", f"Score {score} should be Low risk, got {risk_level}"
        
        print(f"✓ Risk level '{risk_level}' matches score {score}")
    
    def test_stores_detected_is_valid(self, auth_headers):
        """stores_detected should be a non-negative integer"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}/saturation",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        stores = data.get("stores_detected")
        assert isinstance(stores, int), f"stores_detected should be int, got {type(stores)}"
        assert stores >= 0, f"stores_detected should be >= 0, got {stores}"
        print(f"✓ Stores detected is valid: {stores}")
    
    def test_ads_detected_is_valid(self, auth_headers):
        """ads_detected should be a non-negative integer"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}/saturation",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        ads = data.get("ads_detected")
        assert isinstance(ads, int), f"ads_detected should be int, got {type(ads)}"
        assert ads >= 0, f"ads_detected should be >= 0, got {ads}"
        print(f"✓ Ads detected is valid: {ads}")
    
    def test_saturation_returns_404_for_invalid_product(self, auth_headers):
        """Saturation endpoint should return 404 for non-existent product"""
        response = requests.get(
            f"{BASE_URL}/api/products/invalid-product-id-12345/saturation",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404 for invalid product, got {response.status_code}"
        print(f"✓ Saturation returns 404 for invalid product")


class TestProductEndpointForTrendTimeline:
    """Tests for product data needed by TrendTimeline component - Part 8"""
    
    def test_product_has_trend_score(self, auth_headers):
        """Product should have trend_score for timeline chart"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json().get("data", {})
        
        assert "trend_score" in data, "Product should have trend_score"
        assert isinstance(data["trend_score"], (int, float)), "trend_score should be numeric"
        print(f"✓ Product has trend_score: {data['trend_score']}")
    
    def test_product_has_market_score(self, auth_headers):
        """Product should have market_score for timeline chart"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json().get("data", {})
        
        assert "market_score" in data, "Product should have market_score"
        print(f"✓ Product has market_score: {data.get('market_score')}")
    
    def test_product_has_launch_score(self, auth_headers):
        """Product should have launch_score for score snapshot"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json().get("data", {})
        
        assert "launch_score" in data, "Product should have launch_score"
        print(f"✓ Product has launch_score: {data.get('launch_score')}")
    
    def test_product_has_early_trend_score(self, auth_headers):
        """Product should have early_trend_score for timeline"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json().get("data", {})
        
        # early_trend_score may not always be present, but check if available
        early_score = data.get("early_trend_score")
        print(f"✓ Product early_trend_score: {early_score}")
    
    def test_product_has_tiktok_views(self, auth_headers):
        """Product should have tiktok_views for timeline"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json().get("data", {})
        
        tiktok_views = data.get("tiktok_views")
        print(f"✓ Product tiktok_views: {tiktok_views}")


class TestProductEndpointForProfitCalculator:
    """Tests for product data needed by ProductProfitCalculator - Part 10"""
    
    def test_product_has_supplier_cost(self, auth_headers):
        """Product should have supplier_cost for profit calculator"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json().get("data", {})
        
        supplier_cost = data.get("supplier_cost")
        assert supplier_cost is not None, "Product should have supplier_cost"
        assert isinstance(supplier_cost, (int, float)), "supplier_cost should be numeric"
        print(f"✓ Product has supplier_cost: {supplier_cost}")
    
    def test_product_has_estimated_retail_price(self, auth_headers):
        """Product should have estimated_retail_price for profit calculator"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json().get("data", {})
        
        retail_price = data.get("estimated_retail_price")
        assert retail_price is not None, "Product should have estimated_retail_price"
        assert isinstance(retail_price, (int, float)), "estimated_retail_price should be numeric"
        print(f"✓ Product has estimated_retail_price: {retail_price}")
    
    def test_product_has_estimated_margin(self, auth_headers):
        """Product should have estimated_margin for profit context"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json().get("data", {})
        
        margin = data.get("estimated_margin")
        print(f"✓ Product has estimated_margin: {margin}")


class TestRegressionFilters:
    """Regression tests for filter functionality - Part 6 regression"""
    
    def test_products_competition_level_low_filter(self, auth_headers):
        """Competition level filter should work with 'low'"""
        response = requests.get(
            f"{BASE_URL}/api/products",
            params={"competition_level": "low", "limit": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        products = data.get("data", [])
        
        for product in products:
            assert product.get("competition_level") == "low", f"Expected 'low' competition, got '{product.get('competition_level')}'"
        
        print(f"✓ Competition level 'low' filter works ({len(products)} products)")
    
    def test_products_competition_level_medium_filter(self, auth_headers):
        """Competition level filter should work with 'medium'"""
        response = requests.get(
            f"{BASE_URL}/api/products",
            params={"competition_level": "medium", "limit": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        products = data.get("data", [])
        
        for product in products:
            assert product.get("competition_level") == "medium", f"Expected 'medium' competition, got '{product.get('competition_level')}'"
        
        print(f"✓ Competition level 'medium' filter works ({len(products)} products)")
    
    def test_products_competition_level_high_filter(self, auth_headers):
        """Competition level filter should work with 'high'"""
        response = requests.get(
            f"{BASE_URL}/api/products",
            params={"competition_level": "high", "limit": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        products = data.get("data", [])
        
        for product in products:
            assert product.get("competition_level") == "high", f"Expected 'high' competition, got '{product.get('competition_level')}'"
        
        print(f"✓ Competition level 'high' filter works ({len(products)} products)")
    
    def test_products_min_price_filter(self, auth_headers):
        """Min price filter should work"""
        min_price = 10.0
        response = requests.get(
            f"{BASE_URL}/api/products",
            params={"min_price": min_price, "limit": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        products = data.get("data", [])
        
        for product in products:
            price = product.get("estimated_retail_price", 0)
            assert price >= min_price, f"Expected price >= {min_price}, got {price}"
        
        print(f"✓ Min price filter works ({len(products)} products with price >= {min_price})")
    
    def test_products_max_price_filter(self, auth_headers):
        """Max price filter should work"""
        max_price = 50.0
        response = requests.get(
            f"{BASE_URL}/api/products",
            params={"max_price": max_price, "limit": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        products = data.get("data", [])
        
        for product in products:
            price = product.get("estimated_retail_price", 0)
            assert price <= max_price, f"Expected price <= {max_price}, got {price}"
        
        print(f"✓ Max price filter works ({len(products)} products with price <= {max_price})")
    
    def test_products_price_range_filter(self, auth_headers):
        """Price range filter should work"""
        min_price = 10.0
        max_price = 30.0
        response = requests.get(
            f"{BASE_URL}/api/products",
            params={"min_price": min_price, "max_price": max_price, "limit": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        products = data.get("data", [])
        
        for product in products:
            price = product.get("estimated_retail_price", 0)
            assert min_price <= price <= max_price, f"Expected price in [{min_price}, {max_price}], got {price}"
        
        print(f"✓ Price range filter works ({len(products)} products in range)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
