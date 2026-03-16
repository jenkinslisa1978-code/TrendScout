"""
Tests for Shopify App Bridge / Embedded App Integration:
- GET /api/shopify/app/embedded/dashboard - Embedded dashboard data
- POST /api/shopify/app/session-token - Session token verification
- Regression: GDPR endpoints still work
- Regression: WebSocket notifications still work
"""
import pytest
import requests
import os
import json
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEmbeddedDashboard:
    """Tests for GET /api/shopify/app/embedded/dashboard endpoint"""
    
    def test_embedded_dashboard_returns_200_with_shop(self):
        """Embedded dashboard should return 200 with valid shop param"""
        shop = "test.myshopify.com"
        response = requests.get(f"{BASE_URL}/api/shopify/app/embedded/dashboard?shop={shop}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"PASS: GET /api/shopify/app/embedded/dashboard?shop={shop} returns 200")
    
    def test_embedded_dashboard_response_structure(self):
        """Response should contain trending_products, recent_exports, radar_detections"""
        shop = "test.myshopify.com"
        response = requests.get(f"{BASE_URL}/api/shopify/app/embedded/dashboard?shop={shop}")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "trending_products" in data, "Missing 'trending_products' field"
        assert "recent_exports" in data, "Missing 'recent_exports' field"
        assert "radar_detections" in data, "Missing 'radar_detections' field"
        assert "shop" in data, "Missing 'shop' field"
        assert "connected" in data, "Missing 'connected' field"
        
        # Check types
        assert isinstance(data["trending_products"], list), "trending_products should be a list"
        assert isinstance(data["recent_exports"], list), "recent_exports should be a list"
        assert isinstance(data["radar_detections"], list), "radar_detections should be a list"
        assert data["shop"] == shop, f"Expected shop '{shop}', got '{data['shop']}'"
        
        print(f"PASS: Response contains trending_products ({len(data['trending_products'])}), recent_exports ({len(data['recent_exports'])}), radar_detections ({len(data['radar_detections'])})")
    
    def test_embedded_dashboard_requires_shop_param(self):
        """Embedded dashboard should return 400 without shop param"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/embedded/dashboard")
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
        print(f"PASS: GET /api/shopify/app/embedded/dashboard without shop returns {response.status_code}")
    
    def test_embedded_dashboard_returns_empty_shop_400(self):
        """Embedded dashboard should return 400 with empty shop param"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/embedded/dashboard?shop=")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: GET /api/shopify/app/embedded/dashboard with empty shop returns 400")


class TestSessionToken:
    """Tests for POST /api/shopify/app/session-token endpoint"""
    
    def test_session_token_rejects_empty_body(self):
        """Session token endpoint should reject empty body with 400"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/session-token",
            json={},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data or "error" in data, "Response should contain error detail"
        print(f"PASS: POST /api/shopify/app/session-token with empty body returns 400")
    
    def test_session_token_rejects_empty_token(self):
        """Session token endpoint should reject empty session_token with 400"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/session-token",
            json={"session_token": ""},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: POST /api/shopify/app/session-token with empty token returns 400")
    
    def test_session_token_rejects_invalid_token(self):
        """Session token endpoint should reject invalid tokens with 401"""
        # Use a fake malformed JWT
        invalid_token = "invalid.token.here"
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/session-token",
            json={"session_token": invalid_token},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        data = response.json()
        assert "detail" in data or "error" in data, "Response should contain error detail"
        print("PASS: POST /api/shopify/app/session-token with invalid token returns 401")
    
    def test_session_token_rejects_tampered_jwt(self):
        """Session token endpoint should reject tampered JWT with 401"""
        # Create a fake JWT structure that will fail signature verification
        fake_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZGVzdCI6Imh0dHBzOi8vdGVzdC5teXNob3BpZnkuY29tIiwiaWF0IjoxNjE2MjM5MDIyfQ.fakeSignature123"
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/session-token",
            json={"session_token": fake_jwt},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: POST /api/shopify/app/session-token with tampered JWT returns 401")


class TestGDPREndpointsRegression:
    """Regression tests for GDPR endpoints - verifies they exist and enforce HMAC"""
    
    def test_customer_data_request_endpoint_exists(self):
        """GDPR customer data request endpoint should exist (requires HMAC when secret is set)"""
        payload = {
            "shop_domain": f"regression-{uuid.uuid4().hex[:8]}.myshopify.com",
            "customer": {"id": 12345, "email": f"test-{uuid.uuid4().hex[:8]}@example.com"}
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/customers/data_request",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        # Returns 401 when SHOPIFY_CLIENT_SECRET is set but no valid HMAC provided
        # Returns 200 when secret is not set
        assert response.status_code in [200, 401], f"Expected 200 or 401, got {response.status_code}"
        print(f"PASS: GDPR customer data request endpoint exists (returns {response.status_code})")
    
    def test_customer_redact_endpoint_exists(self):
        """GDPR customer redact endpoint should exist (requires HMAC when secret is set)"""
        payload = {
            "shop_domain": f"regression-{uuid.uuid4().hex[:8]}.myshopify.com",
            "customer": {"id": 67890, "email": f"redact-{uuid.uuid4().hex[:8]}@example.com"}
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/customers/redact",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [200, 401], f"Expected 200 or 401, got {response.status_code}"
        print(f"PASS: GDPR customer redact endpoint exists (returns {response.status_code})")
    
    def test_shop_redact_endpoint_exists(self):
        """GDPR shop redact endpoint should exist (requires HMAC when secret is set)"""
        payload = {
            "shop_domain": f"regression-{uuid.uuid4().hex[:8]}.myshopify.com",
            "shop_id": 999999
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/shop/redact",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [200, 401], f"Expected 200 or 401, got {response.status_code}"
        print(f"PASS: GDPR shop redact endpoint exists (returns {response.status_code})")


class TestAppInfoRegression:
    """Regression tests for app info endpoint"""
    
    def test_app_info_still_works(self):
        """App info endpoint should still return 200 with expected data"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("name") == "TrendScout"
        assert data.get("version") == "1.0.0"
        assert "features" in data
        assert "gdpr_endpoints" in data
        print("PASS: App info endpoint still works")


class TestWebSocketRegression:
    """Regression tests for WebSocket notifications"""
    
    def test_websocket_endpoint_exists(self):
        """WebSocket endpoint should exist (returns 405 for HTTP)"""
        response = requests.get(f"{BASE_URL}/api/notifications/ws")
        assert response.status_code == 405, f"Expected 405, got {response.status_code}"
        print("PASS: WebSocket endpoint /api/notifications/ws exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
