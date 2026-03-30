"""
Iteration 89 Feature Tests
Tests: Ad Tests page, Data Transparency, TikTok links, Admin Images Stats
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://uk-warehouse-spy.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "admin123456"
SAMPLE_PRODUCT_ID = "2f40b4e2-912f-40b3-890d-f60510f50d8d"


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for admin user"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed")


class TestAdminImagesEndpoint:
    """Test GET /api/admin/images/stats endpoint"""
    
    def test_images_stats_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/images/stats")
        assert response.status_code == 401
        print("SUCCESS: Admin images stats requires auth (401)")
    
    def test_images_stats_returns_data(self, auth_token):
        """Test that endpoint returns image statistics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/images/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected fields
        assert "total_products" in data
        assert "with_images" in data
        assert "without_images" in data
        
        # Verify values are integers
        assert isinstance(data["total_products"], int)
        assert isinstance(data["with_images"], int)
        assert isinstance(data["without_images"], int)
        
        print(f"SUCCESS: Images stats - total: {data['total_products']}, with images: {data['with_images']}, without: {data['without_images']}")


class TestAdTestsEndpoint:
    """Test GET /api/ad-tests/my endpoint"""
    
    def test_ad_tests_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/my")
        assert response.status_code == 401
        print("SUCCESS: Ad tests requires auth (401)")
    
    def test_ad_tests_returns_data(self, auth_token):
        """Test that endpoint returns ad tests list"""
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/my",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected structure
        assert "tests" in data
        assert isinstance(data["tests"], list)
        
        print(f"SUCCESS: Ad tests returned {len(data['tests'])} tests")
        
        # If tests exist, verify structure
        if data["tests"]:
            test = data["tests"][0]
            assert "id" in test
            assert "status" in test
            print(f"  First test: {test.get('product_name', 'N/A')} - status: {test['status']}")


class TestTikTokIntelligenceEndpoint:
    """Test GET /api/tools/tiktok-intelligence endpoint"""
    
    def test_tiktok_intelligence_returns_data(self):
        """Test that endpoint returns TikTok intelligence data"""
        response = requests.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected structure
        assert "viral_products" in data
        assert "categories" in data
        assert "stats" in data
        
        print(f"SUCCESS: TikTok intelligence returned {len(data['viral_products'])} viral products")
    
    def test_tiktok_viral_products_have_ids(self):
        """Test that viral products have proper IDs for linking"""
        response = requests.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all viral products have IDs (not just slugs)
        for product in data.get("viral_products", [])[:5]:
            assert "id" in product
            # ID should be UUID format
            assert len(product["id"]) == 36
            print(f"  Product ID: {product['id']} - {product.get('product_name', 'N/A')}")
        
        print("SUCCESS: All viral products have proper UUIDs for linking")


class TestProductEndpoints:
    """Test product-related endpoints"""
    
    def test_product_detail_returns_data(self):
        """Test that product detail endpoint works"""
        response = requests.get(f"{BASE_URL}/api/products/{SAMPLE_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected structure
        assert "data" in data
        product = data["data"]
        assert "product_name" in product
        assert "id" in product
        
        print(f"SUCCESS: Product detail - {product['product_name']}")
    
    def test_product_has_supplier_info(self):
        """Test that product has supplier information"""
        response = requests.get(f"{BASE_URL}/api/products/{SAMPLE_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        product = data["data"]
        
        # Check for supplier info
        assert "suppliers" in product or "supplier_cost" in product
        
        if "suppliers" in product and product["suppliers"]:
            supplier = product["suppliers"][0]
            print(f"SUCCESS: Product has supplier - {supplier.get('name', 'N/A')}, {supplier.get('country', 'N/A')}")
        else:
            print(f"INFO: Product has supplier_cost: {product.get('supplier_cost')}")


class TestRoutesAccessibility:
    """Test that all required routes are accessible"""
    
    def test_discover_route(self, auth_token):
        """Test /discover page loads (via API check)"""
        response = requests.get(f"{BASE_URL}/api/products?limit=1")
        assert response.status_code == 200
        print("SUCCESS: /api/products works (discover page backend)")
    
    def test_ad_tests_route(self, auth_token):
        """Test /ad-tests page loads (via API check)"""
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/my",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print("SUCCESS: /api/ad-tests/my works (ad-tests page backend)")
    
    def test_tiktok_route(self):
        """Test /tiktok-intelligence page loads (via API check)"""
        response = requests.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        assert response.status_code == 200
        print("SUCCESS: /api/tools/tiktok-intelligence works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
