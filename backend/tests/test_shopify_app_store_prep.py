"""
Test Suite: Shopify App Store Preparation
Tests email updates, privacy/terms content, GDPR webhooks, and reviewer account
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthCheck:
    """Verify backend is running"""
    
    def test_health_check_returns_ok(self):
        """GET /api/health should return status ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"


class TestShopifyAppInfo:
    """Test /api/shopify/app/info endpoint for correct email and metadata"""
    
    def test_app_info_returns_correct_support_email(self):
        """App info should use info@trendscout.click as support email"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        assert response.status_code == 200
        data = response.json()
        assert data.get("support_email") == "info@trendscout.click", "Support email should be info@trendscout.click"
    
    def test_app_info_has_gdpr_endpoints(self):
        """App info should list GDPR endpoint paths"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        assert response.status_code == 200
        data = response.json()
        gdpr = data.get("gdpr_endpoints", {})
        assert gdpr.get("customer_data_request") == "/api/shopify/app/webhooks/customers/data_request"
        assert gdpr.get("customer_redact") == "/api/shopify/app/webhooks/customers/redact"
        assert gdpr.get("shop_redact") == "/api/shopify/app/webhooks/shop/redact"
    
    def test_app_info_has_correct_privacy_terms_urls(self):
        """App info should have correct privacy and terms URLs"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        assert response.status_code == 200
        data = response.json()
        assert data.get("privacy_policy") == "/privacy"
        assert data.get("terms_of_service") == "/terms"


class TestGDPRWebhooks:
    """Test GDPR mandatory webhooks - expect 401 without HMAC verification"""
    
    def test_customer_data_request_webhook_exists(self):
        """POST /api/shopify/app/webhooks/customers/data_request should return 401 without HMAC"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/customers/data_request",
            json={"shop_domain": "test.myshopify.com", "customer": {"email": "test@test.com"}}
        )
        # 401 is expected without proper HMAC header - endpoint exists
        assert response.status_code == 401, "GDPR customer data request endpoint should require HMAC verification"
    
    def test_customer_redact_webhook_exists(self):
        """POST /api/shopify/app/webhooks/customers/redact should return 401 without HMAC"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/customers/redact",
            json={"shop_domain": "test.myshopify.com", "customer": {"email": "test@test.com"}}
        )
        assert response.status_code == 401, "GDPR customer redact endpoint should require HMAC verification"
    
    def test_shop_redact_webhook_exists(self):
        """POST /api/shopify/app/webhooks/shop/redact should return 401 without HMAC"""
        response = requests.post(
            f"{BASE_URL}/api/shopify/app/webhooks/shop/redact",
            json={"shop_domain": "test.myshopify.com", "shop_id": "12345"}
        )
        assert response.status_code == 401, "GDPR shop redact endpoint should require HMAC verification"


class TestReviewerAccount:
    """Test reviewer account can log in"""
    
    def test_reviewer_login_succeeds(self):
        """Reviewer account reviewer@trendscout.click should be able to log in"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "reviewer@trendscout.click", "password": "ShopifyReview2026!"}
        )
        assert response.status_code == 200, "Reviewer account should be able to log in"
        data = response.json()
        assert "token" in data, "Login should return a token"
        assert data.get("user", {}).get("email") == "reviewer@trendscout.click"


class TestTestUserAccount:
    """Test main test user account can log in"""
    
    def test_admin_login_succeeds(self):
        """Test user jenkinslisa1978@gmail.com should be able to log in"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "jenkinslisa1978@gmail.com", "password": "admin123456"}
        )
        assert response.status_code == 200, "Test user should be able to log in"
        data = response.json()
        assert "token" in data
        assert data.get("user", {}).get("email") == "jenkinslisa1978@gmail.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
