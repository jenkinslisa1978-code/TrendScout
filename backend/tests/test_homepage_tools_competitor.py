"""
Tests for P4 Homepage Polish, Enhanced Free Tools, and Competitor Intelligence Engine
- Homepage design (/, /tools page)
- TikTok Analyzer, Product Trend Checker (frontend simulation)
- GET /api/products/{id}/competitor-intelligence (public endpoint)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')


class TestCompetitorIntelligence:
    """Test competitor-intelligence endpoint (PUBLIC - no auth needed)"""
    
    @pytest.fixture
    def get_product_id(self):
        """Get a product ID for testing"""
        # First login to get a product ID
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testref@test.com",
            "password": "Test1234!"
        })
        if login_response.status_code != 200:
            pytest.skip("Cannot login to fetch product ID")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        products_response = requests.get(f"{BASE_URL}/api/products?limit=1", headers=headers)
        if products_response.status_code != 200 or not products_response.json().get("data"):
            pytest.skip("No products available for testing")
        
        return products_response.json()["data"][0]["id"]
    
    def test_competitor_intelligence_public_access(self, get_product_id):
        """Test that competitor-intelligence endpoint is public (no auth required)"""
        product_id = get_product_id
        
        # Call without auth
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/competitor-intelligence")
        
        # Should be accessible without auth
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"[PASS] Competitor intelligence endpoint is public (no auth needed)")
    
    def test_competitor_intelligence_response_structure(self, get_product_id):
        """Test response contains all required fields"""
        product_id = get_product_id
        
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/competitor-intelligence")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify required fields
        required_fields = [
            "product_id", "stores_detected", "new_stores_7d", "price_range",
            "avg_store_age_months", "advertising_activity", "ads_detected",
            "competition_level", "competition_impact"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"[PASS] Response contains all required fields: {list(data.keys())}")
    
    def test_competitor_intelligence_data_types(self, get_product_id):
        """Test data types of response fields"""
        product_id = get_product_id
        
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/competitor-intelligence")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check data types
        assert isinstance(data["product_id"], str), "product_id should be string"
        assert isinstance(data["stores_detected"], int), "stores_detected should be int"
        assert isinstance(data["new_stores_7d"], int), "new_stores_7d should be int"
        assert isinstance(data["price_range"], dict), "price_range should be dict"
        assert isinstance(data["avg_store_age_months"], (int, float)), "avg_store_age_months should be number"
        assert isinstance(data["advertising_activity"], str), "advertising_activity should be string"
        assert isinstance(data["ads_detected"], int), "ads_detected should be int"
        assert isinstance(data["competition_level"], str), "competition_level should be string"
        assert isinstance(data["competition_impact"], str), "competition_impact should be string"
        
        print(f"[PASS] All data types are correct")
        print(f"  - stores_detected: {data['stores_detected']}")
        print(f"  - new_stores_7d: {data['new_stores_7d']}")
        print(f"  - price_range: {data['price_range']}")
        print(f"  - avg_store_age_months: {data['avg_store_age_months']}")
        print(f"  - advertising_activity: {data['advertising_activity']}")
        print(f"  - ads_detected: {data['ads_detected']}")
        print(f"  - competition_level: {data['competition_level']}")
        print(f"  - competition_impact: {data['competition_impact']}")
    
    def test_competitor_intelligence_price_range_structure(self, get_product_id):
        """Test price_range has correct structure"""
        product_id = get_product_id
        
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/competitor-intelligence")
        assert response.status_code == 200
        
        data = response.json()
        price_range = data["price_range"]
        
        assert "low" in price_range, "price_range should have 'low'"
        assert "high" in price_range, "price_range should have 'high'"
        assert isinstance(price_range["low"], (int, float)), "price_range.low should be number"
        assert isinstance(price_range["high"], (int, float)), "price_range.high should be number"
        assert price_range["low"] <= price_range["high"], "low price should be <= high price"
        
        print(f"[PASS] Price range structure valid: £{price_range['low']} - £{price_range['high']}")
    
    def test_competitor_intelligence_nonexistent_product(self):
        """Test 404 for non-existent product"""
        response = requests.get(f"{BASE_URL}/api/products/nonexistent-product-id-12345/competitor-intelligence")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"[PASS] Returns 404 for non-existent product")


class TestHealthAndPublicEndpoints:
    """Test public endpoints accessibility"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"[PASS] API health check passed")
    
    def test_public_featured_product(self):
        """Test public featured product endpoint used by homepage"""
        response = requests.get(f"{BASE_URL}/api/public/featured-product")
        # May return empty product but should be 200
        assert response.status_code == 200
        print(f"[PASS] Public featured product endpoint accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
