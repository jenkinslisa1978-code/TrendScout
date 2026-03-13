"""
Tests for TikTok Intelligence and AI Product Launch Simulator features.
Session: Phase C - TrendScout SaaS Platform
Features:
1. TikTok Ad Intelligence dashboard (public endpoint)
2. AI Product Launch Simulator (GPT 5.2 via emergentintegrations)
3. Weekly competitor scan scheduled task
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "testuser_phase_c@test.com"
TEST_USER_PASSWORD = "test123"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Authentication failed - status {response.status_code}")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


@pytest.fixture(scope="module")
def sample_product_id(api_client):
    """Get a sample product ID from daily picks"""
    response = api_client.get(f"{BASE_URL}/api/public/daily-picks")
    if response.status_code == 200:
        picks = response.json().get("picks", [])
        if picks:
            return picks[0]["id"]
    # Fallback to a known product from TikTok intelligence
    response = api_client.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
    if response.status_code == 200:
        viral = response.json().get("viral_products", [])
        if viral:
            return viral[0]["id"]
    pytest.skip("No products available for testing")


class TestTikTokIntelligence:
    """Tests for GET /api/tools/tiktok-intelligence (public endpoint)"""

    def test_tiktok_intelligence_returns_200(self, api_client):
        """TikTok Intelligence endpoint returns 200"""
        response = api_client.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_tiktok_intelligence_has_viral_products(self, api_client):
        """Response includes viral_products array"""
        response = api_client.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        data = response.json()
        assert "viral_products" in data, "Missing viral_products key"
        assert isinstance(data["viral_products"], list), "viral_products must be a list"

    def test_tiktok_intelligence_viral_products_structure(self, api_client):
        """Viral products have required fields"""
        response = api_client.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        data = response.json()
        viral = data.get("viral_products", [])
        if viral:
            product = viral[0]
            assert "id" in product, "Product missing id"
            assert "product_name" in product, "Product missing product_name"
            assert "tiktok_views" in product, "Product missing tiktok_views"
            assert "launch_score" in product, "Product missing launch_score"
            assert "category" in product, "Product missing category"

    def test_tiktok_intelligence_has_categories(self, api_client):
        """Response includes categories array with performance data"""
        response = api_client.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        data = response.json()
        assert "categories" in data, "Missing categories key"
        categories = data["categories"]
        assert isinstance(categories, list), "categories must be a list"
        if categories:
            cat = categories[0]
            assert "name" in cat, "Category missing name"
            assert "total_views" in cat, "Category missing total_views"
            assert "product_count" in cat, "Category missing product_count"

    def test_tiktok_intelligence_has_trending_patterns(self, api_client):
        """Response includes trending_patterns array"""
        response = api_client.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        data = response.json()
        assert "trending_patterns" in data, "Missing trending_patterns key"
        patterns = data["trending_patterns"]
        assert isinstance(patterns, list), "trending_patterns must be a list"
        if patterns:
            pattern = patterns[0]
            assert "pattern" in pattern, "Pattern missing pattern field"
            assert "relevance" in pattern, "Pattern missing relevance"
            assert "description" in pattern, "Pattern missing description"

    def test_tiktok_intelligence_has_stats(self, api_client):
        """Response includes stats object with aggregated metrics"""
        response = api_client.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        data = response.json()
        assert "stats" in data, "Missing stats key"
        stats = data["stats"]
        assert "total_tiktok_views" in stats, "Stats missing total_tiktok_views"
        assert "products_tracked" in stats, "Stats missing products_tracked"
        assert "avg_launch_score" in stats, "Stats missing avg_launch_score"
        assert "top_category" in stats, "Stats missing top_category"

    def test_tiktok_intelligence_views_are_positive(self, api_client):
        """TikTok views should be positive (> 0)"""
        response = api_client.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        data = response.json()
        stats = data.get("stats", {})
        total_views = stats.get("total_tiktok_views", 0)
        assert total_views > 0, f"Expected positive total views, got {total_views}"


class TestBaseSimulator:
    """Tests for GET /api/ad-tests/simulate/{product_id} (requires auth)"""

    def test_simulate_requires_auth(self, api_client, sample_product_id):
        """Simulate endpoint returns 401 without auth"""
        # Use clean client without auth header
        clean_client = requests.Session()
        response = clean_client.get(f"{BASE_URL}/api/ad-tests/simulate/{sample_product_id}")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"

    def test_simulate_returns_200_with_auth(self, authenticated_client, sample_product_id):
        """Simulate endpoint returns 200 with valid auth"""
        response = authenticated_client.get(f"{BASE_URL}/api/ad-tests/simulate/{sample_product_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_simulate_returns_simulation_data(self, authenticated_client, sample_product_id):
        """Simulate response has simulation object"""
        response = authenticated_client.get(f"{BASE_URL}/api/ad-tests/simulate/{sample_product_id}")
        data = response.json()
        assert "simulation" in data, "Missing simulation key"
        sim = data["simulation"]
        assert "profit_per_sale" in sim, "simulation missing profit_per_sale"
        assert "estimated_cvr" in sim, "simulation missing estimated_cvr"
        assert "daily_sales_range" in sim, "simulation missing daily_sales_range"

    def test_simulate_returns_potential_rating(self, authenticated_client, sample_product_id):
        """Response has potential rating (High/Moderate/Risky)"""
        response = authenticated_client.get(f"{BASE_URL}/api/ad-tests/simulate/{sample_product_id}")
        data = response.json()
        assert "potential" in data, "Missing potential key"
        assert data["potential"] in ["High", "Moderate", "Risky"], f"Invalid potential: {data['potential']}"

    def test_simulate_returns_guidance(self, authenticated_client, sample_product_id):
        """Response has guidance text"""
        response = authenticated_client.get(f"{BASE_URL}/api/ad-tests/simulate/{sample_product_id}")
        data = response.json()
        assert "guidance" in data, "Missing guidance key"
        assert isinstance(data["guidance"], str), "guidance must be a string"
        assert len(data["guidance"]) > 10, "guidance should be meaningful text"

    def test_simulate_with_invalid_product_returns_404(self, authenticated_client):
        """Invalid product ID returns 404"""
        response = authenticated_client.get(f"{BASE_URL}/api/ad-tests/simulate/invalid-product-id-12345")
        assert response.status_code == 404, f"Expected 404 for invalid product, got {response.status_code}"


class TestAISimulator:
    """Tests for GET /api/ad-tests/ai-simulate/{product_id} (requires auth, uses GPT 5.2)"""

    def test_ai_simulate_requires_auth(self, api_client, sample_product_id):
        """AI Simulate endpoint returns 401 without auth"""
        clean_client = requests.Session()
        response = clean_client.get(f"{BASE_URL}/api/ad-tests/ai-simulate/{sample_product_id}")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"

    def test_ai_simulate_returns_200_with_auth(self, authenticated_client, sample_product_id):
        """AI Simulate endpoint returns 200 with valid auth (may take 10-15s for GPT 5.2)"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/ad-tests/ai-simulate/{sample_product_id}",
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_ai_simulate_has_ai_analysis(self, authenticated_client, sample_product_id):
        """Response includes ai_analysis with GPT 5.2 generated content"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/ad-tests/ai-simulate/{sample_product_id}",
            timeout=60
        )
        data = response.json()
        assert "ai_analysis" in data, "Missing ai_analysis key"
        ai = data["ai_analysis"]
        # Check AI analysis structure
        assert "verdict" in ai, "ai_analysis missing verdict"
        assert "confidence_score" in ai, "ai_analysis missing confidence_score"

    def test_ai_simulate_has_strategy_phases(self, authenticated_client, sample_product_id):
        """AI analysis includes strategy with phase_1, phase_2, phase_3"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/ad-tests/ai-simulate/{sample_product_id}",
            timeout=60
        )
        data = response.json()
        ai = data.get("ai_analysis", {})
        if not ai.get("error"):
            assert "strategy" in ai, "ai_analysis missing strategy"
            strategy = ai["strategy"]
            assert "phase_1" in strategy, "strategy missing phase_1"
            assert "phase_2" in strategy, "strategy missing phase_2"
            assert "phase_3" in strategy, "strategy missing phase_3"

    def test_ai_simulate_has_target_audience(self, authenticated_client, sample_product_id):
        """AI analysis includes target_audience"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/ad-tests/ai-simulate/{sample_product_id}",
            timeout=60
        )
        data = response.json()
        ai = data.get("ai_analysis", {})
        if not ai.get("error"):
            assert "target_audience" in ai, "ai_analysis missing target_audience"
            ta = ai["target_audience"]
            assert "primary" in ta, "target_audience missing primary"
            assert "secondary" in ta, "target_audience missing secondary"
            assert "platforms" in ta, "target_audience missing platforms"

    def test_ai_simulate_has_revenue_projection(self, authenticated_client, sample_product_id):
        """AI analysis includes revenue_projection"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/ad-tests/ai-simulate/{sample_product_id}",
            timeout=60
        )
        data = response.json()
        ai = data.get("ai_analysis", {})
        if not ai.get("error"):
            assert "revenue_projection" in ai, "ai_analysis missing revenue_projection"
            rp = ai["revenue_projection"]
            assert "month_1" in rp, "revenue_projection missing month_1"
            assert "month_3" in rp, "revenue_projection missing month_3"
            assert "month_6" in rp, "revenue_projection missing month_6"


class TestScheduledTasks:
    """Tests for scheduled tasks including weekly_competitor_scan"""

    def test_jobs_status_returns_200(self, api_client):
        """Jobs status endpoint returns 200"""
        response = api_client.get(f"{BASE_URL}/api/jobs/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_scheduler_has_18_tasks(self, api_client):
        """Scheduler has 18 registered tasks"""
        response = api_client.get(f"{BASE_URL}/api/jobs/status")
        data = response.json()
        scheduler = data.get("scheduler", {})
        scheduled_jobs = scheduler.get("scheduled_jobs", 0)
        assert scheduled_jobs == 18, f"Expected 18 scheduled tasks, got {scheduled_jobs}"

    def test_weekly_competitor_scan_is_registered(self, api_client):
        """weekly_competitor_scan is registered as a scheduled task"""
        response = api_client.get(f"{BASE_URL}/api/jobs/status")
        data = response.json()
        available_tasks = data.get("available_tasks", {})
        assert "weekly_competitor_scan" in available_tasks, "weekly_competitor_scan not registered"
        task = available_tasks["weekly_competitor_scan"]
        assert task["name"] == "weekly_competitor_scan"
        assert task["description"] == "Re-scan all tracked competitor stores and notify users of changes"
        # Verify cron schedule (Monday 6 AM)
        assert task["default_schedule"] == "0 6 * * 1", f"Wrong schedule: {task['default_schedule']}"

    def test_weekly_competitor_scan_scheduled(self, api_client):
        """weekly_competitor_scan is in the scheduler's job list"""
        response = api_client.get(f"{BASE_URL}/api/jobs/status")
        data = response.json()
        jobs = data.get("scheduler", {}).get("jobs", [])
        job_ids = [j["id"] for j in jobs]
        assert "scheduled_weekly_competitor_scan" in job_ids, "weekly_competitor_scan not in scheduler jobs"
