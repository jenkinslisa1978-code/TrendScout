"""
Tests for P1 (Predictive Engine, Daily Opportunities) and P2 (Homepage Redesign, SEO Pages, Free Tools) features.
- Public endpoints: /api/public/featured-product, /api/public/seo/{slug}
- Protected endpoints: /api/dashboard/daily-opportunities
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review request
TEST_EMAIL = "testref@test.com"
TEST_PASSWORD = "Test1234!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token for protected endpoints"""
    response = api_client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Authentication failed with status {response.status_code}: {response.text}")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header for protected endpoints"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


class TestPublicFeaturedProduct:
    """Tests for GET /api/public/featured-product - Public endpoint for homepage live demo card"""

    def test_featured_product_endpoint_accessible(self, api_client):
        """Verify endpoint is accessible without authentication"""
        response = api_client.get(f"{BASE_URL}/api/public/featured-product")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_featured_product_returns_product_data(self, api_client):
        """Verify endpoint returns product with all required fields"""
        response = api_client.get(f"{BASE_URL}/api/public/featured-product")
        assert response.status_code == 200
        data = response.json()
        
        # Must contain product key
        assert "product" in data, "Response must contain 'product' key"
        
        if data["product"] is not None:
            product = data["product"]
            # Required fields per spec
            required_fields = [
                "id", "product_name", "category", "image_url",
                "launch_score", "success_probability", "trend_stage",
                "estimated_profit", "supplier_source"
            ]
            for field in required_fields:
                assert field in product, f"Missing required field: {field}"
            
            # Type validations
            assert isinstance(product["product_name"], str), "product_name must be string"
            assert isinstance(product["launch_score"], (int, float)), "launch_score must be numeric"
            assert isinstance(product["success_probability"], (int, float)), "success_probability must be numeric"
            assert product["trend_stage"] in ["Exploding", "Emerging", "Rising", "Stable", "Declining"], \
                f"Invalid trend_stage: {product['trend_stage']}"


class TestPublicSeoPages:
    """Tests for GET /api/public/seo/{slug} - Public SEO pages with product grids"""

    def test_seo_trending_tiktok_products(self, api_client):
        """Verify trending-tiktok-products page returns data"""
        response = api_client.get(f"{BASE_URL}/api/public/seo/trending-tiktok-products")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "title" in data, "Missing title"
        assert "description" in data, "Missing description"
        assert "products" in data, "Missing products array"
        assert isinstance(data["products"], list), "products must be array"
        
        # Verify title matches expected
        assert "TikTok" in data["title"], f"Title should contain TikTok: {data['title']}"

    def test_seo_winning_products_2025(self, api_client):
        """Verify winning-products-2025 page returns data"""
        response = api_client.get(f"{BASE_URL}/api/public/seo/winning-products-2025")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "title" in data
        assert "products" in data
        assert "2025" in data["title"], f"Title should contain 2025: {data['title']}"

    def test_seo_product_fields(self, api_client):
        """Verify SEO products have required fields"""
        response = api_client.get(f"{BASE_URL}/api/public/seo/trending-tiktok-products")
        assert response.status_code == 200
        data = response.json()
        
        if data["products"]:
            product = data["products"][0]
            required_fields = ["id", "product_name", "category", "launch_score", "trend_stage"]
            for field in required_fields:
                assert field in product, f"SEO product missing required field: {field}"

    def test_seo_invalid_slug_returns_404(self, api_client):
        """Verify invalid slug returns 404"""
        response = api_client.get(f"{BASE_URL}/api/public/seo/invalid-slug-xyz")
        assert response.status_code == 404, f"Expected 404 for invalid slug, got {response.status_code}"


class TestDailyOpportunities:
    """Tests for GET /api/dashboard/daily-opportunities - Protected endpoint for Dashboard panel"""

    def test_daily_opportunities_requires_auth(self, api_client):
        """Verify endpoint requires authentication"""
        # Use a fresh session without auth headers
        fresh_session = requests.Session()
        fresh_session.headers.update({"Content-Type": "application/json"})
        response = fresh_session.get(f"{BASE_URL}/api/dashboard/daily-opportunities")
        assert response.status_code in [401, 403], \
            f"Expected 401/403 without auth, got {response.status_code}: {response.text}"

    def test_daily_opportunities_returns_data(self, authenticated_client):
        """Verify endpoint returns opportunity data with auth"""
        response = authenticated_client.get(f"{BASE_URL}/api/dashboard/daily-opportunities")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Required keys per spec
        required_keys = ["top_opportunity", "emerging_products", "strong_launches", "trend_spikes"]
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"

    def test_daily_opportunities_top_opportunity_fields(self, authenticated_client):
        """Verify top_opportunity has required fields"""
        response = authenticated_client.get(f"{BASE_URL}/api/dashboard/daily-opportunities")
        assert response.status_code == 200
        data = response.json()
        
        if data["top_opportunity"]:
            top = data["top_opportunity"]
            required_fields = ["id", "product_name", "launch_score", "trend_stage", "estimated_profit"]
            for field in required_fields:
                assert field in top, f"top_opportunity missing field: {field}"
            
            # Type validations
            assert isinstance(top["launch_score"], (int, float)), "launch_score must be numeric"
            assert isinstance(top["estimated_profit"], (int, float)), "estimated_profit must be numeric"

    def test_daily_opportunities_emerging_products(self, authenticated_client):
        """Verify emerging_products array structure"""
        response = authenticated_client.get(f"{BASE_URL}/api/dashboard/daily-opportunities")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["emerging_products"], list), "emerging_products must be array"
        
        # If there are products, verify structure
        if data["emerging_products"]:
            product = data["emerging_products"][0]
            assert "id" in product
            assert "product_name" in product
            assert "launch_score" in product

    def test_daily_opportunities_strong_launches(self, authenticated_client):
        """Verify strong_launches array (may be empty if no products with launch_score >= 65)"""
        response = authenticated_client.get(f"{BASE_URL}/api/dashboard/daily-opportunities")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["strong_launches"], list), "strong_launches must be array"

    def test_daily_opportunities_trend_spikes(self, authenticated_client):
        """Verify trend_spikes array"""
        response = authenticated_client.get(f"{BASE_URL}/api/dashboard/daily-opportunities")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["trend_spikes"], list), "trend_spikes must be array"


class TestHealthCheck:
    """Verify basic API health"""

    def test_health_endpoint(self, api_client):
        """Verify API is running"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
