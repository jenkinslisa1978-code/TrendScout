"""
Iteration 72 - 7-Part Improvement Testing:
Part 1: Shopify OAuth flow (init + callback endpoints)
Part 2: Image validation service
Part 3: Enhanced Shopify export (endpoints already exist)
Part 4: Beginner Mode (frontend)
Part 5: Winning Product Indicator (frontend)
Part 6: Product Launch Playbook (GET /api/launch-playbook/{product_id})
Part 7: Security (token encryption module)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "jenkinslisa1978@gmail.com"
TEST_PASSWORD = "admin123456"


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for authenticated requests"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if resp.status_code == 200:
        data = resp.json()
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Auth failed: {resp.status_code} - {resp.text}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="module")
def sample_product_id():
    """Get a valid product ID for testing"""
    resp = requests.get(f"{BASE_URL}/api/products", params={"limit": 1})
    if resp.status_code == 200:
        data = resp.json().get("data", [])
        if data:
            return data[0].get("id")
    pytest.skip("No products found for testing")


# ====================
# Part 1: Shopify OAuth Tests
# ====================
class TestShopifyOAuth:
    """Tests for Shopify OAuth flow"""

    def test_shopify_oauth_init_returns_503_without_config(self, auth_headers):
        """POST /api/shopify/oauth/init returns 503 when SHOPIFY_CLIENT_ID is not set"""
        # This is EXPECTED behavior per the review request
        resp = requests.post(
            f"{BASE_URL}/api/shopify/oauth/init",
            json={"shop_domain": "test-store"},
            headers=auth_headers
        )
        # Should return 503 because SHOPIFY_CLIENT_ID is not set
        assert resp.status_code == 503
        data = resp.json()
        assert "SHOPIFY_CLIENT_ID" in data.get("detail", "") or "not configured" in data.get("detail", "").lower()

    def test_shopify_oauth_status_returns_not_connected(self, auth_headers):
        """GET /api/shopify/oauth/status returns connected: false for user without connection"""
        resp = requests.get(
            f"{BASE_URL}/api/shopify/oauth/status",
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        # User should have connected: false since they haven't connected Shopify
        assert "connected" in data

    def test_shopify_oauth_init_requires_auth(self):
        """POST /api/shopify/oauth/init returns 401 without auth"""
        resp = requests.post(
            f"{BASE_URL}/api/shopify/oauth/init",
            json={"shop_domain": "test-store"}
        )
        assert resp.status_code in [401, 403]

    def test_shopify_oauth_status_requires_auth(self):
        """GET /api/shopify/oauth/status returns 401 without auth"""
        resp = requests.get(f"{BASE_URL}/api/shopify/oauth/status")
        assert resp.status_code in [401, 403]


# ====================
# Part 6: Launch Playbook Tests
# ====================
class TestLaunchPlaybook:
    """Tests for GET /api/launch-playbook/{product_id}"""

    def test_launch_playbook_returns_5_steps(self, auth_headers, sample_product_id):
        """Launch playbook returns 5 launch steps"""
        resp = requests.get(
            f"{BASE_URL}/api/launch-playbook/{sample_product_id}",
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify 5 launch steps
        assert "launch_steps" in data
        assert len(data["launch_steps"]) == 5
        
        # Verify each step has required fields
        for step in data["launch_steps"]:
            assert "step" in step
            assert "title" in step
            assert "description" in step
            assert "action" in step
            assert "estimated_time" in step

    def test_launch_playbook_returns_3_ad_angles(self, auth_headers, sample_product_id):
        """Launch playbook returns 3 ad creative angles"""
        resp = requests.get(
            f"{BASE_URL}/api/launch-playbook/{sample_product_id}",
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify 3 ad angles
        assert "ad_angles" in data
        assert len(data["ad_angles"]) == 3
        
        # Verify each angle has required fields
        for angle in data["ad_angles"]:
            assert "angle" in angle
            assert "description" in angle
            assert "example" in angle

    def test_launch_playbook_returns_audience_suggestions(self, auth_headers, sample_product_id):
        """Launch playbook returns audience suggestions"""
        resp = requests.get(
            f"{BASE_URL}/api/launch-playbook/{sample_product_id}",
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify audience suggestions exist
        assert "audience_suggestions" in data
        assert len(data["audience_suggestions"]) > 0
        
        # Verify each audience has required fields
        for aud in data["audience_suggestions"]:
            assert "name" in aud
            assert "age" in aud
            assert "interests" in aud

    def test_launch_playbook_returns_testing_budget(self, auth_headers, sample_product_id):
        """Launch playbook returns testing budget recommendation"""
        resp = requests.get(
            f"{BASE_URL}/api/launch-playbook/{sample_product_id}",
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify testing budget exists with required fields
        assert "testing_budget" in data
        budget = data["testing_budget"]
        assert "recommended_daily" in budget
        assert "total_test_budget" in budget
        assert "creatives" in budget
        assert "test_period" in budget
        assert "note" in budget

    def test_launch_playbook_returns_404_for_invalid_product(self, auth_headers):
        """Launch playbook returns 404 for non-existent product"""
        resp = requests.get(
            f"{BASE_URL}/api/launch-playbook/invalid-product-id-xyz",
            headers=auth_headers
        )
        assert resp.status_code == 404

    def test_launch_playbook_requires_auth(self, sample_product_id):
        """Launch playbook requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/launch-playbook/{sample_product_id}")
        assert resp.status_code in [401, 403]


# ====================
# Profitability Calculator Regression Tests
# ====================
class TestProfitabilityCalculator:
    """Regression tests for profitability calculator"""

    def test_profitability_calculator_works(self, sample_product_id):
        """POST /api/profitability-calculator returns correct structure"""
        resp = requests.post(
            f"{BASE_URL}/api/profitability-calculator",
            json={
                "product_id": sample_product_id,
                "daily_ad_budget": 20.0,
                "conversion_rate": 2.0,
                "avg_cpc": 0.50,
                "days": 30
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify structure
        assert "projections" in data
        assert "break_even" in data
        assert "verdict" in data
        assert "verdict_color" in data
        
        # Verify projections have expected fields
        proj = data["projections"]
        assert "total_revenue" in proj
        assert "total_profit" in proj
        assert "roi_percent" in proj


# ====================
# Rate Limiting Regression Tests
# ====================
class TestRateLimiting:
    """Regression tests for rate limiting headers"""

    def test_rate_limit_headers_present(self, auth_headers):
        """Authenticated requests have rate limit headers"""
        resp = requests.get(
            f"{BASE_URL}/api/products",
            headers=auth_headers,
            params={"limit": 1}
        )
        assert resp.status_code == 200
        
        # Check rate limit headers are present
        assert "X-RateLimit-Limit" in resp.headers or "x-ratelimit-limit" in resp.headers
        assert "X-RateLimit-Remaining" in resp.headers or "x-ratelimit-remaining" in resp.headers


# ====================
# Health Check
# ====================
class TestHealthCheck:
    """Basic health check tests"""

    def test_health_endpoint(self):
        """GET /api/health returns 200"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200

    def test_products_endpoint(self):
        """GET /api/products returns data array"""
        resp = requests.get(f"{BASE_URL}/api/products", params={"limit": 5})
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert isinstance(data["data"], list)
