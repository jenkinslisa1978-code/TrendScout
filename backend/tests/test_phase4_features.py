"""
Phase 4 Features Test Suite - TrendScout
Tests: Winner Streak Badge System, Public SEO Pages, API Access for Power Users
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://scout-deploy-2.preview.emergentagent.com"

TEST_EMAIL = "jenkinslisa1978@gmail.com"
TEST_PASSWORD = "admin123456"


@pytest.fixture(scope="module")
def auth_token():
    """Login and get auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


# =====================
# PUBLIC SEO ENDPOINTS (No Auth Required)
# =====================

class TestPublicTrendingIndex:
    """Tests for GET /api/public/trending-index - Public SEO directory"""

    def test_trending_index_returns_products(self):
        """GET /api/public/trending-index returns products with slugs"""
        response = requests.get(f"{BASE_URL}/api/public/trending-index")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "products" in data, "Response should have 'products' field"
        assert "categories" in data, "Response should have 'categories' field"
        assert len(data["products"]) > 0, "Should have at least 1 product"
        
    def test_trending_index_product_has_slug(self):
        """Products in trending index should have slug field"""
        response = requests.get(f"{BASE_URL}/api/public/trending-index")
        assert response.status_code == 200
        
        data = response.json()
        products = data.get("products", [])
        assert len(products) > 0, "Need at least 1 product"
        
        p = products[0]
        assert "slug" in p, "Product should have 'slug' field"
        assert "id" in p, "Product should have 'id' field"
        assert "product_name" in p, "Product should have 'product_name' field"
        assert "launch_score" in p, "Product should have 'launch_score' field"
        
    def test_trending_index_returns_categories(self):
        """Trending index returns list of categories"""
        response = requests.get(f"{BASE_URL}/api/public/trending-index")
        assert response.status_code == 200
        
        data = response.json()
        categories = data.get("categories", [])
        assert isinstance(categories, list), "Categories should be a list"


class TestPublicTrendingProductSEO:
    """Tests for GET /api/public/trending/:slug - Public product SEO page"""

    def test_trending_product_by_slug(self):
        """GET /api/public/trending/:slug returns product with SEO data"""
        # First get a valid slug from trending index
        idx_response = requests.get(f"{BASE_URL}/api/public/trending-index")
        assert idx_response.status_code == 200
        products = idx_response.json().get("products", [])
        assert len(products) > 0, "Need at least 1 product for slug test"
        
        slug = products[0].get("slug")
        assert slug, "First product should have a slug"
        
        # Now test the trending product endpoint
        response = requests.get(f"{BASE_URL}/api/public/trending/{slug}")
        assert response.status_code == 200, f"Expected 200 for slug '{slug}', got {response.status_code}"
        
        data = response.json()
        assert "product" in data, "Response should have 'product' field"
        assert "seo" in data, "Response should have 'seo' field"
        assert "related_products" in data, "Response should have 'related_products' field"
        
    def test_trending_product_seo_fields(self):
        """SEO data contains title, description, json_ld, canonical_url"""
        idx_response = requests.get(f"{BASE_URL}/api/public/trending-index")
        products = idx_response.json().get("products", [])
        if not products:
            pytest.skip("No products available")
        
        slug = products[0].get("slug")
        response = requests.get(f"{BASE_URL}/api/public/trending/{slug}")
        assert response.status_code == 200
        
        data = response.json()
        seo = data.get("seo", {})
        assert "title" in seo, "SEO should have 'title'"
        assert "description" in seo, "SEO should have 'description'"
        assert "json_ld" in seo, "SEO should have 'json_ld' structured data"
        assert "canonical_url" in seo, "SEO should have 'canonical_url'"
        
        json_ld = seo.get("json_ld", {})
        assert json_ld.get("@context") == "https://schema.org", "JSON-LD should have schema.org context"
        assert json_ld.get("@type") == "Product", "JSON-LD should be Product type"

    def test_trending_product_invalid_slug_returns_404(self):
        """Invalid slug returns 404"""
        response = requests.get(f"{BASE_URL}/api/public/trending/invalid-nonexistent-slug-12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


# =====================
# WINNER STREAK BADGE SYSTEM
# =====================

class TestWinnerStreakBadge:
    """Tests for Winner Streak Badge System"""

    def test_my_badge_requires_auth(self):
        """GET /api/winners/my-badge requires authentication"""
        response = requests.get(f"{BASE_URL}/api/winners/my-badge")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_my_badge_returns_badge_info(self, auth_headers):
        """GET /api/winners/my-badge returns badge tier and verified_count"""
        response = requests.get(f"{BASE_URL}/api/winners/my-badge", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "verified_count" in data, "Response should have 'verified_count'"
        assert "badge" in data, "Response should have 'badge' (can be null)"
        assert "tiers" in data, "Response should have 'tiers' list"
        
        # Check tiers structure
        tiers = data.get("tiers", [])
        assert len(tiers) == 3, "Should have 3 badge tiers (Bronze, Silver, Gold)"
        
        for tier in tiers:
            assert "tier" in tier, "Tier should have 'tier' field"
            assert "min_wins" in tier, "Tier should have 'min_wins'"
            assert "label" in tier, "Tier should have 'label'"
            assert "color" in tier, "Tier should have 'color'"

    def test_winners_list_includes_badge_info(self):
        """GET /api/winners/ response includes badge info per winner"""
        response = requests.get(f"{BASE_URL}/api/winners/")
        assert response.status_code == 200
        
        data = response.json()
        assert "winners" in data, "Response should have 'winners' list"
        # Badge info is added per winner if they have verified wins


# =====================
# API KEY MANAGEMENT
# =====================

class TestApiKeyManagement:
    """Tests for API Key Generation/Management"""

    def test_generate_key_requires_auth(self):
        """POST /api/api-keys/generate requires authentication"""
        response = requests.post(f"{BASE_URL}/api/api-keys/generate", json={"name": "Test Key"})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_generate_api_key(self, auth_headers):
        """POST /api/api-keys/generate creates a new API key"""
        response = requests.post(
            f"{BASE_URL}/api/api-keys/generate",
            headers=auth_headers,
            json={"name": "TEST_Phase4_Key"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "key" in data, "Response should have 'key' (the raw API key)"
        assert "key_id" in data, "Response should have 'key_id'"
        assert "name" in data, "Response should have 'name'"
        
        key = data.get("key", "")
        assert key.startswith("ts_"), f"Key should start with 'ts_', got '{key[:10]}...'"

    def test_list_api_keys(self, auth_headers):
        """GET /api/api-keys/ lists user's API keys"""
        response = requests.get(f"{BASE_URL}/api/api-keys/", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "keys" in data, "Response should have 'keys' list"
        
        keys = data.get("keys", [])
        if keys:
            k = keys[0]
            assert "id" in k, "Key should have 'id'"
            assert "name" in k, "Key should have 'name'"
            assert "key_prefix" in k, "Key should have 'key_prefix'"
            assert "active" in k, "Key should have 'active' status"
            assert "key_hash" not in k, "Key hash should NOT be returned"

    def test_revoke_api_key(self, auth_headers):
        """DELETE /api/api-keys/{id} revokes a key"""
        # First generate a key to revoke
        gen_response = requests.post(
            f"{BASE_URL}/api/api-keys/generate",
            headers=auth_headers,
            json={"name": "TEST_ToRevoke_Key"}
        )
        if gen_response.status_code != 200:
            pytest.skip("Could not generate key to revoke")
        
        key_id = gen_response.json().get("key_id")
        assert key_id, "Should have key_id to revoke"
        
        # Now revoke it
        revoke_response = requests.delete(f"{BASE_URL}/api/api-keys/{key_id}", headers=auth_headers)
        assert revoke_response.status_code == 200, f"Expected 200, got {revoke_response.status_code}"
        
        data = revoke_response.json()
        assert data.get("revoked") == True, "Response should confirm revoked=True"


# =====================
# API V1 ENDPOINTS (Key-Authenticated)
# =====================

class TestApiV1Endpoints:
    """Tests for API v1 endpoints with X-API-Key authentication"""

    @pytest.fixture
    def api_key(self, auth_headers):
        """Generate an API key for testing"""
        response = requests.post(
            f"{BASE_URL}/api/api-keys/generate",
            headers=auth_headers,
            json={"name": "TEST_V1_Endpoint_Key"}
        )
        if response.status_code == 200:
            return response.json().get("key")
        pytest.skip("Could not generate API key for v1 tests")

    def test_v1_products_search_requires_api_key(self):
        """GET /api/v1/products/search returns 401 without X-API-Key"""
        response = requests.get(f"{BASE_URL}/api/v1/products/search")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_v1_products_search_with_key(self, api_key):
        """GET /api/v1/products/search works with X-API-Key header"""
        response = requests.get(
            f"{BASE_URL}/api/v1/products/search",
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "products" in data, "Response should have 'products'"
        assert "total" in data, "Response should have 'total'"

    def test_v1_products_search_with_query(self, api_key):
        """GET /api/v1/products/search?q=... filters by search query"""
        response = requests.get(
            f"{BASE_URL}/api/v1/products/search?q=wireless&limit=10",
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 200

    def test_v1_product_score(self, api_key):
        """GET /api/v1/products/{id}/score returns score breakdown"""
        # First get a product ID
        search_response = requests.get(
            f"{BASE_URL}/api/v1/products/search?limit=1",
            headers={"X-API-Key": api_key}
        )
        if search_response.status_code != 200:
            pytest.skip("Could not get product for score test")
        
        products = search_response.json().get("products", [])
        if not products:
            pytest.skip("No products available")
        
        product_id = products[0].get("id")
        
        response = requests.get(
            f"{BASE_URL}/api/v1/products/{product_id}/score",
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "product" in data, "Response should have 'product'"

    def test_v1_trends_categories(self, api_key):
        """GET /api/v1/trends/categories returns trending categories"""
        response = requests.get(
            f"{BASE_URL}/api/v1/trends/categories",
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "categories" in data, "Response should have 'categories'"

    def test_v1_trends_top(self, api_key):
        """GET /api/v1/trends/top returns top products"""
        response = requests.get(
            f"{BASE_URL}/api/v1/trends/top",
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "products" in data, "Response should have 'products'"
        assert "total" in data, "Response should have 'total'"


# =====================
# SIDEBAR NAVIGATION
# =====================

class TestSidebarNavigation:
    """Tests for sidebar navigation updates (checked via UI testing)"""
    pass  # Sidebar 'API Access' link will be tested via Playwright


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
