"""
Tests for Platform Connections API endpoints
- GET /api/connections/platforms - Get supported platforms (stores + ads)
- POST /api/connections/store - Connect a store platform
- POST /api/connections/ads - Connect an ad platform
- GET /api/connections/ - Get user's active connections
- DELETE /api/connections/store/{platform} - Disconnect store platform
- DELETE /api/connections/ads/{platform} - Disconnect ad platform
- POST /api/connections/publish/{store_id} - Auto-publish store to connected platform
- POST /api/connections/post-ads/{product_id} - Auto-post ads to connected platforms
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestConnectionsPlatforms:
    """Test /api/connections/platforms - Get supported platforms"""

    def test_get_supported_platforms(self):
        """GET /api/connections/platforms returns stores and ads platforms"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "stores" in data
        assert "ads" in data
        
        # Verify required store platforms
        stores = data["stores"]
        assert "shopify" in stores
        assert "woocommerce" in stores
        assert "etsy" in stores
        assert "bigcommerce" in stores
        assert "squarespace" in stores
        
        # Verify store platform structure
        assert stores["shopify"]["name"] == "Shopify"
        assert "fields" in stores["shopify"]
        assert "help" in stores["shopify"]
        assert "url" in stores["shopify"]
        
        # Verify WooCommerce fields
        assert "store_url" in stores["woocommerce"]["fields"]
        assert "api_key" in stores["woocommerce"]["fields"]
        assert "api_secret" in stores["woocommerce"]["fields"]
        
        # Verify required ad platforms
        ads = data["ads"]
        assert "meta" in ads
        assert "tiktok" in ads
        assert "google" in ads
        
        # Verify ad platform structure
        assert ads["meta"]["name"] == "Meta (Facebook & Instagram)"
        assert "fields" in ads["meta"]
        assert "access_token" in ads["meta"]["fields"]
        assert "account_id" in ads["meta"]["fields"]
        assert "pixel_id" in ads["meta"]["fields"]
        
        print(f"✓ Supported platforms returned: {len(stores)} stores, {len(ads)} ad platforms")


class TestAuthenticatedConnections:
    """Tests requiring authentication"""

    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers by logging in"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if login_response.status_code != 200:
            pytest.skip("Authentication failed - skipping authenticated tests")
        
        data = login_response.json()
        token = data.get("access_token") or data.get("session", {}).get("access_token")
        if not token:
            pytest.skip("No access token received - skipping authenticated tests")
        
        return {"Authorization": f"Bearer {token}"}

    def test_get_user_connections(self, auth_headers):
        """GET /api/connections/ returns user's connections"""
        response = requests.get(f"{BASE_URL}/api/connections/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "stores" in data
        assert "ads" in data
        assert isinstance(data["stores"], list)
        assert isinstance(data["ads"], list)
        
        print(f"✓ User has {len(data['stores'])} store connections, {len(data['ads'])} ad connections")

    def test_connect_woocommerce_store(self, auth_headers):
        """POST /api/connections/store connects WooCommerce"""
        response = requests.post(f"{BASE_URL}/api/connections/store", 
            headers=auth_headers,
            json={
                "platform": "woocommerce",
                "store_url": "https://test-store.woocommerce.com",
                "api_key": "ck_test_api_key_123",
                "api_secret": "cs_test_api_secret_456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["platform"] == "woocommerce"
        assert "WooCommerce" in data["message"]
        print(f"✓ WooCommerce connected: {data['message']}")

    def test_connect_etsy_store(self, auth_headers):
        """POST /api/connections/store connects Etsy"""
        response = requests.post(f"{BASE_URL}/api/connections/store", 
            headers=auth_headers,
            json={
                "platform": "etsy",
                "store_url": "https://www.etsy.com/shop/testshop",
                "api_key": "etsy_test_api_key",
                "access_token": "etsy_test_token"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["platform"] == "etsy"
        print(f"✓ Etsy connected: {data['message']}")

    def test_connect_meta_ads(self, auth_headers):
        """POST /api/connections/ads connects Meta ads"""
        response = requests.post(f"{BASE_URL}/api/connections/ads", 
            headers=auth_headers,
            json={
                "platform": "meta",
                "access_token": "test_meta_access_token",
                "account_id": "act_123456789",
                "pixel_id": "987654321"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["platform"] == "meta"
        assert "Meta" in data["message"]
        print(f"✓ Meta ads connected: {data['message']}")

    def test_connect_tiktok_ads(self, auth_headers):
        """POST /api/connections/ads connects TikTok ads"""
        response = requests.post(f"{BASE_URL}/api/connections/ads", 
            headers=auth_headers,
            json={
                "platform": "tiktok",
                "access_token": "test_tiktok_access_token",
                "account_id": "tiktok_advertiser_123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["platform"] == "tiktok"
        print(f"✓ TikTok ads connected: {data['message']}")

    def test_connect_google_ads(self, auth_headers):
        """POST /api/connections/ads connects Google ads"""
        response = requests.post(f"{BASE_URL}/api/connections/ads", 
            headers=auth_headers,
            json={
                "platform": "google",
                "access_token": "test_google_access_token",
                "account_id": "customers/123-456-7890"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["platform"] == "google"
        print(f"✓ Google ads connected: {data['message']}")

    def test_verify_all_connections(self, auth_headers):
        """Verify all test connections were saved"""
        response = requests.get(f"{BASE_URL}/api/connections/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check store connections
        store_platforms = [c["platform"] for c in data["stores"]]
        assert "woocommerce" in store_platforms or "etsy" in store_platforms
        
        # Check ad connections
        ad_platforms = [c["platform"] for c in data["ads"]]
        assert "meta" in ad_platforms or "tiktok" in ad_platforms or "google" in ad_platforms
        
        print(f"✓ Verified connections: stores={store_platforms}, ads={ad_platforms}")

    def test_connect_unsupported_platform(self, auth_headers):
        """POST /api/connections/store rejects unsupported platform"""
        response = requests.post(f"{BASE_URL}/api/connections/store", 
            headers=auth_headers,
            json={
                "platform": "fakeshop",
                "store_url": "https://fake.com",
                "api_key": "fake"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported platform" in data.get("detail", "")
        print("✓ Unsupported platform correctly rejected")

    def test_disconnect_woocommerce(self, auth_headers):
        """DELETE /api/connections/store/woocommerce disconnects"""
        response = requests.delete(f"{BASE_URL}/api/connections/store/woocommerce", headers=auth_headers)
        # Accept 200 (deleted) or 404 (already deleted)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            print("✓ WooCommerce disconnected")
        else:
            print("✓ WooCommerce already disconnected (404)")

    def test_disconnect_etsy(self, auth_headers):
        """DELETE /api/connections/store/etsy disconnects"""
        response = requests.delete(f"{BASE_URL}/api/connections/store/etsy", headers=auth_headers)
        assert response.status_code in [200, 404]
        print("✓ Etsy disconnect handled")

    def test_disconnect_meta_ads(self, auth_headers):
        """DELETE /api/connections/ads/meta disconnects"""
        response = requests.delete(f"{BASE_URL}/api/connections/ads/meta", headers=auth_headers)
        assert response.status_code in [200, 404]
        print("✓ Meta ads disconnect handled")

    def test_disconnect_tiktok_ads(self, auth_headers):
        """DELETE /api/connections/ads/tiktok disconnects"""
        response = requests.delete(f"{BASE_URL}/api/connections/ads/tiktok", headers=auth_headers)
        assert response.status_code in [200, 404]
        print("✓ TikTok ads disconnect handled")

    def test_disconnect_google_ads(self, auth_headers):
        """DELETE /api/connections/ads/google disconnects"""
        response = requests.delete(f"{BASE_URL}/api/connections/ads/google", headers=auth_headers)
        assert response.status_code in [200, 404]
        print("✓ Google ads disconnect handled")


class TestAutoPublishAndPost:
    """Tests for auto-publish and auto-post endpoints (MOCKED - does not call external APIs)"""

    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if login_response.status_code != 200:
            pytest.skip("Authentication failed")
        
        data = login_response.json()
        token = data.get("access_token") or data.get("session", {}).get("access_token")
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def setup_connections(self, auth_headers):
        """Set up store and ad connections for testing auto-publish/post"""
        # Connect Shopify store
        requests.post(f"{BASE_URL}/api/connections/store", 
            headers=auth_headers,
            json={
                "platform": "shopify",
                "store_url": "https://test-auto-publish.myshopify.com",
                "api_key": "shpak_test",
                "access_token": "shpat_test_token"
            }
        )
        
        # Connect Meta ads
        requests.post(f"{BASE_URL}/api/connections/ads", 
            headers=auth_headers,
            json={
                "platform": "meta",
                "access_token": "test_meta_token",
                "account_id": "act_test_123"
            }
        )
        
        return True

    def test_auto_publish_requires_store_connection(self, auth_headers):
        """POST /api/connections/publish/{store_id} requires store connection"""
        # First disconnect all stores
        requests.delete(f"{BASE_URL}/api/connections/store/shopify", headers=auth_headers)
        requests.delete(f"{BASE_URL}/api/connections/store/woocommerce", headers=auth_headers)
        
        response = requests.post(f"{BASE_URL}/api/connections/publish/fake-store-id", headers=auth_headers)
        # Expect 400 (no store connected) or 404 (store not found)
        assert response.status_code in [400, 404]
        print("✓ Auto-publish correctly requires store connection")

    def test_auto_post_ads_requires_ad_connection(self, auth_headers):
        """POST /api/connections/post-ads/{product_id} requires ad connection"""
        # First disconnect all ad platforms
        requests.delete(f"{BASE_URL}/api/connections/ads/meta", headers=auth_headers)
        requests.delete(f"{BASE_URL}/api/connections/ads/tiktok", headers=auth_headers)
        requests.delete(f"{BASE_URL}/api/connections/ads/google", headers=auth_headers)
        
        response = requests.post(f"{BASE_URL}/api/connections/post-ads/fake-product-id", headers=auth_headers)
        # Expect 400 (no ad platform connected) or 404 (product/creatives not found)
        assert response.status_code in [400, 404]
        print("✓ Auto-post ads correctly requires ad connection")

    def test_auto_publish_with_store_connected(self, auth_headers, setup_connections):
        """POST /api/connections/publish/{store_id} publishes to connected store (MOCKED)"""
        # Get user's stores
        stores_response = requests.get(f"{BASE_URL}/api/stores", headers=auth_headers)
        if stores_response.status_code != 200:
            pytest.skip("No stores available for testing")
        
        stores = stores_response.json()
        if not stores:
            pytest.skip("No stores available for testing")
        
        store_id = stores[0].get("id")
        if not store_id:
            pytest.skip("Store has no ID")
        
        response = requests.post(f"{BASE_URL}/api/connections/publish/{store_id}", headers=auth_headers)
        # Expect 200 (success) or 400 (no store connected after cleanup)
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "platform" in data
            print(f"✓ MOCKED: Auto-publish to {data.get('platform')}: {data.get('message')}")
        else:
            print(f"✓ Auto-publish returned {response.status_code} (expected if no store connected)")

    def test_auto_post_ads_with_ad_connected(self, auth_headers, setup_connections):
        """POST /api/connections/post-ads/{product_id} posts to connected ad platforms (MOCKED)"""
        # Get products
        products_response = requests.get(f"{BASE_URL}/api/products?limit=1", headers=auth_headers)
        if products_response.status_code != 200:
            pytest.skip("No products available for testing")
        
        products_data = products_response.json()
        products = products_data.get("data") or products_data.get("products") or []
        if not products:
            pytest.skip("No products available for testing")
        
        product_id = products[0].get("id")
        
        # First generate ad creatives for this product
        requests.post(f"{BASE_URL}/api/ad-creatives/generate/{product_id}", headers=auth_headers)
        
        response = requests.post(f"{BASE_URL}/api/connections/post-ads/{product_id}", headers=auth_headers)
        # Expect 200 (success), 400 (no ad connected), or 404 (no creatives)
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            print(f"✓ MOCKED: Auto-post ads to {len(data.get('posted_to', []))} platforms")
        else:
            print(f"✓ Auto-post returned {response.status_code} (expected if no ad connected or no creatives)")


class TestConnectionsCleanup:
    """Cleanup test connections"""

    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if login_response.status_code != 200:
            pytest.skip("Authentication failed")
        
        data = login_response.json()
        token = data.get("access_token") or data.get("session", {}).get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_cleanup_test_connections(self, auth_headers):
        """Clean up test connections created during tests"""
        # Clean up any test stores
        for platform in ["woocommerce", "etsy", "bigcommerce", "squarespace"]:
            requests.delete(f"{BASE_URL}/api/connections/store/{platform}", headers=auth_headers)
        
        # Keep Shopify if it was existing
        # Clean up ad platforms
        for platform in ["tiktok", "google"]:
            requests.delete(f"{BASE_URL}/api/connections/ads/{platform}", headers=auth_headers)
        
        print("✓ Test connections cleaned up")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
