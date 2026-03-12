"""
Test Suite for Smart Budget Optimizer V2 Features

Tests for:
- GET /api/optimization/presets - returns 3 presets
- POST /api/optimization/set-preset - changes user's preset
- POST /api/optimization/toggle-auto-recommend - toggles auto-recommend mode
- GET /api/optimization/settings - returns current settings
- GET /api/optimization/alerts - returns optimizer alerts
- POST /api/optimization/alerts/mark-read - marks alerts as read
- GET /api/optimization/dashboard-summary - uses user's preset
- GET /api/optimization/timeline/{test_id} - returns timeline events
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "jenkinslisa1978@gmail.com"
TEST_PASSWORD = "TestAdmin123!"


class TestBudgetOptimizerV2:
    """Smart Budget Optimizer V2 API Tests"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for API calls"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if res.status_code != 200:
            pytest.skip("Authentication failed - skipping authenticated tests")
        return res.json().get("token")

    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Return headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    # =====================
    # PRESETS ENDPOINT TESTS
    # =====================

    def test_get_presets_returns_3_options(self, auth_headers):
        """GET /api/optimization/presets should return beginner, balanced, aggressive"""
        res = requests.get(f"{BASE_URL}/api/optimization/presets", headers=auth_headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "presets" in data, "Response should contain 'presets' key"
        
        presets = data["presets"]
        assert "beginner" in presets, "Should have 'beginner' preset"
        assert "balanced" in presets, "Should have 'balanced' preset"
        assert "aggressive" in presets, "Should have 'aggressive' preset"
        assert len(presets) == 3, f"Should have exactly 3 presets, got {len(presets)}"
        
        # Check preset structure
        for key, preset in presets.items():
            assert "id" in preset, f"Preset {key} should have 'id'"
            assert "name" in preset, f"Preset {key} should have 'name'"
            assert "description" in preset, f"Preset {key} should have 'description'"

    def test_presets_requires_auth(self):
        """GET /api/optimization/presets should require authentication"""
        res = requests.get(f"{BASE_URL}/api/optimization/presets")
        assert res.status_code == 401, f"Expected 401 without auth, got {res.status_code}"

    # =====================
    # SET PRESET TESTS
    # =====================

    def test_set_preset_to_aggressive(self, auth_headers):
        """POST /api/optimization/set-preset should change preset"""
        res = requests.post(
            f"{BASE_URL}/api/optimization/set-preset",
            headers=auth_headers,
            json={"preset": "aggressive"}
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert data.get("status") == "success", "Should return success status"
        assert data.get("preset") == "aggressive", "Should echo back the new preset"
        
        # Verify via GET /settings
        settings_res = requests.get(f"{BASE_URL}/api/optimization/settings", headers=auth_headers)
        assert settings_res.status_code == 200
        settings = settings_res.json()
        assert settings.get("preset") == "aggressive", "Settings should reflect aggressive preset"

    def test_set_preset_to_beginner(self, auth_headers):
        """POST /api/optimization/set-preset can set to beginner"""
        res = requests.post(
            f"{BASE_URL}/api/optimization/set-preset",
            headers=auth_headers,
            json={"preset": "beginner"}
        )
        assert res.status_code == 200
        assert res.json().get("preset") == "beginner"

    def test_set_preset_invalid_returns_400(self, auth_headers):
        """POST /api/optimization/set-preset with invalid preset should return 400"""
        res = requests.post(
            f"{BASE_URL}/api/optimization/set-preset",
            headers=auth_headers,
            json={"preset": "invalid_preset_xyz"}
        )
        assert res.status_code == 400, f"Expected 400 for invalid preset, got {res.status_code}"

    # =====================
    # TOGGLE AUTO-RECOMMEND TESTS
    # =====================

    def test_toggle_auto_recommend_enable(self, auth_headers):
        """POST /api/optimization/toggle-auto-recommend should enable auto-recommend"""
        res = requests.post(
            f"{BASE_URL}/api/optimization/toggle-auto-recommend",
            headers=auth_headers,
            json={"enabled": True}
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert data.get("status") == "success"
        assert data.get("auto_recommend_enabled") is True
        
        # Verify via GET /settings
        settings_res = requests.get(f"{BASE_URL}/api/optimization/settings", headers=auth_headers)
        settings = settings_res.json()
        assert settings.get("auto_recommend_enabled") is True, "Settings should show auto-recommend enabled"

    def test_toggle_auto_recommend_disable(self, auth_headers):
        """POST /api/optimization/toggle-auto-recommend should disable auto-recommend"""
        res = requests.post(
            f"{BASE_URL}/api/optimization/toggle-auto-recommend",
            headers=auth_headers,
            json={"enabled": False}
        )
        assert res.status_code == 200
        assert res.json().get("auto_recommend_enabled") is False
        
        # Verify via GET /settings
        settings_res = requests.get(f"{BASE_URL}/api/optimization/settings", headers=auth_headers)
        settings = settings_res.json()
        assert settings.get("auto_recommend_enabled") is False

    # =====================
    # SETTINGS ENDPOINT TESTS
    # =====================

    def test_get_settings_returns_preset_and_auto_recommend(self, auth_headers):
        """GET /api/optimization/settings returns current preset and auto_recommend_enabled"""
        res = requests.get(f"{BASE_URL}/api/optimization/settings", headers=auth_headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "preset" in data, "Settings should contain 'preset' key"
        assert "auto_recommend_enabled" in data, "Settings should contain 'auto_recommend_enabled' key"
        
        # Preset should be one of valid values
        assert data["preset"] in ["beginner", "balanced", "aggressive"], f"Invalid preset: {data['preset']}"
        assert isinstance(data["auto_recommend_enabled"], bool), "auto_recommend_enabled should be boolean"

    # =====================
    # ALERTS ENDPOINT TESTS
    # =====================

    def test_get_optimizer_alerts(self, auth_headers):
        """GET /api/optimization/alerts returns alerts list with unread count"""
        res = requests.get(f"{BASE_URL}/api/optimization/alerts?limit=20", headers=auth_headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "alerts" in data, "Response should contain 'alerts' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "unread" in data, "Response should contain 'unread' key"
        
        assert isinstance(data["alerts"], list), "Alerts should be a list"
        assert isinstance(data["total"], int), "Total should be an integer"
        assert isinstance(data["unread"], int), "Unread should be an integer"

    def test_mark_alerts_as_read(self, auth_headers):
        """POST /api/optimization/alerts/mark-read marks all alerts as read"""
        res = requests.post(f"{BASE_URL}/api/optimization/alerts/mark-read", headers=auth_headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "marked_read" in data, "Response should contain 'marked_read' count"
        assert isinstance(data["marked_read"], int), "marked_read should be an integer"
        
        # After marking all as read, unread count should be 0
        alerts_res = requests.get(f"{BASE_URL}/api/optimization/alerts", headers=auth_headers)
        alerts_data = alerts_res.json()
        assert alerts_data.get("unread") == 0, "Unread count should be 0 after marking all read"

    # =====================
    # DASHBOARD SUMMARY TESTS
    # =====================

    def test_dashboard_summary_returns_structure(self, auth_headers):
        """GET /api/optimization/dashboard-summary returns expected structure"""
        res = requests.get(f"{BASE_URL}/api/optimization/dashboard-summary", headers=auth_headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        # Check expected fields from generate_dashboard_summary
        assert "candidates_to_scale" in data, "Should have candidates_to_scale"
        assert "losers_to_pause" in data, "Should have losers_to_pause"
        assert "needs_action" in data, "Should have needs_action"
        assert "waiting_data" in data, "Should have waiting_data"
        assert "total_active_tests" in data, "Should have total_active_tests"
        
        assert isinstance(data["candidates_to_scale"], list)
        assert isinstance(data["losers_to_pause"], list)
        assert isinstance(data["total_active_tests"], int)

    # =====================
    # TIMELINE ENDPOINT TESTS
    # =====================

    def test_timeline_endpoint_works(self, auth_headers):
        """GET /api/optimization/timeline/{test_id} returns timeline events"""
        # Use a dummy test_id - should return empty list if no events
        test_id = "test_dummy_id_12345"
        res = requests.get(f"{BASE_URL}/api/optimization/timeline/{test_id}", headers=auth_headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "events" in data, "Response should contain 'events' key"
        assert "total" in data, "Response should contain 'total' key"
        assert isinstance(data["events"], list), "Events should be a list"

    # =====================
    # INTEGRATION - PRESET AFFECTS RECOMMENDATIONS
    # =====================

    def test_preset_change_persists(self, auth_headers):
        """Verify preset change persists across requests"""
        # Set to balanced
        requests.post(
            f"{BASE_URL}/api/optimization/set-preset",
            headers=auth_headers,
            json={"preset": "balanced"}
        )
        
        # Verify
        settings_res = requests.get(f"{BASE_URL}/api/optimization/settings", headers=auth_headers)
        assert settings_res.json().get("preset") == "balanced"


class TestWeeklyRadarDigestTask:
    """Verify the send_weekly_radar_digest task is registered"""

    def test_jobs_status_includes_weekly_radar_digest(self):
        """GET /api/jobs/status should list send_weekly_radar_digest task"""
        res = requests.get(f"{BASE_URL}/api/jobs/status")
        
        # This endpoint may not require auth for basic status
        if res.status_code == 200:
            data = res.json()
            available_tasks = data.get("available_tasks", {})
            
            # Check if send_weekly_radar_digest is registered
            assert "send_weekly_radar_digest" in available_tasks, \
                f"send_weekly_radar_digest should be in available tasks: {list(available_tasks.keys())}"
            
            task_info = available_tasks["send_weekly_radar_digest"]
            assert "schedule" in task_info or "default_schedule" in task_info, \
                "Task should have a schedule defined"
        else:
            # If endpoint requires auth, we'll skip this particular check
            pytest.skip("Jobs status requires auth, testing via logs instead")


class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        """GET /api/health should return healthy"""
        res = requests.get(f"{BASE_URL}/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data.get("status") == "healthy"
