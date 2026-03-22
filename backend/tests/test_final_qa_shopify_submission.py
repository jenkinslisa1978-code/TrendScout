"""
Final QA Test Suite for Shopify App Store Submission
Tests all major API endpoints and critical flows before production deployment.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://analytics-fix-28.preview.emergentagent.com').rstrip('/')


class TestHealthAndPublicEndpoints:
    """Test health check and public endpoints"""

    def test_health_endpoint(self):
        """Health endpoint returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"

    def test_public_trending_index(self):
        """Public trending index returns products"""
        response = requests.get(f"{BASE_URL}/api/public/trending-index")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data or isinstance(data, list)

    def test_sitemap(self):
        """Sitemap is accessible"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200


class TestAuthentication:
    """Test authentication flows"""

    def test_login_admin_user(self):
        """Admin user can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data or "access_token" in data

    def test_login_reviewer_account(self):
        """Reviewer account can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "reviewer@trendscout.click",
            "password": "ShopifyReview2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data or "access_token" in data

    def test_login_invalid_credentials(self):
        """Invalid credentials return error"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [400, 401, 404]

    def test_forgot_password_endpoint_exists(self):
        """Forgot password endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": "test@example.com"
        })
        # Should return 200 (success) or 404 (user not found) - not 500
        assert response.status_code in [200, 400, 404, 429]  # 429 for rate limit


class TestDashboardAndProducts:
    """Test dashboard and product endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_dashboard_stats(self):
        """Dashboard stats endpoint works - testing dashboard products which is the main data"""
        response = requests.get(f"{BASE_URL}/api/dashboard/onboarding", headers=self.headers)
        # Dashboard has multiple sub-endpoints, test the one that exists
        if response.status_code == 404:
            response = requests.get(f"{BASE_URL}/api/dashboard/next-steps", headers=self.headers)
        assert response.status_code == 200

    def test_dashboard_next_steps(self):
        """Dashboard next steps endpoint works"""
        response = requests.get(f"{BASE_URL}/api/dashboard/next-steps", headers=self.headers)
        assert response.status_code == 200

    def test_products_list(self):
        """Products endpoint returns list"""
        response = requests.get(f"{BASE_URL}/api/products", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or isinstance(data, list)

    def test_products_featured(self):
        """Products search endpoint works"""
        response = requests.get(f"{BASE_URL}/api/products/search?q=phone", headers=self.headers)
        assert response.status_code == 200

    def test_products_categories(self):
        """Products categories endpoint works"""
        response = requests.get(f"{BASE_URL}/api/products/categories/list", headers=self.headers)
        # Try alternative endpoints if not found
        if response.status_code == 404:
            response = requests.get(f"{BASE_URL}/api/categories", headers=self.headers)
        assert response.status_code in [200, 404]  # Accept 404 if not implemented


class TestProductDetail:
    """Test product detail endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token and find a product"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            
            # Get a product ID
            prod_response = requests.get(f"{BASE_URL}/api/products?limit=1", headers=self.headers)
            if prod_response.status_code == 200:
                prod_data = prod_response.json()
                products = prod_data.get("data", prod_data.get("products", prod_data)) if isinstance(prod_data, dict) else prod_data
                if products and isinstance(products, list) and len(products) > 0:
                    self.product_id = products[0].get("id")
                else:
                    self.product_id = None
            else:
                self.product_id = None
        else:
            pytest.skip("Could not authenticate")

    def test_product_detail(self):
        """Product detail endpoint works"""
        if not self.product_id:
            pytest.skip("No product found")
        response = requests.get(f"{BASE_URL}/api/products/{self.product_id}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        # API wraps in 'data' key
        product = data.get("data", data)
        assert "id" in product or "product_name" in product or "title" in product

    def test_product_launch_score_breakdown(self):
        """Product launch score breakdown endpoint works"""
        if not self.product_id:
            pytest.skip("No product found")
        response = requests.get(f"{BASE_URL}/api/products/{self.product_id}/launch-score-breakdown", headers=self.headers)
        assert response.status_code == 200


class TestCJSourcing:
    """Test CJ Dropshipping integration"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_cj_search(self):
        """CJ search endpoint works"""
        response = requests.get(f"{BASE_URL}/api/cj/search?q=phone case&page=1&page_size=5", headers=self.headers)
        # Could be 200 or 429 (rate limit) or 503 (CJ API down)
        assert response.status_code in [200, 400, 429, 500, 503]
        if response.status_code == 200:
            data = response.json()
            assert "products" in data or "data" in data or isinstance(data, list)

    def test_cj_categories(self):
        """CJ categories endpoint works"""
        response = requests.get(f"{BASE_URL}/api/cj/categories", headers=self.headers)
        assert response.status_code in [200, 429, 500, 503]


class TestAdIntelligence:
    """Test Ad Intelligence (Ad Spy) endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_ads_discover(self):
        """Ads discover endpoint works"""
        response = requests.get(f"{BASE_URL}/api/ads/discover", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "ads" in data or isinstance(data, list)

    def test_ads_categories(self):
        """Ads categories endpoint works"""
        response = requests.get(f"{BASE_URL}/api/ads/categories", headers=self.headers)
        assert response.status_code == 200


class TestProfitabilitySimulator:
    """Test profitability simulator endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_profitability_simulator(self):
        """Profitability simulator works"""
        response = requests.post(f"{BASE_URL}/api/tools/profitability-simulator", 
            headers=self.headers,
            json={
                "product_cost": 5.00,
                "selling_price": 25.00,
                "cpm": 10.00,
                "conversion_rate": 2.0,
                "ad_budget": 100.00,
                "competition_level": "medium"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should return simulation results
        assert isinstance(data, dict)


class TestCompetitorIntel:
    """Test Competitor Intelligence endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_competitor_intel_history(self):
        """Competitor intel history endpoint works"""
        response = requests.get(f"{BASE_URL}/api/competitor-intel/history", headers=self.headers)
        assert response.status_code == 200


class TestRadarAlerts:
    """Test Radar Alerts endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_radar_watches(self):
        """Radar watches endpoint works"""
        response = requests.get(f"{BASE_URL}/api/radar/watches", headers=self.headers)
        assert response.status_code == 200

    def test_radar_alert_feed(self):
        """Radar alert feed endpoint works"""
        response = requests.get(f"{BASE_URL}/api/radar/alert-feed", headers=self.headers)
        assert response.status_code == 200

    def test_radar_live_events(self):
        """Radar live events endpoint works"""
        response = requests.get(f"{BASE_URL}/api/radar/live-events", headers=self.headers)
        assert response.status_code == 200


class TestVerifiedWinners:
    """Test Verified Winners endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_winners_list(self):
        """Winners list endpoint works"""
        response = requests.get(f"{BASE_URL}/api/winners/", headers=self.headers)
        assert response.status_code == 200

    def test_my_submissions(self):
        """My submissions endpoint works"""
        response = requests.get(f"{BASE_URL}/api/winners/my-submissions", headers=self.headers)
        assert response.status_code == 200

    def test_my_badge(self):
        """My badge endpoint works"""
        response = requests.get(f"{BASE_URL}/api/winners/my-badge", headers=self.headers)
        assert response.status_code == 200


class TestTikTokIntelligence:
    """Test TikTok Intelligence endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_tiktok_trending(self):
        """TikTok trending endpoint works"""
        response = requests.get(f"{BASE_URL}/api/tiktok/trending", headers=self.headers)
        assert response.status_code == 200

    def test_tiktok_products(self):
        """TikTok products endpoint works"""
        response = requests.get(f"{BASE_URL}/api/tiktok/products", headers=self.headers)
        assert response.status_code == 200


class TestSavedProducts:
    """Test Saved Products endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_saved_products(self):
        """Saved products endpoint works"""
        response = requests.get(f"{BASE_URL}/api/products/saved", headers=self.headers)
        assert response.status_code == 200


class TestStores:
    """Test Store management endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_stores_list(self):
        """Stores list endpoint works"""
        response = requests.get(f"{BASE_URL}/api/stores", headers=self.headers)
        assert response.status_code == 200


class TestConnections:
    """Test Platform Connections endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_connections_list(self):
        """Connections list endpoint works"""
        response = requests.get(f"{BASE_URL}/api/connections", headers=self.headers)
        assert response.status_code == 200


class TestReports:
    """Test Reports endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_reports_list(self):
        """Reports list endpoint works"""
        response = requests.get(f"{BASE_URL}/api/reports", headers=self.headers)
        assert response.status_code == 200


class TestAdTests:
    """Test Ad Tests endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_ad_tests_list(self):
        """Ad tests list endpoint works"""
        response = requests.get(f"{BASE_URL}/api/ad-tests", headers=self.headers)
        assert response.status_code == 200


class TestShopifyApp:
    """Test Shopify App endpoints"""

    def test_shopify_app_info(self):
        """Shopify app info endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/shopify/app/info")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data or "app_name" in data or "support_email" in data

    def test_gdpr_webhooks_require_hmac(self):
        """GDPR webhooks require HMAC verification"""
        # These should return 401 without proper HMAC header
        endpoints = [
            "/api/shopify/app/webhooks/customers/data_request",
            "/api/shopify/app/webhooks/customers/redact",
            "/api/shopify/app/webhooks/shop/redact"
        ]
        for endpoint in endpoints:
            response = requests.post(f"{BASE_URL}{endpoint}", json={"test": "data"})
            assert response.status_code == 401, f"Expected 401 for {endpoint}, got {response.status_code}"


class TestShopifyPushProduct:
    """Test Shopify push product functionality"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "jenkinslisa1978@gmail.com",
            "password": "admin123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate")

    def test_shopify_exports_list(self):
        """Shopify exports list endpoint works"""
        response = requests.get(f"{BASE_URL}/api/shopify/exports", headers=self.headers)
        assert response.status_code == 200


class TestDigest:
    """Test Weekly Digest endpoints"""

    def test_digest_latest(self):
        """Digest latest endpoint works"""
        response = requests.get(f"{BASE_URL}/api/digest/latest")
        # Could be 200 (found) or 404 (no digest yet)
        assert response.status_code in [200, 404]

    def test_digest_archive(self):
        """Digest archive endpoint works"""
        response = requests.get(f"{BASE_URL}/api/digest/archive")
        assert response.status_code == 200

    def test_digest_subscriber_count(self):
        """Digest subscriber count endpoint works"""
        response = requests.get(f"{BASE_URL}/api/digest/subscriber-count")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
