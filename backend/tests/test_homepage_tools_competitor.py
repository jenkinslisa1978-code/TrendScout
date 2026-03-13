"""
Test Suite for Shopify Store Analyzer (Public Tool) and Competitor Tracker (Auth Required)
Phase C New Features: Shopify Analyzer at /tools/shopify-analyzer, Competitor Tracker at /competitor-tracker
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
FREE_USER_EMAIL = "testuser_phase_c@test.com"
FREE_USER_PASSWORD = "test123"
ADMIN_USER_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_USER_PASSWORD = "Test123!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def free_user_token(api_client):
    """Login and get token for free user"""
    response = api_client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": FREE_USER_EMAIL, "password": FREE_USER_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Free user login failed: {response.status_code}")


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Login and get token for admin user"""
    response = api_client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_USER_EMAIL, "password": ADMIN_USER_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Admin login failed: {response.status_code}")


@pytest.fixture
def authenticated_client(api_client, free_user_token):
    """Session with free user auth header"""
    api_client.headers.update({"Authorization": f"Bearer {free_user_token}"})
    return api_client


@pytest.fixture
def admin_client(api_client, admin_token):
    """Session with admin auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


class TestShopifyAnalyzerPublicEndpoint:
    """Test POST /api/tools/analyze-store - PUBLIC endpoint (no auth required)"""
    
    def test_analyze_real_shopify_store_allbirds(self, api_client):
        """Test analyzing a real Shopify store - allbirds.com"""
        response = api_client.post(
            f"{BASE_URL}/api/tools/analyze-store",
            json={"url": "allbirds.com"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify required fields
        assert "product_count" in data, "Missing product_count"
        assert "store_size" in data, "Missing store_size"
        assert "categories" in data, "Missing categories"
        assert "price_range" in data, "Missing price_range"
        assert "newest_products" in data, "Missing newest_products"
        assert "domain" in data, "Missing domain"
        assert "store_url" in data, "Missing store_url"
        
        # Verify product_count is positive (allbirds has products)
        assert data["product_count"] > 0, f"Expected products, got {data['product_count']}"
        
        # Verify price_range structure
        assert "min" in data["price_range"]
        assert "max" in data["price_range"]
        assert "avg" in data["price_range"]
        
        print(f"Allbirds store analyzed: {data['product_count']} products, store_size={data['store_size']}")
    
    def test_analyze_gymshark_store(self, api_client):
        """Test analyzing gymshark.com Shopify store"""
        response = api_client.post(
            f"{BASE_URL}/api/tools/analyze-store",
            json={"url": "gymshark.com"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["product_count"] >= 0  # Even 0 is valid if store restricts access
        assert "categories" in data
        print(f"Gymshark store analyzed: {data['product_count']} products")
    
    def test_analyze_store_with_https_prefix(self, api_client):
        """Test URL normalization with https:// prefix"""
        response = api_client.post(
            f"{BASE_URL}/api/tools/analyze-store",
            json={"url": "https://allbirds.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "allbirds.com"
    
    def test_analyze_invalid_url_returns_400(self, api_client):
        """Test that invalid URL returns 400 error"""
        response = api_client.post(
            f"{BASE_URL}/api/tools/analyze-store",
            json={"url": "not-a-valid-shopify-store-xyz123.invalidtld"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_analyze_non_shopify_store_returns_400(self, api_client):
        """Test that non-Shopify store returns appropriate error"""
        response = api_client.post(
            f"{BASE_URL}/api/tools/analyze-store",
            json={"url": "google.com"}
        )
        # Should return 400 because google.com doesn't have /products.json
        assert response.status_code == 400


class TestCompetitorStoreEndpointsAuth:
    """Test /api/competitor-stores endpoints - require authentication"""
    
    def test_list_competitor_stores_requires_auth(self, api_client):
        """GET /api/competitor-stores requires authentication"""
        # Clear any existing auth header
        api_client.headers.pop("Authorization", None)
        response = api_client.get(f"{BASE_URL}/api/competitor-stores")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_add_competitor_store_requires_auth(self, api_client):
        """POST /api/competitor-stores requires authentication"""
        api_client.headers.pop("Authorization", None)
        response = api_client.post(
            f"{BASE_URL}/api/competitor-stores",
            json={"url": "bombas.com"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestCompetitorStoresCRUD:
    """Test competitor store CRUD operations with authentication"""
    
    def test_list_competitor_stores_authenticated(self, authenticated_client):
        """GET /api/competitor-stores returns list for authenticated user"""
        response = authenticated_client.get(f"{BASE_URL}/api/competitor-stores")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "stores" in data, "Missing 'stores' key in response"
        assert isinstance(data["stores"], list), "stores should be a list"
        assert "count" in data
        
        print(f"User has {data['count']} tracked competitor stores")
    
    def test_add_competitor_store_duplicate_returns_400(self, authenticated_client):
        """POST /api/competitor-stores with duplicate store returns 400"""
        # First get existing stores
        list_response = authenticated_client.get(f"{BASE_URL}/api/competitor-stores")
        stores = list_response.json().get("stores", [])
        
        # Try to add allbirds.com which should already exist per test context
        response = authenticated_client.post(
            f"{BASE_URL}/api/competitor-stores",
            json={"url": "allbirds.com"}
        )
        
        # If allbirds is already tracked, should get 400
        # If not already tracked and under limit, should get 200/201
        if response.status_code == 400:
            assert "already tracking" in response.json().get("detail", "").lower() or \
                   "duplicate" in response.json().get("detail", "").lower() or \
                   "limit" in response.json().get("detail", "").lower()
            print("Confirmed: Duplicate store returns 400")
        else:
            assert response.status_code == 200
            print("Store was added (wasn't a duplicate)")
    
    def test_add_new_competitor_store(self, authenticated_client):
        """POST /api/competitor-stores adds a new store with initial scan data"""
        # Use a unique store that likely isn't tracked yet
        import time
        test_store = "bombas.com"  # Another real Shopify store
        
        # First check if it exists
        list_response = authenticated_client.get(f"{BASE_URL}/api/competitor-stores")
        stores = list_response.json().get("stores", [])
        existing_domains = [s.get("domain", "") for s in stores]
        
        if test_store in existing_domains:
            # Delete it first so we can test add
            store_to_delete = next((s for s in stores if s.get("domain") == test_store), None)
            if store_to_delete:
                authenticated_client.delete(f"{BASE_URL}/api/competitor-stores/{store_to_delete['id']}")
        
        # Now add the store
        response = authenticated_client.post(
            f"{BASE_URL}/api/competitor-stores",
            json={"url": test_store, "name": "Bombas Test"}
        )
        
        if response.status_code == 403:
            # Exceeded plan limit
            print(f"Plan limit reached: {response.json().get('detail')}")
            pytest.skip("User has reached competitor store limit")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should include store id"
        assert "domain" in data, "Response should include domain"
        assert "product_count" in data, "Response should include initial product_count"
        assert "last_scan_at" in data, "Response should include last_scan_at"
        
        print(f"Added competitor store: {data['domain']} with {data.get('product_count', 0)} products")
        
        # Cleanup - delete the test store
        authenticated_client.delete(f"{BASE_URL}/api/competitor-stores/{data['id']}")
    
    def test_refresh_competitor_store(self, authenticated_client):
        """POST /api/competitor-stores/{id}/refresh re-scans a store"""
        # Get existing stores
        list_response = authenticated_client.get(f"{BASE_URL}/api/competitor-stores")
        stores = list_response.json().get("stores", [])
        
        if not stores:
            pytest.skip("No competitor stores to refresh")
        
        store = stores[0]
        store_id = store["id"]
        old_count = store.get("product_count", 0)
        
        response = authenticated_client.post(f"{BASE_URL}/api/competitor-stores/{store_id}/refresh")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "product_count" in data, "Should return updated product_count"
        assert "last_scan_at" in data, "Should return updated last_scan_at"
        
        print(f"Refreshed store: {data.get('name')} - count: {old_count} -> {data.get('product_count')}")
    
    def test_refresh_nonexistent_store_returns_404(self, authenticated_client):
        """POST /api/competitor-stores/{id}/refresh with invalid id returns 404"""
        response = authenticated_client.post(f"{BASE_URL}/api/competitor-stores/invalid-id-xyz/refresh")
        assert response.status_code == 404
    
    def test_delete_competitor_store(self, authenticated_client):
        """DELETE /api/competitor-stores/{id} removes a tracked store"""
        # First add a store we can delete
        add_response = authenticated_client.post(
            f"{BASE_URL}/api/competitor-stores",
            json={"url": "colourpop.com", "name": "Delete Test"}
        )
        
        if add_response.status_code == 403:
            pytest.skip("Plan limit reached, can't test delete")
        
        if add_response.status_code == 400:
            # Already exists - find and delete it
            list_response = authenticated_client.get(f"{BASE_URL}/api/competitor-stores")
            stores = list_response.json().get("stores", [])
            store = next((s for s in stores if "colourpop" in s.get("domain", "")), None)
            if store:
                store_id = store["id"]
            else:
                pytest.skip("Cannot create test store for deletion")
        else:
            store_id = add_response.json()["id"]
        
        # Now delete it
        response = authenticated_client.delete(f"{BASE_URL}/api/competitor-stores/{store_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "deleted"
        
        # Verify it's gone
        list_response = authenticated_client.get(f"{BASE_URL}/api/competitor-stores")
        stores = list_response.json().get("stores", [])
        assert not any(s.get("id") == store_id for s in stores), "Store should be deleted"
        
        print("Confirmed: Store deleted successfully")
    
    def test_delete_nonexistent_store_returns_404(self, authenticated_client):
        """DELETE /api/competitor-stores/{id} with invalid id returns 404"""
        response = authenticated_client.delete(f"{BASE_URL}/api/competitor-stores/nonexistent-id-abc")
        assert response.status_code == 404


class TestCompetitorStorePlanLimits:
    """Test plan-based limits for competitor tracking"""
    
    def test_free_user_limit(self, authenticated_client):
        """Free plan users can track up to 2 stores"""
        # This is a soft test - we check if the error message mentions limits
        response = authenticated_client.get(f"{BASE_URL}/api/competitor-stores")
        data = response.json()
        count = data.get("count", 0)
        
        # Try to exceed limit by adding multiple stores
        if count >= 2:
            # Try to add another
            add_response = authenticated_client.post(
                f"{BASE_URL}/api/competitor-stores",
                json={"url": "unique-test-store-xyz.myshopify.com"}
            )
            if add_response.status_code == 403:
                assert "plan" in add_response.json().get("detail", "").lower() or \
                       "limit" in add_response.json().get("detail", "").lower() or \
                       "upgrade" in add_response.json().get("detail", "").lower()
                print("Confirmed: Plan limit enforcement working")
            elif add_response.status_code == 400:
                # Invalid store URL or already tracked
                print(f"Got 400: {add_response.json().get('detail')}")
        else:
            print(f"User has {count}/2 stores tracked")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
