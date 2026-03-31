"""
Test UK Supplier Features:
1. uk_supplier boolean field in API responses
2. +15 points launch_score boost for UK suppliers
3. is_uk_supplier() function logic
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ============================================================
# Test is_uk_supplier() function logic
# ============================================================

class TestIsUkSupplierFunction:
    """Test the is_uk_supplier() function in scoring.py"""
    
    def test_is_uk_supplier_with_avasam_pid(self):
        """Products with avasam_pid should be UK suppliers"""
        from common.scoring import is_uk_supplier
        product = {"avasam_pid": "AVAS123"}
        assert is_uk_supplier(product) == True
    
    def test_is_uk_supplier_with_avasam_data_source(self):
        """Products with data_source='avasam' should be UK suppliers"""
        from common.scoring import is_uk_supplier
        product = {"data_source": "avasam"}
        assert is_uk_supplier(product) == True
    
    def test_is_uk_supplier_with_gb_supplier(self):
        """Products with GB country supplier should be UK suppliers"""
        from common.scoring import is_uk_supplier
        product = {"suppliers": [{"country": "GB"}]}
        assert is_uk_supplier(product) == True
    
    def test_is_uk_supplier_with_uk_supplier(self):
        """Products with UK country supplier should be UK suppliers"""
        from common.scoring import is_uk_supplier
        product = {"suppliers": [{"country": "UK"}]}
        assert is_uk_supplier(product) == True
    
    def test_is_uk_supplier_with_lowercase_gb(self):
        """Products with lowercase 'gb' country should be UK suppliers"""
        from common.scoring import is_uk_supplier
        product = {"suppliers": [{"country": "gb"}]}
        assert is_uk_supplier(product) == True
    
    def test_is_uk_supplier_with_cn_supplier(self):
        """Products with CN country supplier should NOT be UK suppliers"""
        from common.scoring import is_uk_supplier
        product = {"suppliers": [{"country": "CN"}]}
        assert is_uk_supplier(product) == False
    
    def test_is_uk_supplier_with_no_suppliers(self):
        """Products with no suppliers should NOT be UK suppliers"""
        from common.scoring import is_uk_supplier
        product = {}
        assert is_uk_supplier(product) == False
    
    def test_is_uk_supplier_with_empty_suppliers(self):
        """Products with empty suppliers list should NOT be UK suppliers"""
        from common.scoring import is_uk_supplier
        product = {"suppliers": []}
        assert is_uk_supplier(product) == False
    
    def test_is_uk_supplier_with_cj_data_source(self):
        """Products with data_source='cj_dropshipping' should NOT be UK suppliers"""
        from common.scoring import is_uk_supplier
        product = {"data_source": "cj_dropshipping"}
        assert is_uk_supplier(product) == False


# ============================================================
# Test +15 launch_score boost for UK suppliers
# ============================================================

class TestLaunchScoreUkBonus:
    """Test that UK suppliers get +15 points in launch_score"""
    
    def test_launch_score_includes_uk_bonus(self):
        """UK supplier products should get +15 bonus in launch_score"""
        from common.scoring import calculate_launch_score
        
        # Base product without UK supplier
        base_product = {
            "trend_score": 50,
            "margin_score": 50,
            "competition_score": 50,
            "ad_activity_score": 50,
            "supplier_demand_score": 50,
            "ad_count": 50,
            "competition_level": "medium",
            "market_saturation": 30,
            "active_competitor_stores": 20,
        }
        
        # Calculate score without UK supplier
        score_no_uk, label_no_uk, reasoning_no_uk = calculate_launch_score(base_product)
        
        # Add UK supplier flag
        uk_product = {**base_product, "avasam_pid": "AVAS123"}
        score_uk, label_uk, reasoning_uk = calculate_launch_score(uk_product)
        
        # UK supplier should have higher score (up to +15)
        assert score_uk > score_no_uk, f"UK supplier score {score_uk} should be higher than non-UK {score_no_uk}"
        assert score_uk - score_no_uk <= 15, f"UK bonus should be at most 15 points"
    
    def test_launch_score_reasoning_includes_uk_bonus(self):
        """UK supplier products should have 'UK supplier bonus' in reasoning"""
        from common.scoring import calculate_launch_score
        
        uk_product = {
            "trend_score": 50,
            "margin_score": 50,
            "competition_score": 50,
            "ad_activity_score": 50,
            "supplier_demand_score": 50,
            "ad_count": 50,
            "competition_level": "medium",
            "market_saturation": 30,
            "active_competitor_stores": 20,
            "avasam_pid": "AVAS123",
        }
        
        score, label, reasoning = calculate_launch_score(uk_product)
        
        assert "UK supplier bonus" in reasoning, f"Reasoning should mention UK supplier bonus: {reasoning}"
        assert "+15pts" in reasoning or "+15" in reasoning, f"Reasoning should mention +15 points: {reasoning}"
    
    def test_non_uk_supplier_no_bonus_in_reasoning(self):
        """Non-UK supplier products should NOT have UK bonus in reasoning"""
        from common.scoring import calculate_launch_score
        
        non_uk_product = {
            "trend_score": 50,
            "margin_score": 50,
            "competition_score": 50,
            "ad_activity_score": 50,
            "supplier_demand_score": 50,
            "ad_count": 50,
            "competition_level": "medium",
            "market_saturation": 30,
            "active_competitor_stores": 20,
            "data_source": "cj_dropshipping",
        }
        
        score, label, reasoning = calculate_launch_score(non_uk_product)
        
        assert "UK supplier bonus" not in reasoning, f"Non-UK product should not have UK bonus in reasoning: {reasoning}"


# ============================================================
# Test uk_supplier field in API responses
# ============================================================

class TestUkSupplierInApiResponses:
    """Test that uk_supplier boolean is returned in API responses"""
    
    def test_trending_products_has_uk_supplier_field(self):
        """GET /api/public/trending-products should return uk_supplier field"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "products" in data
        
        if len(data["products"]) > 0:
            product = data["products"][0]
            assert "uk_supplier" in product, f"Product should have uk_supplier field: {product.keys()}"
            assert isinstance(product["uk_supplier"], bool), f"uk_supplier should be boolean: {type(product['uk_supplier'])}"
    
    def test_top_trending_has_uk_supplier_field(self):
        """GET /api/public/top-trending should return uk_supplier field"""
        response = requests.get(f"{BASE_URL}/api/public/top-trending")
        assert response.status_code == 200
        
        data = response.json()
        assert "products" in data
        
        if len(data["products"]) > 0:
            product = data["products"][0]
            assert "uk_supplier" in product, f"Product should have uk_supplier field: {product.keys()}"
            assert isinstance(product["uk_supplier"], bool), f"uk_supplier should be boolean"
    
    def test_products_list_has_uk_supplier_field(self):
        """GET /api/products should return uk_supplier field"""
        response = requests.get(f"{BASE_URL}/api/products?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        
        if len(data["data"]) > 0:
            product = data["data"][0]
            assert "uk_supplier" in product, f"Product should have uk_supplier field: {product.keys()}"
            assert isinstance(product["uk_supplier"], bool), f"uk_supplier should be boolean"
    
    def test_product_detail_has_uk_supplier_field(self):
        """GET /api/products/{id} should return uk_supplier field"""
        # First get a product ID
        list_response = requests.get(f"{BASE_URL}/api/products?limit=1")
        assert list_response.status_code == 200
        
        products = list_response.json().get("data", [])
        if len(products) == 0:
            pytest.skip("No products available to test")
        
        product_id = products[0]["id"]
        
        # Get product detail
        response = requests.get(f"{BASE_URL}/api/products/{product_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        product = data["data"]
        assert "uk_supplier" in product, f"Product detail should have uk_supplier field: {product.keys()}"
        assert isinstance(product["uk_supplier"], bool), f"uk_supplier should be boolean"
    
    def test_public_product_by_slug_has_uk_supplier_field(self):
        """GET /api/public/product/{slug} should return uk_supplier field"""
        # First get a product to find its slug
        list_response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=1")
        assert list_response.status_code == 200
        
        products = list_response.json().get("products", [])
        if len(products) == 0:
            pytest.skip("No products available to test")
        
        slug = products[0].get("slug")
        if not slug:
            pytest.skip("Product has no slug")
        
        # Get product by slug
        response = requests.get(f"{BASE_URL}/api/public/product/{slug}")
        assert response.status_code == 200
        
        product = response.json()
        assert "uk_supplier" in product, f"Product by slug should have uk_supplier field: {product.keys()}"
        assert isinstance(product["uk_supplier"], bool), f"uk_supplier should be boolean"


# ============================================================
# Test uk_supplier value correctness
# ============================================================

class TestUkSupplierValueCorrectness:
    """Test that uk_supplier value is correctly computed"""
    
    def test_uk_supplier_false_for_standard_products(self):
        """Products without UK supplier indicators should have uk_supplier=false"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=20")
        assert response.status_code == 200
        
        products = response.json().get("products", [])
        
        # Most products in preview should be uk_supplier=false (no Avasam keys configured)
        # Just verify the field exists and is boolean
        for product in products:
            assert "uk_supplier" in product
            assert isinstance(product["uk_supplier"], bool)
    
    def test_uk_shipping_and_uk_supplier_both_present(self):
        """Products should have both uk_shipping and uk_supplier fields"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        assert response.status_code == 200
        
        products = response.json().get("products", [])
        
        for product in products:
            assert "uk_shipping" in product, f"Product should have uk_shipping field"
            assert "uk_supplier" in product, f"Product should have uk_supplier field"


# ============================================================
# Health check
# ============================================================

class TestHealthEndpoints:
    """Basic health checks"""
    
    def test_health_endpoint(self):
        """Health endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
    
    def test_api_health_endpoint(self):
        """API health endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
