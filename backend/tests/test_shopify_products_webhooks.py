"""
Test suite for Shopify Products page, webhooks, and OAuth features.
Tests:
- Shopify Products page endpoints (synced-products, sync-products)
- Shopify OAuth init endpoint
- Shopify webhook endpoints (products-create, products-update, products-delete, app-uninstalled)
- Platform connections with oauth_ready flag
- Health check endpoint
"""
import pytest
import requests
import os
import json
import hmac
import hashlib
import base64

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "demo@trendscout.click"
TEST_PASSWORD = "DemoReview2026!"


class TestAuthentication:
    """Test login flow"""
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data or "access_token" in data, "No token in response"
        print(f"✓ Login successful")


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestShopifyOAuthInit:
    """Test Shopify OAuth init endpoint"""
    
    def test_oauth_init_accepts_shop_domain(self, auth_headers):
        """POST /api/shopify/oauth/init - accepts shop_domain, returns oauth_url"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/oauth/init",
            json={"shop_domain": "test-store"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"OAuth init failed: {response.text}"
        data = response.json()
        assert "oauth_url" in data, "No oauth_url in response"
        assert "state" in data, "No state in response"
        # Verify oauth_url contains correct Shopify authorize URL
        oauth_url = data["oauth_url"]
        assert "test-store.myshopify.com" in oauth_url, "Shop domain not in oauth_url"
        assert "/admin/oauth/authorize" in oauth_url, "Not a Shopify authorize URL"
        assert "client_id=" in oauth_url, "No client_id in oauth_url"
        assert "scope=" in oauth_url, "No scope in oauth_url"
        assert "redirect_uri=" in oauth_url, "No redirect_uri in oauth_url"
        assert "state=" in oauth_url, "No state in oauth_url"
        print(f"✓ OAuth init returns correct Shopify authorize URL")
    
    def test_oauth_init_normalizes_domain(self, auth_headers):
        """Test that shop domain is normalized to .myshopify.com"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/oauth/init",
            json={"shop_domain": "my-test-store.myshopify.com"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "my-test-store.myshopify.com" in data["oauth_url"]
        print(f"✓ OAuth init normalizes domain correctly")


class TestShopifySyncedProducts:
    """Test Shopify synced products endpoints"""
    
    def test_get_synced_products_empty(self, auth_headers):
        """GET /api/shopify/synced-products - returns empty list when no products synced"""
        response = requests.get(
            f"{BASE_URL}/api/shopify/synced-products",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get synced products failed: {response.text}"
        data = response.json()
        assert "success" in data, "No success field in response"
        assert "products" in data, "No products field in response"
        assert isinstance(data["products"], list), "Products should be a list"
        print(f"✓ GET /api/shopify/synced-products returns products list (count: {len(data['products'])})")
    
    def test_sync_products_no_connection(self, auth_headers):
        """POST /api/shopify/sync-products - returns success=false with error when no connection"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/sync-products",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Sync products request failed: {response.text}"
        data = response.json()
        # Should return success=false since demo user has no real Shopify store connected
        assert "success" in data, "No success field in response"
        if not data["success"]:
            assert "error" in data, "No error field when success=false"
            print(f"✓ POST /api/shopify/sync-products returns error when no connection: {data['error']}")
        else:
            print(f"✓ POST /api/shopify/sync-products succeeded (user has connection)")


class TestShopifyWebhooks:
    """Test Shopify webhook endpoints - should return 401 with invalid HMAC"""
    
    def _generate_invalid_hmac(self, body: bytes) -> str:
        """Generate an invalid HMAC for testing"""
        return base64.b64encode(b"invalid_hmac_signature").decode()
    
    def test_products_create_webhook_invalid_hmac(self):
        """POST /api/shopify/webhooks/products-create - returns 401 with invalid HMAC"""
        body = json.dumps({"id": 123, "title": "Test Product"}).encode()
        response = requests.post(
            f"{BASE_URL}/api/shopify/webhooks/products-create",
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Hmac-Sha256": self._generate_invalid_hmac(body),
                "X-Shopify-Shop-Domain": "test-store.myshopify.com"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print(f"✓ POST /api/shopify/webhooks/products-create returns 401 with invalid HMAC")
    
    def test_products_update_webhook_invalid_hmac(self):
        """POST /api/shopify/webhooks/products-update - returns 401 with invalid HMAC"""
        body = json.dumps({"id": 123, "title": "Updated Product"}).encode()
        response = requests.post(
            f"{BASE_URL}/api/shopify/webhooks/products-update",
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Hmac-Sha256": self._generate_invalid_hmac(body),
                "X-Shopify-Shop-Domain": "test-store.myshopify.com"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print(f"✓ POST /api/shopify/webhooks/products-update returns 401 with invalid HMAC")
    
    def test_products_delete_webhook_invalid_hmac(self):
        """POST /api/shopify/webhooks/products-delete - returns 401 with invalid HMAC"""
        body = json.dumps({"id": 123}).encode()
        response = requests.post(
            f"{BASE_URL}/api/shopify/webhooks/products-delete",
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Hmac-Sha256": self._generate_invalid_hmac(body),
                "X-Shopify-Shop-Domain": "test-store.myshopify.com"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print(f"✓ POST /api/shopify/webhooks/products-delete returns 401 with invalid HMAC")
    
    def test_app_uninstalled_webhook_invalid_hmac(self):
        """POST /api/shopify/webhooks/app-uninstalled - returns 401 with invalid HMAC"""
        body = json.dumps({}).encode()
        response = requests.post(
            f"{BASE_URL}/api/shopify/webhooks/app-uninstalled",
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Hmac-Sha256": self._generate_invalid_hmac(body),
                "X-Shopify-Shop-Domain": "test-store.myshopify.com"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print(f"✓ POST /api/shopify/webhooks/app-uninstalled returns 401 with invalid HMAC")
    
    def test_webhook_missing_hmac(self):
        """Test webhook returns 401 when HMAC header is missing"""
        body = json.dumps({"id": 123}).encode()
        response = requests.post(
            f"{BASE_URL}/api/shopify/webhooks/products-create",
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Shop-Domain": "test-store.myshopify.com"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print(f"✓ Webhook returns 401 when HMAC header is missing")


class TestOAuthPlatforms:
    """Test OAuth platforms endpoint"""
    
    def test_get_oauth_platforms(self, auth_headers):
        """GET /api/oauth/platforms - returns all platforms, Shopify has oauth_ready=true"""
        response = requests.get(
            f"{BASE_URL}/api/oauth/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get OAuth platforms failed: {response.text}"
        data = response.json()
        assert "platforms" in data, "No platforms field in response"
        platforms = data["platforms"]
        assert "shopify" in platforms, "Shopify not in platforms"
        shopify_config = platforms["shopify"]
        assert shopify_config.get("oauth_ready") == True, "Shopify should have oauth_ready=true"
        print(f"✓ GET /api/oauth/platforms returns Shopify with oauth_ready=true")


class TestConnectionsPlatforms:
    """Test connections platforms endpoint"""
    
    def test_get_connections_platforms(self, auth_headers):
        """GET /api/connections/platforms - returns all platforms with oauth_ready enriched"""
        response = requests.get(
            f"{BASE_URL}/api/connections/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get connections platforms failed: {response.text}"
        data = response.json()
        assert "stores" in data, "No stores field in response"
        assert "ads" in data, "No ads field in response"
        
        # Check Shopify has oauth_ready
        stores = data["stores"]
        assert "shopify" in stores, "Shopify not in stores"
        shopify = stores["shopify"]
        assert "oauth_ready" in shopify, "No oauth_ready field for Shopify"
        assert shopify["oauth_ready"] == True, "Shopify should have oauth_ready=true"
        print(f"✓ GET /api/connections/platforms returns Shopify with oauth_ready=true")


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, auth_headers):
        """POST /api/connections/health-check - works without errors"""
        response = requests.post(
            f"{BASE_URL}/api/connections/health-check",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert "results" in data or "message" in data, "No results or message in response"
        print(f"✓ POST /api/connections/health-check works correctly")


class TestShopifyOAuthStatus:
    """Test Shopify OAuth status endpoint"""
    
    def test_get_shopify_status(self, auth_headers):
        """GET /api/shopify/oauth/status - returns connection status"""
        response = requests.get(
            f"{BASE_URL}/api/shopify/oauth/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get Shopify status failed: {response.text}"
        data = response.json()
        assert "connected" in data, "No connected field in response"
        print(f"✓ GET /api/shopify/oauth/status returns connected={data['connected']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
