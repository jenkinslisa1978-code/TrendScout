"""
Test Rate Limiting Middleware and Platform Integrations
Tests new P1 features:
1. Rate limiting middleware with per-user, per-plan limits
2. Real API integrations for Etsy, BigCommerce, Squarespace
3. Platform connections endpoint updates
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "jenkinslisa1978@gmail.com"
TEST_PASSWORD = "admin123456"


class TestRateLimitMiddleware:
    """Tests for per-user, per-plan rate limiting middleware"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for elite user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("token")
    
    def test_rate_limit_headers_on_authenticated_requests(self, auth_token):
        """Rate limit headers should be present on authenticated API responses"""
        response = requests.get(
            f"{BASE_URL}/api/connections/platforms",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        # Check all 4 rate limit headers
        assert "X-RateLimit-Limit" in response.headers, "Missing X-RateLimit-Limit header"
        assert "X-RateLimit-Remaining" in response.headers, "Missing X-RateLimit-Remaining header"
        assert "X-RateLimit-Reset" in response.headers, "Missing X-RateLimit-Reset header"
        assert "X-RateLimit-Plan" in response.headers, "Missing X-RateLimit-Plan header"
        
        print(f"Rate limit headers: Limit={response.headers['X-RateLimit-Limit']}, "
              f"Remaining={response.headers['X-RateLimit-Remaining']}, "
              f"Reset={response.headers['X-RateLimit-Reset']}, "
              f"Plan={response.headers['X-RateLimit-Plan']}")
    
    def test_elite_user_has_600_limit(self, auth_token):
        """Elite user should have 600 requests/minute limit"""
        response = requests.get(
            f"{BASE_URL}/api/connections/platforms",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        limit = int(response.headers.get("X-RateLimit-Limit", "0"))
        plan = response.headers.get("X-RateLimit-Plan", "")
        
        assert plan == "elite", f"Expected elite plan, got: {plan}"
        assert limit == 600, f"Expected 600 limit for elite, got: {limit}"
        
        print(f"Elite user verified: plan={plan}, limit={limit}")
    
    def test_rate_limit_remaining_decreases(self, auth_token):
        """X-RateLimit-Remaining should decrease with each request"""
        # First request
        response1 = requests.get(
            f"{BASE_URL}/api/connections/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        remaining1 = int(response1.headers.get("X-RateLimit-Remaining", "0"))
        
        # Second request
        response2 = requests.get(
            f"{BASE_URL}/api/connections/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        remaining2 = int(response2.headers.get("X-RateLimit-Remaining", "0"))
        
        # Remaining should decrease
        assert remaining2 < remaining1, f"Remaining should decrease: first={remaining1}, second={remaining2}"
        
        print(f"Rate limit remaining decreases correctly: {remaining1} -> {remaining2}")
    
    def test_health_endpoint_exempt_from_rate_limiting(self):
        """GET /api/health should NOT have rate limit headers (exempt)"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        # Health endpoint is exempt - should NOT have rate limit headers
        has_ratelimit_header = "X-RateLimit-Limit" in response.headers
        
        assert not has_ratelimit_header, "Health endpoint should be exempt from rate limiting"
        
        print("Health endpoint correctly exempted from rate limiting")
    
    def test_scoring_methodology_exempt_from_rate_limiting(self):
        """GET /api/scoring/methodology should NOT have rate limit headers (exempt)"""
        response = requests.get(f"{BASE_URL}/api/scoring/methodology")
        assert response.status_code == 200
        
        # scoring/methodology is in EXEMPT_PATHS - should NOT have rate limit headers
        has_ratelimit_header = "X-RateLimit-Limit" in response.headers
        
        assert not has_ratelimit_header, "Scoring methodology endpoint should be exempt from rate limiting"
        
        print("Scoring methodology endpoint correctly exempted from rate limiting")
    
    def test_auth_login_exempt_from_rate_limiting(self):
        """POST /api/auth/login should NOT have rate limit headers (exempt)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        # Auth endpoint is exempt - should NOT have rate limit headers
        has_ratelimit_header = "X-RateLimit-Limit" in response.headers
        
        assert not has_ratelimit_header, "Auth login endpoint should be exempt from rate limiting"
        
        print("Auth login endpoint correctly exempted from rate limiting")


class TestPlatformIntegrationsEndpoints:
    """Tests for new platform integrations (Etsy, BigCommerce, Squarespace)"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("token")
    
    def test_platforms_endpoint_includes_all_stores(self):
        """GET /api/connections/platforms should include all 5 store platforms"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200
        
        data = response.json()
        stores = data.get("stores", {})
        
        # Verify all 5 store platforms are present
        expected_stores = ["shopify", "woocommerce", "etsy", "bigcommerce", "squarespace"]
        for platform in expected_stores:
            assert platform in stores, f"Missing store platform: {platform}"
        
        print(f"All 5 store platforms present: {list(stores.keys())}")
    
    def test_etsy_config_has_store_url_field(self):
        """Etsy config should have store_url field (for Shop ID)"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200
        
        data = response.json()
        etsy_config = data.get("stores", {}).get("etsy", {})
        
        assert "store_url" in etsy_config.get("fields", []), "Etsy should have store_url field"
        assert "api_key" in etsy_config.get("fields", []), "Etsy should have api_key field"
        assert "access_token" in etsy_config.get("fields", []), "Etsy should have access_token field"
        
        print(f"Etsy config fields: {etsy_config.get('fields')}")
    
    def test_bigcommerce_config_has_correct_fields(self):
        """BigCommerce config should have store_url, api_key, access_token fields"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200
        
        data = response.json()
        bc_config = data.get("stores", {}).get("bigcommerce", {})
        
        assert "store_url" in bc_config.get("fields", []), "BigCommerce should have store_url field"
        assert "api_key" in bc_config.get("fields", []), "BigCommerce should have api_key field"
        assert "access_token" in bc_config.get("fields", []), "BigCommerce should have access_token field"
        
        print(f"BigCommerce config fields: {bc_config.get('fields')}")
    
    def test_squarespace_config_has_correct_fields(self):
        """Squarespace config should have store_url, api_key fields"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200
        
        data = response.json()
        sq_config = data.get("stores", {}).get("squarespace", {})
        
        assert "store_url" in sq_config.get("fields", []), "Squarespace should have store_url field"
        assert "api_key" in sq_config.get("fields", []), "Squarespace should have api_key field"
        
        print(f"Squarespace config fields: {sq_config.get('fields')}")
    
    def test_connect_etsy_store_endpoint(self, auth_token):
        """POST /api/connections/store should accept etsy platform"""
        response = requests.post(
            f"{BASE_URL}/api/connections/store",
            json={
                "platform": "etsy",
                "store_url": "12345678",  # Etsy Shop ID
                "api_key": "test-etsy-api-key",
                "access_token": "test-etsy-access-token"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should return 200 with success
        assert response.status_code == 200, f"Connect Etsy failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("platform") == "etsy"
        
        print(f"Etsy store connection: {data}")
    
    def test_connect_bigcommerce_store_endpoint(self, auth_token):
        """POST /api/connections/store should accept bigcommerce platform"""
        response = requests.post(
            f"{BASE_URL}/api/connections/store",
            json={
                "platform": "bigcommerce",
                "store_url": "https://store-abc123.mybigcommerce.com",
                "api_key": "test-bc-api-key",
                "access_token": "test-bc-access-token"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200, f"Connect BigCommerce failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("platform") == "bigcommerce"
        
        print(f"BigCommerce store connection: {data}")
    
    def test_connect_squarespace_store_endpoint(self, auth_token):
        """POST /api/connections/store should accept squarespace platform"""
        response = requests.post(
            f"{BASE_URL}/api/connections/store",
            json={
                "platform": "squarespace",
                "store_url": "https://mystore.squarespace.com",
                "api_key": "test-sq-api-key"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200, f"Connect Squarespace failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("platform") == "squarespace"
        
        print(f"Squarespace store connection: {data}")
    
    def test_invalid_platform_rejected(self, auth_token):
        """POST /api/connections/store should reject unsupported platform"""
        response = requests.post(
            f"{BASE_URL}/api/connections/store",
            json={
                "platform": "amazon",
                "store_url": "https://amazon.com",
                "api_key": "test-key"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400, f"Should reject invalid platform: {response.text}"
        
        print("Invalid platform correctly rejected")


class TestScoringMethodology:
    """Tests for scoring methodology endpoint (regression)"""
    
    def test_scoring_methodology_returns_7_signals(self):
        """GET /api/scoring/methodology should return 7 signals"""
        response = requests.get(f"{BASE_URL}/api/scoring/methodology")
        assert response.status_code == 200
        
        data = response.json()
        signals = data.get("signals", [])
        
        assert len(signals) == 7, f"Expected 7 signals, got {len(signals)}"
        
        expected_signals = [
            "Trend Score", "Margin Score", "Competition Score",
            "Ad Activity Score", "Supplier Demand Score", "Search Growth Score",
            "Order Velocity Score"
        ]
        
        signal_names = [s.get("name") for s in signals]
        for expected in expected_signals:
            assert expected in signal_names, f"Missing signal: {expected}"
        
        print(f"7 signals verified: {signal_names}")


class TestPlatformIntegrationFunctions:
    """Tests to verify platform integration functions exist in platform_integrations.py"""
    
    def test_publish_to_etsy_function_exists(self):
        """Verify publish_to_etsy function is importable"""
        from services.platform_integrations import publish_to_etsy
        assert callable(publish_to_etsy), "publish_to_etsy should be callable"
        print("publish_to_etsy function exists")
    
    def test_publish_to_bigcommerce_function_exists(self):
        """Verify publish_to_bigcommerce function is importable"""
        from services.platform_integrations import publish_to_bigcommerce
        assert callable(publish_to_bigcommerce), "publish_to_bigcommerce should be callable"
        print("publish_to_bigcommerce function exists")
    
    def test_publish_to_squarespace_function_exists(self):
        """Verify publish_to_squarespace function is importable"""
        from services.platform_integrations import publish_to_squarespace
        assert callable(publish_to_squarespace), "publish_to_squarespace should be callable"
        print("publish_to_squarespace function exists")


class TestConnectionsEndpointRouting:
    """Tests for connections routing to correct platform functions"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("token")
    
    def test_get_user_connections_includes_new_platforms(self, auth_token):
        """GET /api/connections/ should show connected new platforms"""
        response = requests.get(
            f"{BASE_URL}/api/connections/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        stores = data.get("stores", [])
        
        # Check if the test-connected platforms are listed
        platforms_connected = [s.get("platform") for s in stores]
        
        print(f"Connected store platforms: {platforms_connected}")
        
        # Should have etsy, bigcommerce, squarespace from previous tests
        assert "etsy" in platforms_connected, "Etsy should be in connected platforms"
        assert "bigcommerce" in platforms_connected, "BigCommerce should be in connected platforms"
        assert "squarespace" in platforms_connected, "Squarespace should be in connected platforms"
    
    def test_disconnect_test_platforms(self, auth_token):
        """Clean up: disconnect test platforms"""
        for platform in ["etsy", "bigcommerce", "squarespace"]:
            response = requests.delete(
                f"{BASE_URL}/api/connections/store/{platform}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            # May return 200 or 404 if already disconnected
            assert response.status_code in [200, 404], f"Disconnect {platform} failed: {response.text}"
            print(f"Disconnected {platform}: {response.status_code}")
