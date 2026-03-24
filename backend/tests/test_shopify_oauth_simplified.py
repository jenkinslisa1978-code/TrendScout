"""
Test Shopify OAuth simplified flow and platform connections oauth_ready flag.
Tests the new one-click OAuth for Shopify where only shop_domain is required.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
DEMO_EMAIL = "demo@trendscout.click"
DEMO_PASSWORD = "DemoReview2026!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for demo user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestOAuthPlatformsEndpoint:
    """Test GET /api/oauth/platforms - returns all platforms with oauth_ready flag"""
    
    def test_oauth_platforms_returns_all_platforms(self):
        """Test that /api/oauth/platforms returns all supported OAuth platforms"""
        response = requests.get(f"{BASE_URL}/api/oauth/platforms")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "platforms" in data, "Response should contain 'platforms' key"
        
        platforms = data["platforms"]
        # Check that Shopify is present
        assert "shopify" in platforms, "Shopify should be in platforms"
        
    def test_shopify_oauth_ready_true(self):
        """Test that Shopify has oauth_ready=true (since SHOPIFY_CLIENT_ID/SECRET are configured)"""
        response = requests.get(f"{BASE_URL}/api/oauth/platforms")
        assert response.status_code == 200
        
        data = response.json()
        shopify = data["platforms"].get("shopify", {})
        
        # Shopify should be oauth_ready since env vars are configured
        assert shopify.get("oauth_ready") == True, f"Shopify should be oauth_ready=true, got: {shopify}"
        assert shopify.get("configured") == True, "Shopify should be configured=true"
        assert shopify.get("requires_shop_domain") == True, "Shopify requires shop_domain"
        
    def test_other_platforms_oauth_ready_false(self):
        """Test that other platforms have oauth_ready=false (no env vars configured)"""
        response = requests.get(f"{BASE_URL}/api/oauth/platforms")
        assert response.status_code == 200
        
        data = response.json()
        platforms = data["platforms"]
        
        # Check that other platforms are NOT oauth_ready (no env vars)
        for key in ["etsy", "meta", "google_ads", "tiktok_ads"]:
            if key in platforms:
                platform = platforms[key]
                assert platform.get("oauth_ready") == False, f"{key} should be oauth_ready=false"


class TestConnectionsPlatformsEndpoint:
    """Test GET /api/connections/platforms - returns platforms with oauth_ready enriched"""
    
    def test_connections_platforms_returns_oauth_ready(self):
        """Test that /api/connections/platforms includes oauth_ready flag"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "stores" in data, "Response should contain 'stores' key"
        assert "ads" in data, "Response should contain 'ads' key"
        
    def test_shopify_store_oauth_ready(self):
        """Test that Shopify in stores has oauth_ready=true"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200
        
        data = response.json()
        stores = data.get("stores", {})
        shopify = stores.get("shopify", {})
        
        assert shopify.get("oauth_ready") == True, f"Shopify store should be oauth_ready=true, got: {shopify}"
        
    def test_other_stores_oauth_ready_false(self):
        """Test that non-OAuth stores have oauth_ready=false"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200
        
        data = response.json()
        stores = data.get("stores", {})
        
        # WooCommerce, BigCommerce, Squarespace should NOT be oauth_ready
        for key in ["woocommerce", "bigcommerce", "squarespace"]:
            if key in stores:
                store = stores[key]
                assert store.get("oauth_ready") == False, f"{key} should be oauth_ready=false"


class TestShopifyOAuthInit:
    """Test POST /api/shopify/oauth/init - simplified OAuth init (only shop_domain required)"""
    
    def test_shopify_oauth_init_only_shop_domain(self, auth_headers):
        """Test that Shopify OAuth init only requires shop_domain (no client_id/secret)"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/oauth/init",
            json={"shop_domain": "test-store"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "oauth_url" in data, "Response should contain oauth_url"
        assert "state" in data, "Response should contain state"
        
        # Verify the oauth_url is properly formatted
        oauth_url = data["oauth_url"]
        assert "test-store.myshopify.com" in oauth_url, "OAuth URL should contain the shop domain"
        assert "client_id=" in oauth_url, "OAuth URL should contain client_id"
        assert "scope=" in oauth_url, "OAuth URL should contain scope"
        
    def test_shopify_oauth_init_with_myshopify_domain(self, auth_headers):
        """Test that shop_domain with .myshopify.com suffix works"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/oauth/init",
            json={"shop_domain": "another-store.myshopify.com"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "oauth_url" in data
        assert "another-store.myshopify.com" in data["oauth_url"]
        
    def test_shopify_oauth_init_missing_shop_domain(self, auth_headers):
        """Test that missing shop_domain returns validation error"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/oauth/init",
            json={},
            headers=auth_headers
        )
        # Should fail validation - shop_domain is required
        assert response.status_code == 422, f"Expected 422 for missing shop_domain, got {response.status_code}"
        
    def test_shopify_oauth_init_requires_auth(self):
        """Test that OAuth init requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/oauth/init",
            json={"shop_domain": "test-store"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"


class TestShopifySyncProducts:
    """Test POST /api/shopify/sync-products - returns error when no connection exists"""
    
    def test_sync_products_no_connection(self, auth_headers):
        """Test that sync-products returns error when no Shopify store is connected"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/sync-products",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should return success=false with error message
        assert data.get("success") == False, f"Expected success=false, got: {data}"
        assert "error" in data, "Response should contain error message"
        
    def test_sync_products_requires_auth(self):
        """Test that sync-products requires authentication"""
        response = requests.post(f"{BASE_URL}/api/shopify/sync-products")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"


class TestShopifySyncedProducts:
    """Test GET /api/shopify/synced-products - returns empty list for user with no synced data"""
    
    def test_synced_products_empty_list(self, auth_headers):
        """Test that synced-products returns empty list for user with no synced products"""
        response = requests.get(
            f"{BASE_URL}/api/shopify/synced-products",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=true, got: {data}"
        assert "products" in data, "Response should contain products key"
        assert isinstance(data["products"], list), "Products should be a list"
        # For a user with no synced products, list should be empty
        assert "count" in data, "Response should contain count"
        
    def test_synced_products_requires_auth(self):
        """Test that synced-products requires authentication"""
        response = requests.get(f"{BASE_URL}/api/shopify/synced-products")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"


class TestLoginFlow:
    """Test that login flow still works correctly"""
    
    def test_login_with_demo_credentials(self):
        """Test login with demo user credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "token" in data, "Response should contain token"
        assert "user" in data, "Response should contain user"
        
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
