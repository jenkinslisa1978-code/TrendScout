"""
Ad A/B Test System Backend Tests

Tests for:
- GET /api/ad-tests/variations/{product_id} (PUBLIC)
- POST /api/ad-tests/create (AUTH)
- GET /api/ad-tests/my (AUTH)
- PUT /api/ad-tests/{test_id}/results (AUTH)
- POST /api/ad-tests/{test_id}/complete (AUTH)
- GET /api/ad-tests/simulate/{product_id} (AUTH)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "testref@test.com"
TEST_PASSWORD = "Test1234!"
TEST_PRODUCT_ID = "68f41478-9ca2-48c6-997d-b121e2ef8ee9"


def get_auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        # Auth endpoint returns "token" not "access_token"
        return data.get("token") or data.get("access_token")
    return None


# Global auth state
AUTH_TOKEN = None
AUTH_HEADERS = None


@pytest.fixture(scope="session", autouse=True)
def setup_auth():
    """Setup authentication before all tests"""
    global AUTH_TOKEN, AUTH_HEADERS
    AUTH_TOKEN = get_auth_token()
    if AUTH_TOKEN:
        AUTH_HEADERS = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        print(f"\nAuth setup successful, token: {AUTH_TOKEN[:20]}...")
    else:
        AUTH_HEADERS = {"Content-Type": "application/json"}
        print("\nAuth setup FAILED")


def get_headers():
    """Get auth headers - ensure they're populated"""
    global AUTH_TOKEN, AUTH_HEADERS
    if AUTH_HEADERS is None or "Authorization" not in AUTH_HEADERS:
        AUTH_TOKEN = get_auth_token()
        if AUTH_TOKEN:
            AUTH_HEADERS = {
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
    return AUTH_HEADERS


# ═══════════════════════════════════════════════════════════════════
# VARIATIONS ENDPOINT (PUBLIC)
# ═══════════════════════════════════════════════════════════════════

class TestVariationsEndpoint:
    """Tests for GET /api/ad-tests/variations/{product_id}"""

    def test_variations_returns_200_for_valid_product(self):
        """Test variations endpoint returns 200 for valid product"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_variations_returns_product_info(self):
        """Test variations response includes product info"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        assert "product_id" in data
        assert "product_name" in data
        assert data["product_id"] == TEST_PRODUCT_ID

    def test_variations_returns_exactly_3_variations(self):
        """Test variations array contains exactly 3 variations"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        assert "variations" in data
        assert len(data["variations"]) == 3

    def test_variations_have_required_fields(self):
        """Test each variation has all required fields"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        required_fields = [
            "variation_id", "label", "hook_type", "hook_id", "hook_line",
            "video_structure", "script", "cta", "recommended_length", "effectiveness_estimate"
        ]
        for var in data["variations"]:
            for field in required_fields:
                assert field in var, f"Missing field '{field}' in variation"

    def test_variation_labels_are_abc(self):
        """Test variation labels are A, B, C"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        labels = [v["label"] for v in data["variations"]]
        assert "Variation A" in labels
        assert "Variation B" in labels
        assert "Variation C" in labels

    def test_variation_script_has_5_scenes(self):
        """Test each variation script has exactly 5 scenes"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        for var in data["variations"]:
            assert "script" in var
            assert len(var["script"]) == 5, f"Expected 5 scenes, got {len(var['script'])}"

    def test_variation_script_scenes_have_required_fields(self):
        """Test script scenes have time, action, audio fields"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        for var in data["variations"]:
            for scene in var["script"]:
                assert "time" in scene
                assert "action" in scene
                assert "audio" in scene

    def test_effectiveness_estimate_is_valid(self):
        """Test effectiveness_estimate is a reasonable percentage"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        for var in data["variations"]:
            eff = var["effectiveness_estimate"]
            assert isinstance(eff, int), f"effectiveness_estimate should be int, got {type(eff)}"
            assert 0 <= eff <= 100, f"effectiveness_estimate should be 0-100, got {eff}"

    def test_test_plan_included(self):
        """Test test_plan is included in response"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        assert "test_plan" in data

    def test_test_plan_has_6_steps(self):
        """Test test_plan has exactly 6 steps"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        plan = data["test_plan"]
        assert "steps" in plan
        assert len(plan["steps"]) == 6

    def test_test_plan_has_4_metrics(self):
        """Test test_plan has exactly 4 metrics to track"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        plan = data["test_plan"]
        assert "metrics_to_track" in plan
        assert len(plan["metrics_to_track"]) == 4

    def test_test_plan_has_budget_and_duration(self):
        """Test test_plan has budget and duration fields"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/{TEST_PRODUCT_ID}")
        data = response.json()
        plan = data["test_plan"]
        assert "total_budget" in plan
        assert "duration" in plan
        assert "budget_per_variation" in plan

    def test_variations_404_for_nonexistent_product(self):
        """Test variations returns 404 for non-existent product"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/variations/nonexistent-id-12345")
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# CREATE AD TEST ENDPOINT (AUTH)
# ═══════════════════════════════════════════════════════════════════

class TestCreateAdTest:
    """Tests for POST /api/ad-tests/create"""

    def test_create_requires_auth(self):
        """Test create endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/ad-tests/create", json={"product_id": TEST_PRODUCT_ID})
        assert response.status_code in [401, 403]

    def test_create_requires_product_id(self):
        """Test create requires product_id"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.post(f"{BASE_URL}/api/ad-tests/create", json={}, headers=headers)
        assert response.status_code == 400
        assert "product_id" in response.text.lower()

    def test_create_returns_404_for_nonexistent_product(self):
        """Test create returns 404 for non-existent product"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.post(
            f"{BASE_URL}/api/ad-tests/create",
            json={"product_id": "nonexistent-id-12345"},
            headers=headers
        )
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# MY AD TESTS ENDPOINT (AUTH)
# ═══════════════════════════════════════════════════════════════════

class TestMyAdTests:
    """Tests for GET /api/ad-tests/my"""

    def test_my_tests_requires_auth(self):
        """Test my tests endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/my")
        assert response.status_code in [401, 403]

    def test_my_tests_returns_tests_array(self):
        """Test my tests returns tests array"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(f"{BASE_URL}/api/ad-tests/my", headers=headers)
        assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
        data = response.json()
        assert "tests" in data
        assert isinstance(data["tests"], list)

    def test_my_tests_includes_existing_test(self):
        """Test my tests includes the existing completed test for test product"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(f"{BASE_URL}/api/ad-tests/my", headers=headers)
        data = response.json()
        tests = data.get("tests", [])
        # Check if any test is for our test product
        test_product_tests = [t for t in tests if t.get("product_id") == TEST_PRODUCT_ID]
        assert len(test_product_tests) >= 1, "Expected at least one test for test product"
        test = test_product_tests[0]
        assert "status" in test
        assert "variations" in test
        # Verify it's the completed test with winner
        if test["status"] == "completed":
            assert test.get("winner") is not None

    def test_my_tests_test_has_winner_info(self):
        """Test that completed test has proper winner info"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(f"{BASE_URL}/api/ad-tests/my?status=completed", headers=headers)
        data = response.json()
        tests = data.get("tests", [])
        if tests:
            test = tests[0]
            if test.get("winner"):
                winner = test["winner"]
                assert "variation_id" in winner
                assert "label" in winner
                assert "ctr" in winner

    def test_my_tests_filter_by_status(self):
        """Test filtering by status=active"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(f"{BASE_URL}/api/ad-tests/my?status=active", headers=headers)
        assert response.status_code == 200
        data = response.json()
        for test in data.get("tests", []):
            assert test["status"] == "active"

    def test_my_tests_filter_completed(self):
        """Test filtering by status=completed"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(f"{BASE_URL}/api/ad-tests/my?status=completed", headers=headers)
        assert response.status_code == 200
        data = response.json()
        for test in data.get("tests", []):
            assert test["status"] == "completed"


# ═══════════════════════════════════════════════════════════════════
# UPDATE RESULTS ENDPOINT (AUTH)
# ═══════════════════════════════════════════════════════════════════

class TestUpdateResults:
    """Tests for PUT /api/ad-tests/{test_id}/results"""

    def test_update_results_requires_auth(self):
        """Test update results requires authentication"""
        response = requests.put(f"{BASE_URL}/api/ad-tests/some-test-id/results", json={})
        assert response.status_code in [401, 403]

    def test_update_results_404_for_nonexistent_test(self):
        """Test update results returns 404 for non-existent test"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.put(
            f"{BASE_URL}/api/ad-tests/nonexistent-test-id/results",
            json={"variation_id": "var_a_12345", "spend": 10},
            headers=headers
        )
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# COMPLETE TEST ENDPOINT (AUTH)
# ═══════════════════════════════════════════════════════════════════

class TestCompleteAdTest:
    """Tests for POST /api/ad-tests/{test_id}/complete"""

    def test_complete_requires_auth(self):
        """Test complete endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/ad-tests/some-test-id/complete")
        assert response.status_code in [401, 403]

    def test_complete_404_for_nonexistent_test(self):
        """Test complete returns 404 for non-existent test"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.post(
            f"{BASE_URL}/api/ad-tests/nonexistent-test-id/complete",
            headers=headers
        )
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# LAUNCH SIMULATOR ENDPOINT (AUTH)
# ═══════════════════════════════════════════════════════════════════

class TestLaunchSimulator:
    """Tests for GET /api/ad-tests/simulate/{product_id}"""

    def test_simulate_requires_auth(self):
        """Test simulate endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ad-tests/simulate/{TEST_PRODUCT_ID}")
        assert response.status_code in [401, 403]

    def test_simulate_returns_200_for_valid_product(self):
        """Test simulate returns 200 for valid product"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/simulate/{TEST_PRODUCT_ID}",
            headers=headers
        )
        assert response.status_code == 200, f"Got {response.status_code}: {response.text}"

    def test_simulate_returns_simulation_object(self):
        """Test simulate returns simulation object with projections"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/simulate/{TEST_PRODUCT_ID}",
            headers=headers
        )
        data = response.json()
        assert "simulation" in data, f"Missing 'simulation' in response: {data}"
        sim = data["simulation"]
        assert "profit_per_sale" in sim
        assert "estimated_cvr" in sim
        assert "estimated_cpc" in sim
        assert "estimated_cpa" in sim
        assert "daily_sales_range" in sim
        assert "daily_profit_range" in sim

    def test_simulate_daily_ranges_structure(self):
        """Test simulate daily ranges have low/high structure"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/simulate/{TEST_PRODUCT_ID}",
            headers=headers
        )
        data = response.json()
        sim = data["simulation"]
        assert "low" in sim["daily_sales_range"]
        assert "high" in sim["daily_sales_range"]
        assert "low" in sim["daily_profit_range"]
        assert "high" in sim["daily_profit_range"]

    def test_simulate_returns_potential(self):
        """Test simulate returns potential level"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/simulate/{TEST_PRODUCT_ID}",
            headers=headers
        )
        data = response.json()
        assert "potential" in data
        assert data["potential"] in ["High", "Moderate", "Risky"]

    def test_simulate_returns_risks_array(self):
        """Test simulate returns risks array"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/simulate/{TEST_PRODUCT_ID}",
            headers=headers
        )
        data = response.json()
        assert "risks" in data
        assert isinstance(data["risks"], list)

    def test_simulate_returns_guidance(self):
        """Test simulate returns guidance text"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/simulate/{TEST_PRODUCT_ID}",
            headers=headers
        )
        data = response.json()
        assert "guidance" in data
        assert isinstance(data["guidance"], str)
        assert len(data["guidance"]) > 0

    def test_simulate_returns_breakeven_days(self):
        """Test simulate returns breakeven_days"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/simulate/{TEST_PRODUCT_ID}",
            headers=headers
        )
        data = response.json()
        sim = data["simulation"]
        assert "breakeven_days" in sim

    def test_simulate_404_for_nonexistent_product(self):
        """Test simulate returns 404 for non-existent product"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/simulate/nonexistent-id-12345",
            headers=headers
        )
        assert response.status_code == 404

    def test_simulate_returns_inputs_used(self):
        """Test simulate returns inputs_used object"""
        headers = get_headers()
        if not headers or "Authorization" not in headers:
            pytest.skip("Auth not available")
        response = requests.get(
            f"{BASE_URL}/api/ad-tests/simulate/{TEST_PRODUCT_ID}",
            headers=headers
        )
        data = response.json()
        assert "inputs_used" in data
        inputs = data["inputs_used"]
        assert "launch_score" in inputs
        assert "trend_stage" in inputs
        assert "competition" in inputs


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
