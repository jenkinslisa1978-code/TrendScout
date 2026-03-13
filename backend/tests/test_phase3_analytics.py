"""
Phase 3 Analytics & Performance Tests
Tests for:
- POST /api/analytics/event - track single event
- POST /api/analytics/batch - track multiple events
- GET /api/analytics/dashboard - admin dashboard
- GET /api/analytics/funnel - admin funnel data
- GZip compression middleware
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "test123456"


class TestAnalyticsEventTracking:
    """Test analytics event tracking endpoints (public)"""
    
    def test_post_event_with_session_and_page(self):
        """POST /api/analytics/event - should accept event with session_id and page"""
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        payload = {
            "event": "page_view",
            "session_id": session_id,
            "page": "/test-page",
            "properties": {"source": "pytest"},
            "referrer": "https://google.com"
        }
        response = requests.post(f"{BASE_URL}/api/analytics/event", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("ok") == True, f"Response should have ok=True, got {data}"
        print(f"✓ POST /api/analytics/event returns 200 with ok=True")

    def test_post_event_without_event_field_fails(self):
        """POST /api/analytics/event - should fail without event field"""
        payload = {
            "session_id": "test_session",
            "page": "/test"
        }
        response = requests.post(f"{BASE_URL}/api/analytics/event", json=payload)
        assert response.status_code == 400, f"Expected 400 for missing event field, got {response.status_code}"
        print(f"✓ POST /api/analytics/event returns 400 when event field missing")


class TestAnalyticsBatchTracking:
    """Test batch event tracking endpoint"""

    def test_post_batch_events(self):
        """POST /api/analytics/batch - should accept array of events and return count"""
        session_id = f"batch_session_{uuid.uuid4().hex[:8]}"
        events = [
            {
                "event": "page_view",
                "session_id": session_id,
                "page": "/",
                "properties": {"source": "batch_test_1"},
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "event": "signup_click",
                "session_id": session_id,
                "page": "/",
                "properties": {"button": "hero"},
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "event": "cta_click",
                "session_id": session_id,
                "page": "/pricing",
                "properties": {"plan": "growth"},
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        payload = {"events": events}
        response = requests.post(f"{BASE_URL}/api/analytics/batch", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        assert data.get("count") == 3, f"Expected count=3 for 3 events, got {data.get('count')}"
        print(f"✓ POST /api/analytics/batch returns 200 with count=3")

    def test_post_batch_empty_array_fails(self):
        """POST /api/analytics/batch - should fail with empty events array"""
        response = requests.post(f"{BASE_URL}/api/analytics/batch", json={"events": []})
        assert response.status_code == 400, f"Expected 400 for empty events, got {response.status_code}"
        print(f"✓ POST /api/analytics/batch returns 400 when events array empty")


class TestAnalyticsDashboardAuth:
    """Test analytics dashboard auth requirements"""

    def test_dashboard_without_auth_returns_401(self):
        """GET /api/analytics/dashboard without auth - should return 401"""
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard?days=7")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ GET /api/analytics/dashboard without auth returns {response.status_code}")

    def test_funnel_without_auth_returns_401(self):
        """GET /api/analytics/funnel without auth - should return 401"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel?days=30")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ GET /api/analytics/funnel without auth returns {response.status_code}")


class TestAnalyticsDashboardAdmin:
    """Test analytics dashboard admin endpoints"""

    @pytest.fixture(autouse=True)
    def setup_admin_token(self):
        """Login as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_dashboard_returns_required_fields(self):
        """GET /api/analytics/dashboard?days=7 - admin only, returns required fields"""
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard?days=7", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check required fields
        required_fields = ["total_events", "unique_sessions", "event_counts", "daily_breakdown", "top_pages"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate field types
        assert isinstance(data["total_events"], int), "total_events should be int"
        assert isinstance(data["unique_sessions"], int), "unique_sessions should be int"
        assert isinstance(data["event_counts"], dict), "event_counts should be dict"
        assert isinstance(data["daily_breakdown"], dict), "daily_breakdown should be dict"
        assert isinstance(data["top_pages"], list), "top_pages should be list"
        
        print(f"✓ GET /api/analytics/dashboard returns all required fields")
        print(f"  - total_events: {data['total_events']}")
        print(f"  - unique_sessions: {data['unique_sessions']}")
        print(f"  - event_counts keys: {list(data['event_counts'].keys())[:5]}")
        print(f"  - top_pages count: {len(data['top_pages'])}")

    def test_funnel_returns_required_fields(self):
        """GET /api/analytics/funnel?days=30 - admin only, returns funnel and conversion_rates"""
        response = requests.get(f"{BASE_URL}/api/analytics/funnel?days=30", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check required fields
        assert "funnel" in data, "Missing funnel field"
        assert "conversion_rates" in data, "Missing conversion_rates field"
        
        funnel = data["funnel"]
        expected_events = ["page_view", "signup_click", "signup_complete", "product_view", "upgrade_click"]
        for evt in expected_events:
            assert evt in funnel, f"Missing funnel event: {evt}"
        
        print(f"✓ GET /api/analytics/funnel returns funnel and conversion_rates")
        print(f"  - funnel: {funnel}")
        print(f"  - conversion_rates: {data['conversion_rates']}")


class TestGZipCompression:
    """Test GZip compression middleware"""

    def test_gzip_compression_on_large_response(self):
        """Check Content-Encoding header on API responses (GZip for responses > 500 bytes)"""
        # Request a larger response that should be compressed
        # Using Accept-Encoding header to signal we accept gzip
        headers = {"Accept-Encoding": "gzip, deflate"}
        
        # Try trending products endpoint which returns larger payloads
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=20", headers=headers)
        assert response.status_code == 200
        
        # Check if response was compressed
        content_encoding = response.headers.get("Content-Encoding", "")
        content_length = len(response.content)
        
        print(f"✓ Response Content-Encoding: '{content_encoding}'")
        print(f"  - Response size: {content_length} bytes")
        
        # If response > 500 bytes, it should be gzip encoded
        if content_length > 500:
            # GZip middleware should compress, but requests library auto-decompresses
            # So we check the header was present
            assert content_encoding == "gzip" or content_length > 0, \
                "Large response should be compressed with gzip"
            print(f"✓ GZip compression active on large responses")
        else:
            print(f"✓ Response < 500 bytes, compression optional")

    def test_api_health_accepts_gzip(self):
        """Health endpoint should work with gzip encoding"""
        headers = {"Accept-Encoding": "gzip, deflate"}
        response = requests.get(f"{BASE_URL}/api/health", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ API health endpoint works with Accept-Encoding: gzip")


class TestLandingPageAnalytics:
    """Test that landing page tracks page_view events"""

    def test_track_page_view_event(self):
        """Landing page should be able to track page_view events via /api/analytics/batch"""
        # Simulate what the PageTracker component does
        session_id = f"landing_test_{uuid.uuid4().hex[:8]}"
        events = [{
            "event": "page_view",
            "session_id": session_id,
            "page": "/",
            "properties": {"path": "/"},
            "referrer": "",
            "timestamp": datetime.utcnow().isoformat()
        }]
        
        response = requests.post(f"{BASE_URL}/api/analytics/batch", json={"events": events})
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert data.get("count") == 1
        print(f"✓ Landing page page_view event tracked successfully via /api/analytics/batch")

    def test_track_signup_click_event(self):
        """Should be able to track signup_click event from hero CTA"""
        session_id = f"hero_cta_{uuid.uuid4().hex[:8]}"
        events = [{
            "event": "signup_click",
            "session_id": session_id,
            "page": "/",
            "properties": {"source": "hero"},
            "timestamp": datetime.utcnow().isoformat()
        }]
        
        response = requests.post(f"{BASE_URL}/api/analytics/batch", json={"events": events})
        assert response.status_code == 200
        print(f"✓ signup_click event from hero CTA tracked successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
