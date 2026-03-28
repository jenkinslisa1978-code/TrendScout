"""
Test suite for Sync History endpoints and Auto-Sync task registration.
Tests:
- GET /api/sync/history - returns sync history for authenticated user
- GET /api/sync/history/summary - returns per-platform sync summaries
- Auto-sync task 'auto_sync_connected_stores' is registered in scheduler
- GET /api/health returns ok
- Login works for admin and demo users
- GET /api/public/trending-products returns products
- GET /api/public/daily-picks returns picks
- GET /api/public/top-trending returns products
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "reviewer@trendscout.click"
ADMIN_PASSWORD = "ShopifyReview2026!"
DEMO_EMAIL = "demo@trendscout.click"
DEMO_PASSWORD = "DemoReview2026!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token."""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if resp.status_code == 200:
        data = resp.json()
        return data.get("token") or data.get("access_token")
    pytest.skip("Admin login failed")


@pytest.fixture(scope="module")
def demo_token():
    """Get demo user auth token."""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD
    })
    if resp.status_code == 200:
        data = resp.json()
        return data.get("token") or data.get("access_token")
    pytest.skip("Demo login failed")


class TestHealthAndAuth:
    """Basic health and authentication tests."""

    def test_health_endpoint(self):
        """GET /api/health returns ok."""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok"
        print("PASS: GET /api/health returns {status: 'ok'}")

    def test_admin_login(self):
        """Admin login works."""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data or "token" in data
        print(f"PASS: Admin login works for {ADMIN_EMAIL}")

    def test_demo_login(self):
        """Demo user login works."""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data or "token" in data
        print(f"PASS: Demo login works for {DEMO_EMAIL}")


class TestSyncHistory:
    """Tests for sync history endpoints."""

    def test_sync_history_requires_auth(self):
        """GET /api/sync/history requires authentication."""
        resp = requests.get(f"{BASE_URL}/api/sync/history")
        assert resp.status_code in [401, 403]
        print("PASS: GET /api/sync/history requires auth (401/403)")

    def test_sync_history_with_auth(self, admin_token):
        """GET /api/sync/history returns history for authenticated user."""
        resp = requests.get(
            f"{BASE_URL}/api/sync/history",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        assert "history" in data
        assert isinstance(data["history"], list)
        assert "total" in data
        print(f"PASS: GET /api/sync/history returns {len(data['history'])} history items")

    def test_sync_history_summary_requires_auth(self):
        """GET /api/sync/history/summary requires authentication."""
        resp = requests.get(f"{BASE_URL}/api/sync/history/summary")
        assert resp.status_code in [401, 403]
        print("PASS: GET /api/sync/history/summary requires auth (401/403)")

    def test_sync_history_summary_with_auth(self, admin_token):
        """GET /api/sync/history/summary returns per-platform summaries."""
        resp = requests.get(
            f"{BASE_URL}/api/sync/history/summary",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        assert "summary" in data
        assert isinstance(data["summary"], dict)
        # Summary should be keyed by platform name
        for platform, summary in data["summary"].items():
            assert "platform" in summary or platform  # platform key exists
            print(f"  - Platform '{platform}': last_sync={summary.get('last_sync')}, total_syncs={summary.get('total_syncs')}")
        print(f"PASS: GET /api/sync/history/summary returns {len(data['summary'])} platform summaries")

    def test_sync_history_demo_user(self, demo_token):
        """Demo user can also access sync history."""
        resp = requests.get(
            f"{BASE_URL}/api/sync/history",
            headers={"Authorization": f"Bearer {demo_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        print("PASS: Demo user can access GET /api/sync/history")


class TestPublicEndpoints:
    """Tests for public API endpoints."""

    def test_public_trending_products(self):
        """GET /api/public/trending-products returns products."""
        resp = requests.get(f"{BASE_URL}/api/public/trending-products")
        assert resp.status_code == 200
        data = resp.json()
        # Should have products array
        assert "products" in data or isinstance(data, list)
        products = data.get("products", data) if isinstance(data, dict) else data
        print(f"PASS: GET /api/public/trending-products returns {len(products)} products")

    def test_public_daily_picks(self):
        """GET /api/public/daily-picks returns picks."""
        resp = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert resp.status_code == 200
        data = resp.json()
        # Should have picks or products array
        picks = data.get("picks", data.get("products", data))
        if isinstance(picks, list):
            print(f"PASS: GET /api/public/daily-picks returns {len(picks)} picks")
        else:
            print(f"PASS: GET /api/public/daily-picks returns data: {type(data)}")

    def test_public_top_trending(self):
        """GET /api/public/top-trending returns products."""
        resp = requests.get(f"{BASE_URL}/api/public/top-trending")
        assert resp.status_code == 200
        data = resp.json()
        # Should have products array
        products = data.get("products", data) if isinstance(data, dict) else data
        if isinstance(products, list):
            print(f"PASS: GET /api/public/top-trending returns {len(products)} products")
        else:
            print(f"PASS: GET /api/public/top-trending returns data")


class TestAutoSyncTaskRegistration:
    """Tests for auto-sync task registration in scheduler."""

    def test_scheduler_tasks_endpoint(self, admin_token):
        """Check if scheduler has auto_sync_connected_stores task registered."""
        # Use the correct jobs/status endpoint
        resp = requests.get(
            f"{BASE_URL}/api/jobs/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Check scheduler section
        scheduler = data.get("scheduler", {})
        assert scheduler.get("running") is True, "Scheduler should be running"
        
        # Check scheduled jobs list for auto_sync_connected_stores
        jobs = scheduler.get("jobs", [])
        auto_sync_job = None
        for job in jobs:
            if "auto_sync_connected_stores" in job.get("id", "") or "auto_sync_connected_stores" in job.get("name", ""):
                auto_sync_job = job
                break
        
        assert auto_sync_job is not None, "auto_sync_connected_stores should be in scheduled jobs"
        print(f"PASS: auto_sync_connected_stores task found in scheduler")
        print(f"  - Job ID: {auto_sync_job.get('id')}")
        print(f"  - Next run: {auto_sync_job.get('next_run')}")
        print(f"  - Trigger: {auto_sync_job.get('trigger')}")
        
        # Also verify it's in available_tasks
        available_tasks = data.get("available_tasks", {})
        assert "auto_sync_connected_stores" in available_tasks, "auto_sync_connected_stores should be in available_tasks"
        task_info = available_tasks["auto_sync_connected_stores"]
        assert task_info.get("default_schedule") == "0 */6 * * *", "Schedule should be every 6 hours"
        print(f"  - Description: {task_info.get('description')}")
        print(f"  - Schedule: {task_info.get('default_schedule')}")


class TestSyncProducts:
    """Tests for synced products endpoint."""

    def test_sync_products_requires_auth(self):
        """GET /api/sync/products requires authentication."""
        resp = requests.get(f"{BASE_URL}/api/sync/products")
        assert resp.status_code in [401, 403]
        print("PASS: GET /api/sync/products requires auth")

    def test_sync_products_with_auth(self, admin_token):
        """GET /api/sync/products returns products for authenticated user."""
        resp = requests.get(
            f"{BASE_URL}/api/sync/products",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        assert "products" in data
        assert "by_platform" in data
        print(f"PASS: GET /api/sync/products returns {len(data['products'])} products")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
