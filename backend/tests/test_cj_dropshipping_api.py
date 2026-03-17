"""
CJ Dropshipping API Integration Tests
Tests for:
- GET /api/cj/search - Search products from CJ Dropshipping
- GET /api/cj/product/{pid} - Get product detail from CJ
- POST /api/cj/import/{pid} - Import CJ product into TrendScout
- GET /api/cj/categories - Get CJ product categories

NOTE: CJ API has strict rate limits (1 request per second). Tests include delays.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# CJ API rate limit - add delay between requests
def cj_rate_limit_delay():
    time.sleep(2)


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for protected endpoints"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "jenkinslisa1978@gmail.com",
        "password": "admin123456"
    })
    if response.status_code == 200:
        data = response.json()
        # Token can be in 'token' or 'access_token' field
        return data.get("token") or data.get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def auth_headers(auth_token):
    """Return authorization headers"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestCJSearchEndpoint:
    """Tests for GET /api/cj/search - CJ Dropshipping product search"""
    
    def test_search_requires_auth(self):
        """Search endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cj/search?q=phone+case")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ CJ search requires authentication")
    
    def test_search_returns_products(self, auth_headers):
        """Search returns products with correct fields"""
        response = requests.get(
            f"{BASE_URL}/api/cj/search?q=phone+case&page=1&page_size=10",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Check response structure
        assert "products" in data, "Response should have 'products' field"
        assert "success" in data, "Response should have 'success' field"
        assert "total" in data, "Response should have 'total' field"
        
        if data["products"]:
            product = data["products"][0]
            # Verify required fields
            assert "cj_pid" in product, "Product should have cj_pid"
            assert "product_name" in product, "Product should have product_name"
            assert "sell_price" in product, "Product should have sell_price"
            assert "image_url" in product, "Product should have image_url"
            assert "category" in product, "Product should have category"
            assert "stock_status" in product, "Product should have stock_status"
            print(f"✓ CJ search returned {len(data['products'])} products, total: {data['total']}")
            print(f"  Sample product: {product['product_name'][:50]}... (${product['sell_price']})")
        else:
            print("✓ CJ search returned empty results (query may have no matches)")
    
    def test_search_requires_query(self, auth_headers):
        """Search requires query parameter with minimum length"""
        response = requests.get(f"{BASE_URL}/api/cj/search", headers=auth_headers)
        # Should fail validation - query is required
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("✓ CJ search validates query parameter required")
    
    def test_search_pagination(self, auth_headers):
        """Search supports pagination parameters"""
        cj_rate_limit_delay()
        response = requests.get(
            f"{BASE_URL}/api/cj/search?q=led+light&page=2&page_size=5",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # Rate limit may occur - handle gracefully
        if data.get("success") is False and "rate" in str(data.get("error", "")).lower():
            print("✓ CJ search pagination: Rate limited (expected behavior)")
            return
        assert "page" in data, "Response should have 'page' field"
        assert "page_size" in data, "Response should have 'page_size' field"
        print(f"✓ CJ search pagination works: page={data.get('page')}, page_size={data.get('page_size')}")


class TestCJProductDetailEndpoint:
    """Tests for GET /api/cj/product/{pid} - CJ Dropshipping product detail"""
    
    @pytest.fixture
    def sample_pid(self, auth_headers):
        """Get a sample product ID from search results"""
        response = requests.get(
            f"{BASE_URL}/api/cj/search?q=phone+case&page=1&page_size=1",
            headers=auth_headers
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("products"):
                return data["products"][0]["cj_pid"]
        pytest.skip("Could not get sample product ID from search")
    
    def test_product_detail_requires_auth(self):
        """Product detail endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cj/product/test123")
        assert response.status_code == 401
        print("✓ CJ product detail requires authentication")
    
    def test_product_detail_returns_full_data(self, auth_headers, sample_pid):
        """Product detail returns complete product information"""
        response = requests.get(
            f"{BASE_URL}/api/cj/product/{sample_pid}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "success" in data
        assert data["success"] is True
        assert "product" in data
        
        product = data["product"]
        # Verify detailed fields
        assert "cj_pid" in product
        assert "product_name" in product
        assert "sell_price" in product
        assert "category" in product
        assert "image_url" in product or "images" in product
        assert "source_url" in product
        
        # Check for variants if available
        if "variants" in product:
            print(f"✓ Product has {len(product['variants'])} variants")
            if product["variants"]:
                variant = product["variants"][0]
                assert "price" in variant, "Variant should have price"
        
        # Check for properties if available
        if "properties" in product:
            print(f"✓ Product has {len(product['properties'])} properties")
        
        print(f"✓ CJ product detail returned: {product['product_name'][:50]}...")
        print(f"  Price: ${product['sell_price']}, Category: {product.get('category', 'N/A')}")
    
    def test_product_detail_invalid_pid(self, auth_headers):
        """Product detail returns 404 for invalid product ID"""
        response = requests.get(
            f"{BASE_URL}/api/cj/product/invalid_pid_12345",
            headers=auth_headers
        )
        assert response.status_code in [404, 400], f"Expected 404/400, got {response.status_code}"
        print("✓ CJ product detail handles invalid PID correctly")


class TestCJImportEndpoint:
    """Tests for POST /api/cj/import/{pid} - Import CJ product to TrendScout"""
    
    @pytest.fixture
    def sample_pid_for_import(self, auth_headers):
        """Get a sample product ID for import testing"""
        cj_rate_limit_delay()
        response = requests.get(
            f"{BASE_URL}/api/cj/search?q=yoga+mat&page=1&page_size=1",
            headers=auth_headers
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("products"):
                return data["products"][0]["cj_pid"]
        pytest.skip("Could not get sample product ID for import")
    
    def test_import_requires_auth(self):
        """Import endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/cj/import/test123")
        assert response.status_code == 401
        print("✓ CJ import requires authentication")
    
    def test_import_creates_product(self, auth_headers, sample_pid_for_import):
        """Import creates a product in TrendScout with launch score"""
        cj_rate_limit_delay()
        response = requests.post(
            f"{BASE_URL}/api/cj/import/{sample_pid_for_import}",
            headers=auth_headers
        )
        # Handle rate limit
        if response.status_code == 404 and "rate" in response.text.lower():
            print("✓ CJ import: Rate limited (expected behavior)")
            pytest.skip("CJ API rate limited")
            return
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        data = response.json()
        
        assert "success" in data
        assert data["success"] is True
        assert "product_id" in data, "Response should have product_id"
        
        # Check for launch score
        if "launch_score" in data:
            assert isinstance(data["launch_score"], (int, float))
            print(f"✓ CJ import successful: product_id={data['product_id']}, launch_score={data['launch_score']}")
        else:
            print(f"✓ CJ import successful: product_id={data['product_id']}")
        
        # Check if product already existed
        if data.get("already_existed"):
            print("  (Product was already imported)")
        else:
            print("  (New product created)")
        
        return data["product_id"]
    
    def test_import_same_product_twice(self, auth_headers, sample_pid_for_import):
        """Importing same product twice should indicate already exists"""
        cj_rate_limit_delay()
        # First import
        response1 = requests.post(
            f"{BASE_URL}/api/cj/import/{sample_pid_for_import}",
            headers=auth_headers
        )
        if response1.status_code == 404 and "rate" in response1.text.lower():
            pytest.skip("CJ API rate limited")
        assert response1.status_code == 200
        
        cj_rate_limit_delay()
        # Second import
        response2 = requests.post(
            f"{BASE_URL}/api/cj/import/{sample_pid_for_import}",
            headers=auth_headers
        )
        if response2.status_code == 404 and "rate" in response2.text.lower():
            pytest.skip("CJ API rate limited")
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert data2.get("already_existed") is True, "Second import should indicate already_existed"
        print("✓ CJ import handles duplicate imports correctly")


class TestCJCategoriesEndpoint:
    """Tests for GET /api/cj/categories - CJ Dropshipping categories"""
    
    def test_categories_requires_auth(self):
        """Categories endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cj/categories")
        assert response.status_code == 401
        print("✓ CJ categories requires authentication")
    
    def test_categories_returns_list(self, auth_headers):
        """Categories returns list of CJ categories"""
        response = requests.get(
            f"{BASE_URL}/api/cj/categories",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "categories" in data, "Response should have 'categories' field"
        
        if data["categories"]:
            category = data["categories"][0]
            assert "id" in category, "Category should have id"
            assert "name" in category, "Category should have name"
            print(f"✓ CJ categories returned {len(data['categories'])} categories")
            print(f"  Sample: {category['name']} (ID: {category['id']})")
        else:
            print("✓ CJ categories endpoint works (no categories returned)")


class TestImportedProductIntegration:
    """Tests for verifying imported products show CJ Dropshipping source"""
    
    def test_imported_product_has_cj_source(self, auth_headers):
        """Imported products should have data_source='cj_dropshipping'"""
        cj_rate_limit_delay()
        # Search for a product first
        search_response = requests.get(
            f"{BASE_URL}/api/cj/search?q=phone+case&page=1&page_size=1",
            headers=auth_headers
        )
        if search_response.status_code != 200 or not search_response.json().get("products"):
            pytest.skip("Could not get sample product")
        
        cj_pid = search_response.json()["products"][0]["cj_pid"]
        
        cj_rate_limit_delay()
        # Import the product
        import_response = requests.post(
            f"{BASE_URL}/api/cj/import/{cj_pid}",
            headers=auth_headers
        )
        if import_response.status_code == 404 and "rate" in import_response.text.lower():
            pytest.skip("CJ API rate limited")
        assert import_response.status_code == 200
        product_id = import_response.json()["product_id"]
        
        # Fetch the product from TrendScout
        product_response = requests.get(
            f"{BASE_URL}/api/products/{product_id}",
            headers=auth_headers
        )
        assert product_response.status_code == 200
        response_data = product_response.json()
        
        # Product may be nested in 'data' field
        product = response_data.get("data") if "data" in response_data else response_data
        
        assert product.get("data_source") == "cj_dropshipping", f"Product should have data_source='cj_dropshipping', got {product.get('data_source')}"
        assert product.get("cj_pid") == cj_pid, "Product should have cj_pid field"
        print(f"✓ Imported product has correct CJ source: {product['product_name'][:40]}...")
        print(f"  data_source: {product['data_source']}, cj_pid: {product['cj_pid']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
