"""
Test Product Comparison API endpoints.
Tests: POST /api/compare/quick, POST /api/compare, GET /api/compare/shared/{share_id},
       GET /api/compare/my, DELETE /api/compare/{share_id}
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "reviewer@trendscout.click"
ADMIN_PASSWORD = "ShopifyReview2026!"
DEMO_EMAIL = "demo@trendscout.click"
DEMO_PASSWORD = "DemoReview2026!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def product_ids(api_client):
    """Get 3 product IDs from trending products for testing"""
    response = api_client.get(f"{BASE_URL}/api/public/trending-products?limit=10")
    assert response.status_code == 200, f"Failed to get trending products: {response.text}"
    data = response.json()
    products = data.get("products", [])
    assert len(products) >= 3, f"Need at least 3 products for testing, got {len(products)}"
    return [p["id"] for p in products[:3]]


@pytest.fixture(scope="module")
def auth_session():
    """Get authenticated session with CSRF token for demo user"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.text}")
    
    data = response.json()
    token = data.get("access_token") or data.get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Get CSRF token from cookies
    csrf_token = session.cookies.get("__Host-csrf")
    if csrf_token:
        session.headers.update({"x-csrf-token": csrf_token})
    
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token for demo user"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Authentication failed: {response.text}")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    # Get CSRF token from cookies
    csrf_token = api_client.cookies.get("__Host-csrf")
    if csrf_token:
        api_client.headers.update({"x-csrf-token": csrf_token})
    return api_client


class TestHealthCheck:
    """Verify API is accessible"""
    
    def test_health_check(self, api_client):
        """Health check endpoint should return ok"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: Health check returns ok")


class TestQuickCompare:
    """Test POST /api/compare/quick - no auth required"""
    
    def test_quick_compare_success(self, api_client, product_ids):
        """Quick compare with 2 products should return product data"""
        response = api_client.post(f"{BASE_URL}/api/compare/quick", json={
            "product_ids": product_ids[:2]
        })
        assert response.status_code == 200, f"Quick compare failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "products" in data
        assert len(data["products"]) == 2
        # Verify product data structure
        for p in data["products"]:
            assert "id" in p
            assert "product_name" in p
            assert "launch_score" in p or "metrics" in p
        print(f"PASS: Quick compare returns {len(data['products'])} products")
    
    def test_quick_compare_with_3_products(self, api_client, product_ids):
        """Quick compare with 3 products should work"""
        response = api_client.post(f"{BASE_URL}/api/compare/quick", json={
            "product_ids": product_ids[:3]
        })
        assert response.status_code == 200, f"Quick compare with 3 products failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert len(data["products"]) == 3
        print("PASS: Quick compare with 3 products works")
    
    def test_quick_compare_too_few_products(self, api_client, product_ids):
        """Quick compare with 1 product should fail"""
        response = api_client.post(f"{BASE_URL}/api/compare/quick", json={
            "product_ids": [product_ids[0]]
        })
        assert response.status_code == 400, f"Expected 400 for 1 product, got {response.status_code}"
        print("PASS: Quick compare rejects 1 product (needs 2-4)")
    
    def test_quick_compare_too_many_products(self, api_client, product_ids):
        """Quick compare with 5 products should fail"""
        # Create 5 IDs (duplicate if needed)
        five_ids = product_ids + product_ids[:2]
        response = api_client.post(f"{BASE_URL}/api/compare/quick", json={
            "product_ids": five_ids
        })
        assert response.status_code == 400, f"Expected 400 for 5 products, got {response.status_code}"
        print("PASS: Quick compare rejects 5 products (needs 2-4)")
    
    def test_quick_compare_invalid_product_id(self, api_client):
        """Quick compare with invalid product ID should fail"""
        response = api_client.post(f"{BASE_URL}/api/compare/quick", json={
            "product_ids": ["invalid-id-1", "invalid-id-2"]
        })
        assert response.status_code == 404, f"Expected 404 for invalid IDs, got {response.status_code}"
        print("PASS: Quick compare returns 404 for invalid product IDs")


class TestSavedComparison:
    """Test POST /api/compare - requires auth"""
    
    def test_create_comparison_no_auth(self, api_client, product_ids):
        """Creating comparison without auth should fail"""
        # Remove auth header if present
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BASE_URL}/api/compare", json={
            "product_ids": product_ids[:2],
            "title": "Test Comparison"
        }, headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("PASS: Create comparison requires authentication")
    
    def test_create_comparison_success(self, auth_session, product_ids):
        """Creating comparison with auth should return share_id"""
        response = auth_session.post(f"{BASE_URL}/api/compare", json={
            "product_ids": product_ids[:2],
            "title": "TEST_Comparison"
        })
        assert response.status_code == 200, f"Create comparison failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "share_id" in data
        assert "comparison" in data
        assert len(data["share_id"]) == 8  # UUID[:8]
        print(f"PASS: Created comparison with share_id: {data['share_id']}")
        return data["share_id"]
    
    def test_create_comparison_validates_product_count(self, auth_session, product_ids):
        """Creating comparison with 1 product should fail"""
        response = auth_session.post(f"{BASE_URL}/api/compare", json={
            "product_ids": [product_ids[0]],
            "title": "Invalid Comparison"
        })
        assert response.status_code == 400, f"Expected 400 for 1 product, got {response.status_code}"
        print("PASS: Create comparison validates 2-4 products required")


class TestSharedComparison:
    """Test GET /api/compare/shared/{share_id} - public, no auth"""
    
    @pytest.fixture(scope="class")
    def created_share_id(self, auth_session, product_ids):
        """Create a comparison and return its share_id"""
        response = auth_session.post(f"{BASE_URL}/api/compare", json={
            "product_ids": product_ids[:2],
            "title": "TEST_Shared_Comparison"
        })
        assert response.status_code == 200, f"Failed to create comparison: {response.text}"
        return response.json()["share_id"]
    
    def test_get_shared_comparison_success(self, api_client, created_share_id):
        """Getting shared comparison should work without auth"""
        # Use fresh client without auth
        response = requests.get(f"{BASE_URL}/api/compare/shared/{created_share_id}")
        assert response.status_code == 200, f"Get shared comparison failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "comparison" in data
        assert data["comparison"]["share_id"] == created_share_id
        assert "products" in data["comparison"]
        assert len(data["comparison"]["products"]) >= 2
        print(f"PASS: Shared comparison {created_share_id} accessible publicly")
    
    def test_get_shared_comparison_not_found(self, api_client):
        """Getting non-existent share_id should return 404"""
        response = requests.get(f"{BASE_URL}/api/compare/shared/notfound")
        assert response.status_code == 404, f"Expected 404 for invalid share_id, got {response.status_code}"
        print("PASS: Non-existent share_id returns 404")


class TestMyComparisons:
    """Test GET /api/compare/my - requires auth"""
    
    def test_list_my_comparisons_no_auth(self, api_client):
        """Listing comparisons without auth should fail"""
        response = requests.get(f"{BASE_URL}/api/compare/my")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("PASS: List my comparisons requires authentication")
    
    def test_list_my_comparisons_success(self, auth_session):
        """Listing comparisons with auth should return array"""
        response = auth_session.get(f"{BASE_URL}/api/compare/my")
        assert response.status_code == 200, f"List my comparisons failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "comparisons" in data
        assert isinstance(data["comparisons"], list)
        print(f"PASS: List my comparisons returns {len(data['comparisons'])} comparisons")


class TestDeleteComparison:
    """Test DELETE /api/compare/{share_id} - requires auth"""
    
    @pytest.fixture(scope="class")
    def comparison_to_delete(self, auth_session, product_ids):
        """Create a comparison to delete"""
        response = auth_session.post(f"{BASE_URL}/api/compare", json={
            "product_ids": product_ids[:2],
            "title": "TEST_To_Delete"
        })
        assert response.status_code == 200, f"Failed to create comparison: {response.text}"
        return response.json()["share_id"]
    
    def test_delete_comparison_no_auth(self, api_client, comparison_to_delete):
        """Deleting comparison without auth should fail"""
        response = requests.delete(f"{BASE_URL}/api/compare/{comparison_to_delete}")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("PASS: Delete comparison requires authentication")
    
    def test_delete_comparison_success(self, auth_session, comparison_to_delete):
        """Deleting comparison with auth should succeed"""
        response = auth_session.delete(f"{BASE_URL}/api/compare/{comparison_to_delete}")
        assert response.status_code == 200, f"Delete comparison failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print(f"PASS: Deleted comparison {comparison_to_delete}")
        
        # Verify it's actually deleted
        verify_response = requests.get(f"{BASE_URL}/api/compare/shared/{comparison_to_delete}")
        assert verify_response.status_code == 404, "Deleted comparison should not be accessible"
        print("PASS: Deleted comparison no longer accessible")
    
    def test_delete_nonexistent_comparison(self, auth_session):
        """Deleting non-existent comparison should return 404"""
        response = auth_session.delete(f"{BASE_URL}/api/compare/notfound")
        assert response.status_code == 404, f"Expected 404 for non-existent comparison, got {response.status_code}"
        print("PASS: Delete non-existent comparison returns 404")


class TestSSRRegression:
    """Regression test: SSR for /trending-products should still work"""
    
    def test_ssr_trending_products(self, api_client):
        """Crawler request to /trending-products should return SSR content"""
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        }
        response = requests.get(f"{BASE_URL}/trending-products", headers=headers)
        assert response.status_code == 200, f"SSR request failed: {response.status_code}"
        # Check for SSR content markers
        content = response.text
        has_ssr = "ssr-content" in content or "<article" in content or "product" in content.lower()
        print(f"PASS: SSR for /trending-products returns content (has_ssr_markers: {has_ssr})")
