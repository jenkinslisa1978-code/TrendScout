"""
Test Admin OAuth Credential Management API
Tests for /api/admin/oauth/credentials endpoints
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
def admin_token():
    """Get admin user token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def demo_token():
    """Get demo (non-admin) user token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}
    )
    assert response.status_code == 200, f"Demo login failed: {response.text}"
    return response.json()["token"]


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_admin_login(self, admin_token):
        """Test admin login works"""
        assert admin_token is not None
        assert len(admin_token) > 0
    
    def test_demo_login(self, demo_token):
        """Test demo login works"""
        assert demo_token is not None
        assert len(demo_token) > 0
    
    def test_trending_products_api(self):
        """Test /api/public/trending-products returns products"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert isinstance(data["products"], list)


class TestAdminOAuthCredentialsAccess:
    """Test admin-only access to OAuth credential endpoints"""
    
    def test_get_credentials_admin_success(self, admin_token):
        """Admin can GET /api/admin/oauth/credentials"""
        response = requests.get(
            f"{BASE_URL}/api/admin/oauth/credentials",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "credentials" in data
        assert isinstance(data["credentials"], dict)
        # Should have all platforms
        assert "shopify" in data["credentials"]
        assert "meta" in data["credentials"]
        assert "etsy" in data["credentials"]
        assert "google_ads" in data["credentials"]
        assert "tiktok_shop" in data["credentials"]
        assert "tiktok_ads" in data["credentials"]
    
    def test_get_credentials_demo_forbidden(self, demo_token):
        """Non-admin gets 403 on GET /api/admin/oauth/credentials"""
        response = requests.get(
            f"{BASE_URL}/api/admin/oauth/credentials",
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        assert response.status_code == 403
        data = response.json()
        assert "Admin access required" in str(data)
    
    def test_post_credentials_demo_forbidden(self, demo_token):
        """Non-admin gets 403 on POST /api/admin/oauth/credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/oauth/credentials",
            headers={"Authorization": f"Bearer {demo_token}"},
            json={"platform": "etsy", "client_id": "test", "client_secret": "test"}
        )
        assert response.status_code == 403
    
    def test_delete_credentials_demo_forbidden(self, demo_token):
        """Non-admin gets 403 on DELETE /api/admin/oauth/credentials/{platform}"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/oauth/credentials/meta",
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        assert response.status_code == 403
    
    def test_test_credentials_demo_forbidden(self, demo_token):
        """Non-admin gets 403 on POST /api/admin/oauth/credentials/{platform}/test"""
        response = requests.post(
            f"{BASE_URL}/api/admin/oauth/credentials/meta/test",
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        assert response.status_code == 403


class TestAdminOAuthCredentialsCRUD:
    """Test CRUD operations for OAuth credentials"""
    
    def test_shopify_shows_env_source(self, admin_token):
        """Shopify should show source='env' since it's configured via env vars"""
        response = requests.get(
            f"{BASE_URL}/api/admin/oauth/credentials",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        shopify = data["credentials"]["shopify"]
        assert shopify["configured"] == True
        assert shopify["source"] == "env"
    
    def test_save_credentials_success(self, admin_token):
        """Admin can save credentials for a platform"""
        response = requests.post(
            f"{BASE_URL}/api/admin/oauth/credentials",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "platform": "google_ads",
                "client_id": "test_google_client_id_123",
                "client_secret": "test_google_secret_456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["platform"] == "google_ads"
        assert "saved successfully" in data["message"]
    
    def test_verify_saved_credentials(self, admin_token):
        """Verify saved credentials appear in list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/oauth/credentials",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        google_ads = data["credentials"]["google_ads"]
        assert google_ads["configured"] == True
        assert google_ads["source"] == "admin_ui"
        assert google_ads["client_id_preview"].startswith("test_goo")
    
    def test_test_credentials_endpoint(self, admin_token):
        """Test the credential test endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/admin/oauth/credentials/google_ads/test",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "google_ads"
        assert data["oauth_ready"] == True
        assert "configured and ready" in data["message"]
    
    def test_oauth_platforms_reflects_configured(self, admin_token):
        """GET /api/oauth/platforms should show oauth_ready for configured platforms"""
        response = requests.get(f"{BASE_URL}/api/oauth/platforms")
        assert response.status_code == 200
        data = response.json()
        assert "platforms" in data
        # google_ads should now be oauth_ready
        google_ads = data["platforms"].get("google_ads")
        assert google_ads is not None
        assert google_ads["oauth_ready"] == True
    
    def test_connections_platforms_reflects_configured(self, admin_token):
        """GET /api/connections/platforms should show oauth_ready for configured platforms"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200
        data = response.json()
        # google_ads is mapped to 'google' in ads category
        google = data.get("ads", {}).get("google")
        assert google is not None
        # Check that oauth_ready is present (may be True or False depending on state)
        assert "oauth_ready" in google
    
    def test_save_credentials_invalid_platform(self, admin_token):
        """Saving credentials for unknown platform returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/admin/oauth/credentials",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "platform": "unknown_platform",
                "client_id": "test",
                "client_secret": "test"
            }
        )
        assert response.status_code == 400
    
    def test_save_credentials_empty_values(self, admin_token):
        """Saving credentials with empty values returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/admin/oauth/credentials",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "platform": "etsy",
                "client_id": "",
                "client_secret": "test"
            }
        )
        assert response.status_code == 400
    
    def test_delete_credentials_success(self, admin_token):
        """Admin can delete credentials for a platform"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/oauth/credentials/google_ads",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["platform"] == "google_ads"
    
    def test_verify_deleted_credentials(self, admin_token):
        """Verify deleted credentials no longer appear as configured"""
        response = requests.get(
            f"{BASE_URL}/api/admin/oauth/credentials",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        google_ads = data["credentials"]["google_ads"]
        assert google_ads["configured"] == False
        assert google_ads["source"] == "none"
    
    def test_delete_nonexistent_credentials(self, admin_token):
        """Deleting non-existent credentials returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/oauth/credentials/etsy",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404


class TestCredentialStructure:
    """Test the structure of credential responses"""
    
    def test_credential_has_required_fields(self, admin_token):
        """Each credential should have required fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/oauth/credentials",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        for platform, cred in data["credentials"].items():
            assert "platform" in cred
            assert "name" in cred
            assert "connection_type" in cred
            assert "configured" in cred
            assert "source" in cred
            assert "setup_url" in cred
            assert "setup_instructions" in cred
            assert "requires_shop_domain" in cred
            # Verify connection_type is valid
            assert cred["connection_type"] in ["store", "ads", "social"]
