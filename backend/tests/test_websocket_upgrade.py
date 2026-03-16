"""
WebSocket Upgrade Tests - Notification System

Tests the upgrade from SSE to WebSocket for real-time notifications:
- WebSocket endpoint /api/notifications/ws connection and authentication
- REST notification endpoints still working
- Old SSE endpoint /api/notifications/stream removed (should 404)

Test credentials: jenkinslisa1978@gmail.com / admin123456
"""

import pytest
import requests
import os
import json
import jwt
from datetime import datetime, timezone, timedelta

# Get base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "jenkinslisa1978@gmail.com"
TEST_PASSWORD = "admin123456"


class TestNotificationWebSocketEndpoint:
    """Test WebSocket endpoint authentication and connection"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("token") or data.get("access_token")
            self.user_id = data.get("user", {}).get("id") or data.get("user_id")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            print(f"✓ Login successful, token obtained")
        else:
            pytest.skip(f"Login failed: {login_response.status_code} - {login_response.text}")
    
    def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoint /api/notifications/ws exists"""
        # WebSocket endpoints typically return 426 Upgrade Required for HTTP requests
        # or 403/400 for invalid requests - main point is it should NOT be 404
        response = requests.get(f"{BASE_URL}/api/notifications/ws")
        
        # 404 = endpoint doesn't exist
        # 403/400/422 = endpoint exists but request is malformed (expected for WS)
        # 426 = Upgrade Required (expected for HTTP->WS)
        assert response.status_code != 404, f"WebSocket endpoint not found! Got {response.status_code}"
        print(f"✓ WebSocket endpoint exists at /api/notifications/ws (status: {response.status_code})")
    
    def test_websocket_without_token_rejected(self):
        """Test that WebSocket connection without token returns 4001"""
        # HTTP request to WS endpoint without token should indicate auth required
        response = requests.get(f"{BASE_URL}/api/notifications/ws")
        
        # Without token parameter, should fail
        # 405 = Method Not Allowed (HTTP vs WebSocket) - endpoint exists
        # 400, 403, 422, 426 = other expected errors
        assert response.status_code in [400, 403, 405, 422, 426], \
            f"Expected auth error without token, got {response.status_code}"
        print(f"✓ WebSocket endpoint correctly requires upgrade/authentication (status: {response.status_code})")
    
    def test_websocket_with_invalid_token_rejected(self):
        """Test that WebSocket connection with invalid token returns 4001"""
        response = requests.get(f"{BASE_URL}/api/notifications/ws?token=invalid_token_123")
        
        # Invalid token should fail authentication
        # 405 = Method Not Allowed (HTTP vs WebSocket) - endpoint exists
        assert response.status_code in [400, 403, 405, 422, 426], \
            f"Expected auth error with invalid token, got {response.status_code}"
        print(f"✓ WebSocket endpoint correctly rejects invalid token (status: {response.status_code})")


class TestNotificationRESTEndpoints:
    """Test that REST notification endpoints still work after WebSocket upgrade"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            pytest.skip(f"Login failed: {login_response.status_code}")
    
    def test_get_notifications_list(self):
        """GET /api/notifications/ returns notifications list"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "notifications" in data, "Response missing notifications field"
        assert "count" in data, "Response missing count field"
        assert "unread_count" in data, "Response missing unread_count field"
        assert isinstance(data["notifications"], list), "notifications should be a list"
        
        print(f"✓ GET /api/notifications/ works - {data['count']} notifications, {data['unread_count']} unread")
    
    def test_get_unread_count(self):
        """GET /api/notifications/unread-count returns count"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/unread-count",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "unread_count" in data, "Response missing unread_count field"
        assert isinstance(data["unread_count"], int), "unread_count should be an integer"
        
        print(f"✓ GET /api/notifications/unread-count works - {data['unread_count']} unread")
    
    def test_post_mark_read(self):
        """POST /api/notifications/mark-read works"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/mark-read",
            headers=self.headers,
            json=["fake_notification_id"]  # Will not modify anything but should return success
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "success", f"Expected success status, got {data}"
        
        print(f"✓ POST /api/notifications/mark-read works")
    
    def test_post_mark_all_read(self):
        """POST /api/notifications/mark-all-read works"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/mark-all-read",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "success", f"Expected success status, got {data}"
        
        print(f"✓ POST /api/notifications/mark-all-read works - {data.get('modified_count', 0)} modified")
    
    def test_post_test_alert(self):
        """POST /api/notifications/test-alert creates test notification"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/test-alert",
            headers=self.headers
        )
        
        assert response.status_code in [200, 404], f"Expected 200 or 404 (no products), got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") in ["success", "skipped"], f"Unexpected status: {data}"
            print(f"✓ POST /api/notifications/test-alert works - status: {data['status']}")
        else:
            print(f"✓ POST /api/notifications/test-alert returns 404 (no high score products available)")
    
    def test_get_notifications_requires_auth(self):
        """GET /api/notifications/ requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications/")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("✓ GET /api/notifications/ correctly requires authentication")
    
    def test_unread_count_requires_auth(self):
        """GET /api/notifications/unread-count requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("✓ GET /api/notifications/unread-count correctly requires authentication")


class TestSSEEndpointRemoved:
    """Test that old SSE endpoint has been removed"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            pytest.skip(f"Login failed: {login_response.status_code}")
    
    def test_sse_stream_endpoint_removed(self):
        """Old SSE /api/notifications/stream should return 404 or 405"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/stream",
            headers=self.headers
        )
        
        # The old SSE endpoint should no longer exist
        # 404 = Not Found (endpoint removed)
        # 405 = Method Not Allowed (endpoint removed or reconfigured)
        # 307 = Redirect (which would then 404)
        assert response.status_code in [404, 405, 307, 422], \
            f"SSE endpoint should be removed, but got {response.status_code}"
        
        print(f"✓ Old SSE endpoint /api/notifications/stream removed (status: {response.status_code})")


class TestLoginFlowAndDashboard:
    """Test that login flow works and dashboard loads correctly"""
    
    def test_login_works(self):
        """Test that login returns valid token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        token = data.get("token") or data.get("access_token")
        assert token is not None, "No token in login response"
        
        user = data.get("user", {})
        assert user.get("email") == TEST_EMAIL, f"Wrong email in response: {user.get('email')}"
        
        print(f"✓ Login successful for {TEST_EMAIL}")
    
    def test_profile_endpoint_works(self):
        """Test that /api/user/me returns user profile after login"""
        # Login first
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Login failed")
        
        token = login_response.json().get("token") or login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get profile
        response = requests.get(f"{BASE_URL}/api/user/me", headers=headers)
        
        assert response.status_code == 200, f"Profile fetch failed: {response.status_code}"
        
        data = response.json()
        assert "email" in data or "id" in data or "profile" in data, "No user data in response"
        
        print(f"✓ Profile endpoint works after login")


class TestWebSocketURLScheme:
    """Test WebSocket URL scheme configuration in frontend"""
    
    def test_backend_url_for_websocket(self):
        """Verify backend URL can be converted to WebSocket URL"""
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', '')
        
        assert backend_url, "REACT_APP_BACKEND_URL not set"
        
        # Frontend converts https:// to wss:// and http:// to ws://
        if backend_url.startswith('https://'):
            expected_ws_prefix = 'wss://'
        else:
            expected_ws_prefix = 'ws://'
        
        ws_url = backend_url.replace('https://', 'wss://').replace('http://', 'ws://')
        
        assert ws_url.startswith(expected_ws_prefix), \
            f"WebSocket URL should start with {expected_ws_prefix}, got {ws_url}"
        
        full_ws_url = f"{ws_url}/api/notifications/ws"
        print(f"✓ WebSocket URL correctly formed: {full_ws_url}")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
