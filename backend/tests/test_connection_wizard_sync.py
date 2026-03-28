"""
Test Connection Wizard and Multi-Platform Sync Features (Iteration 125)

Tests:
- GET /api/health - Health check
- POST /api/auth/login - Login for admin and demo users
- GET /api/sync/products - Unified synced products endpoint (requires auth)
- POST /api/sync/etsy/products - Etsy sync (requires auth, returns 404 without connection)
- POST /api/sync/woocommerce/products - WooCommerce sync (requires auth, returns 404 without connection)
- POST /api/sync/amazon/products - Amazon sync (requires auth, returns beta message)
- GET /api/connections/platforms - Platform list with oauth_ready status
- GET /api/oauth/platforms - OAuth platforms list
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "reviewer@trendscout.click"
ADMIN_PASSWORD = "ShopifyReview2026!"
DEMO_EMAIL = "demo@trendscout.click"
DEMO_PASSWORD = "DemoReview2026!"


class TestHealthAndAuth:
    """Health check and authentication tests"""
    
    def test_health_check(self):
        """Test /api/health returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: Health check returns ok")
    
    def test_admin_login(self):
        """Test admin user can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        print(f"PASS: Admin login successful")
    
    def test_demo_login(self):
        """Test demo user can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        print(f"PASS: Demo login successful")


class TestSyncEndpoints:
    """Test multi-platform sync endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip("Admin login failed")
    
    @pytest.fixture
    def demo_token(self):
        """Get demo user auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip("Demo login failed")
    
    def test_get_synced_products_requires_auth(self):
        """Test GET /api/sync/products requires authentication"""
        response = requests.get(f"{BASE_URL}/api/sync/products")
        assert response.status_code in [401, 403]
        print("PASS: GET /api/sync/products requires auth")
    
    def test_get_synced_products_with_auth(self, admin_token):
        """Test GET /api/sync/products returns products list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/sync/products", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "products" in data
        assert "by_platform" in data
        print(f"PASS: GET /api/sync/products returns {len(data.get('products', []))} products")
    
    def test_etsy_sync_without_connection(self, admin_token):
        """Test POST /api/sync/etsy/products returns 404 without active connection"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{BASE_URL}/api/sync/etsy/products", headers=headers)
        # Should return 404 because no active etsy connection exists
        assert response.status_code == 404
        data = response.json()
        # Check both detail and error.message formats
        error_msg = data.get("detail", "") or data.get("error", {}).get("message", "")
        assert "etsy" in error_msg.lower() or "connection" in error_msg.lower()
        print("PASS: POST /api/sync/etsy/products returns 404 without connection")
    
    def test_woocommerce_sync_without_connection(self, admin_token):
        """Test POST /api/sync/woocommerce/products returns 404 without active connection"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{BASE_URL}/api/sync/woocommerce/products", headers=headers)
        # Should return 404 because no active woocommerce connection exists
        assert response.status_code == 404
        data = response.json()
        # Check both detail and error.message formats
        error_msg = data.get("detail", "") or data.get("error", {}).get("message", "")
        assert "woocommerce" in error_msg.lower() or "connection" in error_msg.lower()
        print("PASS: POST /api/sync/woocommerce/products returns 404 without connection")
    
    def test_amazon_sync_beta_message(self, admin_token):
        """Test POST /api/sync/amazon/products returns beta message"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{BASE_URL}/api/sync/amazon/products", headers=headers)
        # Should return 404 (no connection) or 200 with beta message
        if response.status_code == 200:
            data = response.json()
            assert "beta" in data.get("message", "").lower() or data.get("synced_count") == 0
            print("PASS: POST /api/sync/amazon/products returns beta message")
        elif response.status_code == 404:
            print("PASS: POST /api/sync/amazon/products returns 404 (no connection)")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")


class TestPlatformEndpoints:
    """Test platform connection endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip("Admin login failed")
    
    def test_get_platforms(self, admin_token):
        """Test GET /api/connections/platforms returns platform list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/connections/platforms", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Should have stores, ads, and possibly social sections
        assert "stores" in data or "ads" in data
        print(f"PASS: GET /api/connections/platforms returns platform data")
        
        # Check for expected platforms
        stores = data.get("stores", {})
        if "shopify" in stores:
            print(f"  - Shopify: oauth_ready={stores['shopify'].get('oauth_ready', False)}")
        if "etsy" in stores:
            print(f"  - Etsy: oauth_ready={stores['etsy'].get('oauth_ready', False)}")
        if "woocommerce" in stores:
            print(f"  - WooCommerce: oauth_ready={stores['woocommerce'].get('oauth_ready', False)}")
    
    def test_get_oauth_platforms(self, admin_token):
        """Test GET /api/oauth/platforms returns OAuth platform list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/oauth/platforms", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "platforms" in data
        print(f"PASS: GET /api/oauth/platforms returns {len(data.get('platforms', {}))} platforms")


class TestSSREndpoint:
    """Test SSR for trending products"""
    
    def test_public_trending_products(self):
        """Test GET /api/public/trending-products returns products"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        print(f"PASS: GET /api/public/trending-products returns {len(data.get('products', []))} products")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
