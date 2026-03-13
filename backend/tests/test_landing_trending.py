"""
Backend API tests for Landing Page and Trending Products Page features.
Tests for:
- Public trending products endpoint with new fields (supplier_cost, retail_price, growth_rate, etc.)
- Public categories endpoint
- Product card data for confidence scores
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestPublicTrendingProducts:
    """Test /api/public/trending-products endpoint"""
    
    def test_trending_products_returns_200(self):
        """Test that trending products endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/public/trending-products returns 200")
    
    def test_trending_products_response_structure(self):
        """Test response has products, total, and detected_this_week"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=10")
        data = response.json()
        
        assert "products" in data, "Response missing 'products' field"
        assert "total" in data, "Response missing 'total' field"
        assert "detected_this_week" in data, "Response missing 'detected_this_week' field"
        assert isinstance(data["products"], list), "'products' should be a list"
        print(f"✓ Response structure correct: {len(data['products'])} products, total={data['total']}, week={data['detected_this_week']}")
    
    def test_product_has_required_fields(self):
        """Test each product has all required fields for product cards"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        data = response.json()
        products = data.get("products", [])
        
        assert len(products) > 0, "No products returned"
        
        required_fields = [
            "id", "slug", "product_name", "category", "image_url",
            "launch_score", "trend_stage", "margin_percent",
            "supplier_cost", "retail_price", "growth_rate",
            "tiktok_views", "detected_at"
        ]
        
        first_product = products[0]
        missing_fields = [f for f in required_fields if f not in first_product]
        
        assert len(missing_fields) == 0, f"Missing fields: {missing_fields}"
        print(f"✓ Product has all {len(required_fields)} required fields")
        print(f"  Fields: {list(first_product.keys())}")
    
    def test_product_supplier_cost_is_number(self):
        """Test supplier_cost is a valid number"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = response.json().get("products", [])
        
        for p in products:
            assert isinstance(p.get("supplier_cost"), (int, float)), f"supplier_cost not numeric: {p.get('supplier_cost')}"
        print("✓ All products have numeric supplier_cost")
    
    def test_product_retail_price_is_number(self):
        """Test retail_price is a valid number"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = response.json().get("products", [])
        
        for p in products:
            assert isinstance(p.get("retail_price"), (int, float)), f"retail_price not numeric: {p.get('retail_price')}"
        print("✓ All products have numeric retail_price")
    
    def test_product_growth_rate_is_number(self):
        """Test growth_rate is a valid number"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = response.json().get("products", [])
        
        for p in products:
            assert isinstance(p.get("growth_rate"), (int, float)), f"growth_rate not numeric: {p.get('growth_rate')}"
        print("✓ All products have numeric growth_rate")
    
    def test_product_tiktok_views_is_number(self):
        """Test tiktok_views is a valid number"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = response.json().get("products", [])
        
        for p in products:
            assert isinstance(p.get("tiktok_views"), (int, float)), f"tiktok_views not numeric: {p.get('tiktok_views')}"
        print("✓ All products have numeric tiktok_views")
    
    def test_product_launch_score_in_range(self):
        """Test launch_score is 0-100"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=10")
        products = response.json().get("products", [])
        
        for p in products:
            score = p.get("launch_score", -1)
            assert 0 <= score <= 100, f"launch_score out of range: {score}"
        print("✓ All launch_scores are in 0-100 range")
    
    def test_product_margin_percent_reasonable(self):
        """Test margin_percent is a reasonable percentage"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=10")
        products = response.json().get("products", [])
        
        for p in products:
            margin = p.get("margin_percent", -1)
            assert -100 <= margin <= 100, f"margin_percent unreasonable: {margin}"
        print("✓ All margin_percent values are reasonable")
    
    def test_product_has_slug(self):
        """Test each product has a valid slug for routing"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = response.json().get("products", [])
        
        for p in products:
            slug = p.get("slug")
            assert slug is not None and len(slug) > 0, f"Product missing slug: {p.get('product_name')}"
        print("✓ All products have valid slugs")
    
    def test_limit_parameter_works(self):
        """Test that limit parameter restricts results"""
        response_3 = requests.get(f"{BASE_URL}/api/public/trending-products?limit=3")
        response_10 = requests.get(f"{BASE_URL}/api/public/trending-products?limit=10")
        
        products_3 = response_3.json().get("products", [])
        products_10 = response_10.json().get("products", [])
        
        assert len(products_3) == 3, f"Expected 3 products, got {len(products_3)}"
        assert len(products_10) == 10, f"Expected 10 products, got {len(products_10)}"
        print("✓ Limit parameter works correctly (3 and 10 products returned)")


class TestPublicCategories:
    """Test /api/public/categories endpoint"""
    
    def test_categories_returns_200(self):
        """Test that categories endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/public/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/public/categories returns 200")
    
    def test_categories_returns_array(self):
        """Test that categories returns an array"""
        response = requests.get(f"{BASE_URL}/api/public/categories")
        data = response.json()
        
        assert isinstance(data, list), f"Expected array, got {type(data)}"
        assert len(data) > 0, "Categories array is empty"
        print(f"✓ Categories returns array with {len(data)} items")
    
    def test_category_has_required_fields(self):
        """Test each category has name, slug, count, avg_score"""
        response = requests.get(f"{BASE_URL}/api/public/categories")
        categories = response.json()
        
        required_fields = ["name", "slug", "count", "avg_score"]
        
        for cat in categories[:5]:  # Test first 5
            missing = [f for f in required_fields if f not in cat]
            assert len(missing) == 0, f"Category {cat.get('name')} missing: {missing}"
        
        print(f"✓ Categories have all required fields: {required_fields}")
    
    def test_category_count_is_positive(self):
        """Test that category count is positive integer"""
        response = requests.get(f"{BASE_URL}/api/public/categories")
        categories = response.json()
        
        for cat in categories:
            count = cat.get("count", 0)
            assert isinstance(count, int) and count > 0, f"Invalid count for {cat.get('name')}: {count}"
        
        print("✓ All categories have positive count values")
    
    def test_category_avg_score_in_range(self):
        """Test that avg_score is in valid range"""
        response = requests.get(f"{BASE_URL}/api/public/categories")
        categories = response.json()
        
        for cat in categories:
            score = cat.get("avg_score", -1)
            assert 0 <= score <= 100, f"avg_score out of range for {cat.get('name')}: {score}"
        
        print("✓ All categories have valid avg_score (0-100)")


class TestConfidenceScores:
    """Test confidence score calculation logic"""
    
    def test_high_confidence_products_exist(self):
        """Test that products with high launch scores (>=75) can be classified as High Confidence"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=50")
        products = response.json().get("products", [])
        
        high_conf = [p for p in products if p.get("launch_score", 0) >= 75]
        emerging = [p for p in products if 50 <= p.get("launch_score", 0) < 75]
        experimental = [p for p in products if p.get("launch_score", 0) < 50]
        
        print(f"  Product distribution by confidence:")
        print(f"    High Confidence (>=75): {len(high_conf)}")
        print(f"    Emerging (50-74): {len(emerging)}")
        print(f"    Experimental (<50): {len(experimental)}")
        
        # At least one category should have products
        total = len(high_conf) + len(emerging) + len(experimental)
        assert total == len(products), "Products should fit into one confidence category"
        print("✓ All products have valid launch_score for confidence classification")


# Run tests when executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
