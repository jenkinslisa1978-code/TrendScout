"""
Tests for Shopify App packaging features:
- GET /api/shopify/app/info - App metadata endpoint
- POST /api/shopify/app/webhooks/customers/data_request - GDPR customer data request
- POST /api/shopify/app/webhooks/customers/redact - GDPR customer erasure
- POST /api/shopify/app/webhooks/shop/redact - GDPR shop data erasure
- POST /api/shopify/app/webhooks/app/uninstalled - App lifecycle uninstall webhook
"""
import pytest
import requests
import os
import json
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestShopifyAppInfo:
    """Tests for GET /api/shopify/app/info endpoint"""
    
    def test_app_info_returns_200(self):
        """App info endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/shopify/app/info returns 200")
    
    def test_app_info_contains_name(self):
        """App info should contain app name"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        data = response.json()
        assert "name" in data, "Missing 'name' field"
        assert data["name"] == "TrendScout", f"Expected 'TrendScout', got '{data['name']}'"
        print(f"PASS: App name is '{data['name']}'")
    
    def test_app_info_contains_version(self):
        """App info should contain version"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        data = response.json()
        assert "version" in data, "Missing 'version' field"
        assert data["version"] == "1.0.0", f"Expected '1.0.0', got '{data['version']}'"
        print(f"PASS: App version is '{data['version']}'")
    
    def test_app_info_contains_features(self):
        """App info should contain features list"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        data = response.json()
        assert "features" in data, "Missing 'features' field"
        assert isinstance(data["features"], list), "Features should be a list"
        assert len(data["features"]) > 0, "Features list should not be empty"
        expected_features = [
            "7-Signal Launch Score",
            "Ad Intelligence",
            "Competitor Store Analysis",
            "1-Click Product Import",
            "Real-time Radar Alerts",
        ]
        for feature_prefix in expected_features:
            matching = [f for f in data["features"] if feature_prefix in f]
            assert len(matching) > 0, f"Missing expected feature containing '{feature_prefix}'"
        print(f"PASS: App has {len(data['features'])} features")
    
    def test_app_info_contains_scopes(self):
        """App info should contain required scopes"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        data = response.json()
        assert "scopes_required" in data, "Missing 'scopes_required' field"
        expected_scopes = ["read_products", "write_products", "read_inventory", "write_inventory"]
        for scope in expected_scopes:
            assert scope in data["scopes_required"], f"Missing scope: {scope}"
        print(f"PASS: App requires scopes: {data['scopes_required']}")
    
    def test_app_info_contains_gdpr_endpoints(self):
        """App info should list GDPR endpoints"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        data = response.json()
        assert "gdpr_endpoints" in data, "Missing 'gdpr_endpoints' field"
        gdpr = data["gdpr_endpoints"]
        assert "customer_data_request" in gdpr, "Missing customer_data_request endpoint"
        assert "customer_redact" in gdpr, "Missing customer_redact endpoint"
        assert "shop_redact" in gdpr, "Missing shop_redact endpoint"
        # Verify endpoints are correct paths
        assert gdpr["customer_data_request"] == "/api/shopify/app/webhooks/customers/data_request"
        assert gdpr["customer_redact"] == "/api/shopify/app/webhooks/customers/redact"
        assert gdpr["shop_redact"] == "/api/shopify/app/webhooks/shop/redact"
        print(f"PASS: GDPR endpoints defined: {list(gdpr.keys())}")
    
    def test_app_info_contains_webhooks(self):
        """App info should list app lifecycle webhooks"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        data = response.json()
        assert "webhooks" in data, "Missing 'webhooks' field"
        assert "app_uninstalled" in data["webhooks"], "Missing app_uninstalled webhook"
        assert data["webhooks"]["app_uninstalled"] == "/api/shopify/app/webhooks/app/uninstalled"
        print(f"PASS: Webhooks defined: {list(data['webhooks'].keys())}")


class TestGDPRCustomerDataRequest:
    """Tests for POST /api/shopify/app/webhooks/customers/data_request endpoint"""
    
    def test_customer_data_request_returns_200(self):
        """GDPR customer data request should return 200"""
        payload = {
            "shop_domain": f"test-{uuid.uuid4().hex[:8]}.myshopify.com",
            "customer": {
                "id": 12345,
                "email": f"test-{uuid.uuid4().hex[:8]}@example.com"
            },
            "orders_requested": [1001, 1002]
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/customers/data_request",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: POST /api/shopify/app/webhooks/customers/data_request returns 200")
    
    def test_customer_data_request_response_structure(self):
        """Response should contain status: ok"""
        payload = {
            "shop_domain": f"test-{uuid.uuid4().hex[:8]}.myshopify.com",
            "customer": {
                "id": 12345,
                "email": f"test-{uuid.uuid4().hex[:8]}@example.com"
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/customers/data_request",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        assert "status" in data, "Missing 'status' in response"
        assert data["status"] == "ok", f"Expected status 'ok', got '{data['status']}'"
        print(f"PASS: Response status is '{data['status']}'")


class TestGDPRCustomerRedact:
    """Tests for POST /api/shopify/app/webhooks/customers/redact endpoint"""
    
    def test_customer_redact_returns_200(self):
        """GDPR customer redact should return 200"""
        payload = {
            "shop_domain": f"test-{uuid.uuid4().hex[:8]}.myshopify.com",
            "customer": {
                "id": 67890,
                "email": f"delete-{uuid.uuid4().hex[:8]}@example.com"
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/customers/redact",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: POST /api/shopify/app/webhooks/customers/redact returns 200")
    
    def test_customer_redact_response_structure(self):
        """Response should contain status: ok"""
        payload = {
            "shop_domain": f"test-{uuid.uuid4().hex[:8]}.myshopify.com",
            "customer": {
                "id": 11111,
                "email": f"redact-{uuid.uuid4().hex[:8]}@example.com"
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/customers/redact",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        assert "status" in data, "Missing 'status' in response"
        assert data["status"] == "ok", f"Expected status 'ok', got '{data['status']}'"
        print(f"PASS: Customer redact status is '{data['status']}'")


class TestGDPRShopRedact:
    """Tests for POST /api/shopify/app/webhooks/shop/redact endpoint"""
    
    def test_shop_redact_returns_200(self):
        """GDPR shop redact should return 200"""
        payload = {
            "shop_domain": f"test-{uuid.uuid4().hex[:8]}.myshopify.com",
            "shop_id": 999999
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/shop/redact",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: POST /api/shopify/app/webhooks/shop/redact returns 200")
    
    def test_shop_redact_response_structure(self):
        """Response should contain status: ok"""
        payload = {
            "shop_domain": f"test-{uuid.uuid4().hex[:8]}.myshopify.com",
            "shop_id": 888888
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/shop/redact",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        assert "status" in data, "Missing 'status' in response"
        assert data["status"] == "ok", f"Expected status 'ok', got '{data['status']}'"
        print(f"PASS: Shop redact status is '{data['status']}'")


class TestAppUninstallWebhook:
    """Tests for POST /api/shopify/app/webhooks/app/uninstalled endpoint"""
    
    def test_app_uninstalled_returns_200(self):
        """App uninstall webhook should return 200"""
        payload = {
            "domain": f"test-{uuid.uuid4().hex[:8]}.myshopify.com",
            "myshopify_domain": f"test-{uuid.uuid4().hex[:8]}.myshopify.com"
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/app/uninstalled",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: POST /api/shopify/app/webhooks/app/uninstalled returns 200")
    
    def test_app_uninstalled_response_structure(self):
        """Response should contain status: ok"""
        payload = {
            "domain": f"uninstall-{uuid.uuid4().hex[:8]}.myshopify.com"
        }
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/app/uninstalled",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        assert "status" in data, "Missing 'status' in response"
        assert data["status"] == "ok", f"Expected status 'ok', got '{data['status']}'"
        print(f"PASS: App uninstall status is '{data['status']}'")


class TestWebSocketRegressionCheck:
    """Quick regression check that WebSocket notification endpoint still exists"""
    
    def test_websocket_endpoint_exists(self):
        """WebSocket endpoint should exist (returns 405 for HTTP requests)"""
        response = requests.get(f"{BASE_URL}/api/notifications/ws")
        # WebSocket endpoint returns 405 when accessed via HTTP (expected)
        assert response.status_code == 405, f"Expected 405 (Method Not Allowed), got {response.status_code}"
        print("PASS: WebSocket endpoint /api/notifications/ws exists (returns 405 for HTTP)")
    
    def test_notifications_list_endpoint(self):
        """Notifications list endpoint should require auth"""
        response = requests.get(f"{BASE_URL}/api/notifications/")
        # Should return 401 without auth
        assert response.status_code == 401, f"Expected 401 (Unauthorized), got {response.status_code}"
        print("PASS: GET /api/notifications/ requires authentication (returns 401)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
