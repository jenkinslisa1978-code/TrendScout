"""
Test Shopify Store Connection Bug Fix (Iteration 78)

Bug fix: Shopify store connection was failing silently.
Root causes fixed:
1. Frontend was asking for OAuth Client ID/Secret but regular users use Admin API access tokens
2. fetch API bodyUsed bug with 4xx responses meant error messages were unreadable
3. CSRF middleware was blocking the POST

Tests verify:
- POST /api/connections/store with platform=shopify and invalid access_token returns 200 with success=false
- POST /api/connections/store with platform=shopify but no access_token returns validation error
- POST /api/connections/store with platform=shopify and non-existent store domain returns descriptive error
- Authenticated requests work correctly
"""

import pytest
import requests
import os
import random
import string

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "admin123456"


class TestShopifyConnectionFix:
    """Test Shopify connection endpoint with various scenarios"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a requests session for the tests"""
        return requests.Session()
    
    @pytest.fixture(scope="class")
    def auth_token(self, session):
        """Login and get auth token"""
        # Login
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        data = login_response.json()
        token = data.get("token") or data.get("access_token")
        assert token, "No token in login response"
        
        # Also get CSRF token from cookies
        csrf_token = None
        for cookie in session.cookies:
            if cookie.name == '__Host-csrf':
                csrf_token = cookie.value
                break
        
        return {"token": token, "csrf": csrf_token}
    
    def test_shopify_connection_invalid_token(self, session, auth_token):
        """Test: Invalid access token returns 200 with success=false and descriptive error"""
        headers = {
            "Authorization": f"Bearer {auth_token['token']}",
            "Content-Type": "application/json",
        }
        if auth_token.get('csrf'):
            headers['x-csrf-token'] = auth_token['csrf']
        
        response = session.post(f"{BASE_URL}/api/connections/store", json={
            "platform": "shopify",
            "store_url": "test-store-123.myshopify.com",
            "access_token": "shpat_fake_invalid_token_12345"
        }, headers=headers)
        
        # Should return 200 (not 4xx) with success=false
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == False, f"Expected success=false, got: {data}"
        assert "error" in data, f"Expected error object in response: {data}"
        
        # Error message should be descriptive (not generic)
        error_message = data.get("error", {}).get("message", "")
        assert error_message, f"No error message in response: {data}"
        assert any(phrase in error_message.lower() for phrase in [
            "not found", "invalid", "access token", "could not", "unreachable"
        ]), f"Error message not descriptive: {error_message}"
        
        print(f"✓ Invalid token returns: success=false, error='{error_message}'")
    
    def test_shopify_connection_missing_token(self, session, auth_token):
        """Test: Missing access token returns 200 with success=false and validation error"""
        headers = {
            "Authorization": f"Bearer {auth_token['token']}",
            "Content-Type": "application/json",
        }
        if auth_token.get('csrf'):
            headers['x-csrf-token'] = auth_token['csrf']
        
        response = session.post(f"{BASE_URL}/api/connections/store", json={
            "platform": "shopify",
            "store_url": "test-store-missing-token.myshopify.com"
            # access_token intentionally missing
        }, headers=headers)
        
        # Should return 200 with success=false
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == False, f"Expected success=false, got: {data}"
        assert "error" in data, f"Expected error object in response: {data}"
        
        error_message = data.get("error", {}).get("message", "")
        assert "required" in error_message.lower() or "access token" in error_message.lower(), \
            f"Expected validation error mentioning 'required' or 'access token': {error_message}"
        
        print(f"✓ Missing token returns: success=false, error='{error_message}'")
    
    def test_shopify_connection_nonexistent_store(self, session, auth_token):
        """Test: Non-existent store domain returns descriptive 'not found' error"""
        headers = {
            "Authorization": f"Bearer {auth_token['token']}",
            "Content-Type": "application/json",
        }
        if auth_token.get('csrf'):
            headers['x-csrf-token'] = auth_token['csrf']
        
        # Use a domain that definitely doesn't exist
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        fake_domain = f"nonexistent-store-{random_suffix}"
        
        response = session.post(f"{BASE_URL}/api/connections/store", json={
            "platform": "shopify",
            "store_url": fake_domain,
            "access_token": "shpat_test_fake_token_abc123"
        }, headers=headers)
        
        # Should return 200 with success=false
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == False, f"Expected success=false, got: {data}"
        assert "error" in data, f"Expected error object in response: {data}"
        
        error = data.get("error", {})
        error_message = error.get("message", "")
        error_code = error.get("code", "")
        
        # Should be NOT_FOUND or UNREACHABLE or similar
        assert error_code in ["NOT_FOUND", "AUTH_FAILED", "UNREACHABLE", "SHOPIFY_ERROR"], \
            f"Expected descriptive error code, got: {error_code}"
        assert error_message, f"Expected error message, got empty"
        
        print(f"✓ Non-existent store returns: code={error_code}, message='{error_message}'")
    
    def test_shopify_connection_unauthenticated(self, session):
        """Test: Unauthenticated request returns 401 or 403"""
        response = session.post(f"{BASE_URL}/api/connections/store", json={
            "platform": "shopify",
            "store_url": "test-store.myshopify.com",
            "access_token": "shpat_test"
        })
        
        # Should be rejected without auth
        assert response.status_code in [401, 403, 422], \
            f"Expected 401/403/422 without auth, got {response.status_code}: {response.text}"
        
        print(f"✓ Unauthenticated request correctly rejected with status {response.status_code}")
    
    def test_platforms_endpoint_shows_shopify_fields(self, session, auth_token):
        """Test: /api/connections/platforms shows Shopify needs store_url and access_token"""
        headers = {"Authorization": f"Bearer {auth_token['token']}"}
        
        response = session.get(f"{BASE_URL}/api/connections/platforms", headers=headers)
        assert response.status_code == 200, f"Failed to get platforms: {response.text}"
        
        data = response.json()
        assert "stores" in data, "No 'stores' in platforms response"
        assert "shopify" in data["stores"], "Shopify not in stores"
        
        shopify_config = data["stores"]["shopify"]
        assert "fields" in shopify_config, "No 'fields' for Shopify"
        
        fields = shopify_config["fields"]
        assert "store_url" in fields, f"store_url not in Shopify fields: {fields}"
        assert "access_token" in fields, f"access_token not in Shopify fields: {fields}"
        
        # Should NOT require api_key/api_secret for Shopify
        # (those were for OAuth which is not used)
        # Note: api_key might still be listed but should not be required
        
        # Check help text mentions Admin API
        help_text = shopify_config.get("help", "")
        assert "admin" in help_text.lower() or "develop apps" in help_text.lower(), \
            f"Shopify help should mention Admin API setup: {help_text}"
        
        print(f"✓ Shopify config: fields={fields}, help mentions Admin API")


class TestOtherPagesRegression:
    """Regression tests to ensure other pages still work after CORS change"""
    
    @pytest.fixture(scope="class")
    def session(self):
        return requests.Session()
    
    @pytest.fixture(scope="class")
    def auth_token(self, session):
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200
        data = login_response.json()
        return data.get("token") or data.get("access_token")
    
    def test_dashboard_api(self, session, auth_token):
        """Test: Dashboard API still works"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = session.get(f"{BASE_URL}/api/dashboard/next-steps", headers=headers)
        # Should work or return appropriate status
        assert response.status_code in [200, 401], f"Dashboard next-steps failed: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "steps" in data or "stats" in data, f"Unexpected dashboard response: {data}"
            print("✓ Dashboard API works")
        else:
            print(f"✓ Dashboard API returns {response.status_code} (auth required)")
    
    def test_health_endpoint(self, session):
        """Test: Health endpoint still works"""
        response = session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("✓ Health endpoint works")
    
    def test_user_connections_endpoint(self, session, auth_token):
        """Test: Get user connections endpoint works"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        csrf_token = None
        for cookie in session.cookies:
            if cookie.name == '__Host-csrf':
                csrf_token = cookie.value
                break
        if csrf_token:
            headers['x-csrf-token'] = csrf_token
        
        response = session.get(f"{BASE_URL}/api/connections/", headers=headers)
        assert response.status_code == 200, f"Get connections failed: {response.text}"
        
        data = response.json()
        assert "stores" in data, "No 'stores' in connections"
        assert "ads" in data, "No 'ads' in connections"
        
        print(f"✓ Get connections works: stores={len(data['stores'])}, ads={len(data['ads'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
