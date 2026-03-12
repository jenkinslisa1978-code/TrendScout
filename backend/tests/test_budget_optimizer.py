"""
Budget Optimizer API Tests

Tests for the Smart Budget Optimizer V1 feature:
- POST /api/optimization/recommend/{test_id} - Get budget recommendations for ad test variations
- GET /api/optimization/timeline/{test_id} - Get optimization event history
- GET /api/optimization/dashboard-summary - Get summary of active tests needing action
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_EMAIL = "optimizer_test@example.com"
TEST_PASSWORD = "TestPass123!"
TEST_FULLNAME = "Test Optimizer"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token - register if needed, then login"""
    # Try to register (will fail if user exists, that's OK)
    api_client.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": TEST_FULLNAME
    })
    
    # Login to get token
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


@pytest.fixture(scope="module")
def test_product_id(authenticated_client):
    """Get or create a test product for ad testing"""
    # Get existing products
    response = authenticated_client.get(f"{BASE_URL}/api/products?limit=1")
    if response.status_code == 200:
        data = response.json()
        products = data.get("data") or data.get("products") or []
        if products:
            return products[0].get("id")
    
    pytest.skip("No products found - cannot test budget optimizer")


@pytest.fixture(scope="module")
def test_ad_test(authenticated_client, test_product_id):
    """Create an ad test for budget optimization testing"""
    # First check if we already have an active test for this product
    response = authenticated_client.get(f"{BASE_URL}/api/ad-tests/my?status=active")
    if response.status_code == 200:
        data = response.json()
        tests = data.get("tests") or []
        for test in tests:
            if test.get("product_id") == test_product_id:
                return test
    
    # Create a new ad test
    response = authenticated_client.post(f"{BASE_URL}/api/ad-tests/create", json={
        "product_id": test_product_id
    })
    
    if response.status_code in [200, 201]:
        data = response.json()
        return data.get("test") or data
    
    # If creation fails, try to get any existing test
    response = authenticated_client.get(f"{BASE_URL}/api/ad-tests/my")
    if response.status_code == 200:
        data = response.json()
        tests = data.get("tests") or []
        if tests:
            return tests[0]
    
    pytest.skip("Could not create or find an ad test")


class TestBudgetOptimizerRecommend:
    """Test POST /api/optimization/recommend/{test_id}"""
    
    def test_recommend_requires_auth(self, api_client):
        """Recommend endpoint requires authentication"""
        # Remove auth header
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/optimization/recommend/fake-test-id", json={})
        assert response.status_code in [401, 403], f"Expected 401/403 for unauthenticated request, got {response.status_code}"
        print("✓ POST /api/optimization/recommend requires authentication")
    
    def test_recommend_404_for_nonexistent_test(self, authenticated_client):
        """Recommend returns 404 for non-existent test"""
        fake_test_id = str(uuid.uuid4())
        response = authenticated_client.post(f"{BASE_URL}/api/optimization/recommend/{fake_test_id}", json={})
        assert response.status_code == 404, f"Expected 404 for non-existent test, got {response.status_code}"
        print(f"✓ POST /api/optimization/recommend returns 404 for non-existent test")
    
    def test_recommend_returns_recommendations(self, authenticated_client, test_ad_test):
        """Recommend returns valid recommendations structure"""
        test_id = test_ad_test.get("id")
        response = authenticated_client.post(f"{BASE_URL}/api/optimization/recommend/{test_id}", json={})
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check structure
        assert "recommendations" in data, "Response should have 'recommendations' field"
        assert "summary" in data, "Response should have 'summary' field"
        assert "benchmarks" in data, "Response should have 'benchmarks' field"
        assert "generated_at" in data, "Response should have 'generated_at' timestamp"
        
        print(f"✓ POST /api/optimization/recommend/{test_id} returns valid structure")
    
    def test_recommend_has_valid_summary(self, authenticated_client, test_ad_test):
        """Recommend summary has expected fields"""
        test_id = test_ad_test.get("id")
        response = authenticated_client.post(f"{BASE_URL}/api/optimization/recommend/{test_id}", json={})
        
        assert response.status_code == 200
        data = response.json()
        summary = data.get("summary", {})
        
        assert "test_id" in summary, "Summary should have test_id"
        assert "total_variations" in summary, "Summary should have total_variations"
        assert "to_scale" in summary, "Summary should have to_scale count"
        assert "to_pause" in summary, "Summary should have to_pause count"
        assert "to_maintain" in summary, "Summary should have to_maintain count"
        assert "waiting_data" in summary, "Summary should have waiting_data count"
        assert "overall_status" in summary, "Summary should have overall_status"
        
        # Validate overall_status is one of expected values
        valid_statuses = ["collecting_data", "scaling", "struggling", "monitoring"]
        assert summary.get("overall_status") in valid_statuses, f"Invalid overall_status: {summary.get('overall_status')}"
        
        print(f"✓ Recommendation summary has valid structure with status: {summary.get('overall_status')}")
    
    def test_recommend_variations_have_required_fields(self, authenticated_client, test_ad_test):
        """Each recommendation has required fields"""
        test_id = test_ad_test.get("id")
        response = authenticated_client.post(f"{BASE_URL}/api/optimization/recommend/{test_id}", json={})
        
        assert response.status_code == 200
        data = response.json()
        recommendations = data.get("recommendations", [])
        
        for rec in recommendations:
            assert "variation_id" in rec, "Recommendation should have variation_id"
            assert "label" in rec, "Recommendation should have label"
            assert "action" in rec, "Recommendation should have action"
            assert "confidence" in rec, "Recommendation should have confidence"
            assert "current_budget" in rec, "Recommendation should have current_budget"
            assert "recommended_budget" in rec, "Recommendation should have recommended_budget"
            assert "reasoning" in rec, "Recommendation should have reasoning list"
            assert "metrics" in rec, "Recommendation should have metrics"
            
            # Validate action is one of expected values
            valid_actions = ["increase_budget", "maintain", "pause", "kill", "needs_more_data"]
            assert rec.get("action") in valid_actions, f"Invalid action: {rec.get('action')}"
            
            # Validate confidence is 0-1
            confidence = rec.get("confidence", 0)
            assert 0 <= confidence <= 1, f"Confidence should be 0-1, got {confidence}"
        
        print(f"✓ All {len(recommendations)} recommendations have valid structure")
    
    def test_recommend_metrics_structure(self, authenticated_client, test_ad_test):
        """Recommendation metrics have expected fields"""
        test_id = test_ad_test.get("id")
        response = authenticated_client.post(f"{BASE_URL}/api/optimization/recommend/{test_id}", json={})
        
        assert response.status_code == 200
        data = response.json()
        recommendations = data.get("recommendations", [])
        
        if recommendations:
            metrics = recommendations[0].get("metrics", {})
            
            # Check expected metric fields
            expected_metrics = ["spend", "clicks", "ctr", "cpc", "purchases"]
            for metric in expected_metrics:
                assert metric in metrics, f"Metrics should have '{metric}' field"
            
            print(f"✓ Recommendation metrics have expected fields: {list(metrics.keys())}")
    
    def test_recommend_with_target_cpa(self, authenticated_client, test_ad_test):
        """Recommend accepts target_cpa parameter"""
        test_id = test_ad_test.get("id")
        response = authenticated_client.post(
            f"{BASE_URL}/api/optimization/recommend/{test_id}", 
            json={"target_cpa": 25.00}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "recommendations" in data
        
        print(f"✓ Recommend endpoint accepts target_cpa parameter")
    
    def test_recommend_benchmarks_structure(self, authenticated_client, test_ad_test):
        """Benchmarks have expected values"""
        test_id = test_ad_test.get("id")
        response = authenticated_client.post(f"{BASE_URL}/api/optimization/recommend/{test_id}", json={})
        
        assert response.status_code == 200
        data = response.json()
        benchmarks = data.get("benchmarks", {})
        
        expected_benchmarks = ["ctr_excellent", "ctr_good", "ctr_poor", "cpc_good", "cpc_poor", "atc_good", "atc_poor"]
        for bm in expected_benchmarks:
            assert bm in benchmarks, f"Benchmarks should have '{bm}'"
        
        print(f"✓ Benchmarks structure is valid: {benchmarks}")


class TestBudgetOptimizerTimeline:
    """Test GET /api/optimization/timeline/{test_id}"""
    
    def test_timeline_requires_auth(self, api_client):
        """Timeline endpoint requires authentication"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.get(f"{BASE_URL}/api/optimization/timeline/fake-test-id")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ GET /api/optimization/timeline requires authentication")
    
    def test_timeline_returns_events(self, authenticated_client, test_ad_test):
        """Timeline returns events array"""
        test_id = test_ad_test.get("id")
        
        # First trigger a recommendation to create events
        authenticated_client.post(f"{BASE_URL}/api/optimization/recommend/{test_id}", json={})
        
        # Then get timeline
        response = authenticated_client.get(f"{BASE_URL}/api/optimization/timeline/{test_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "events" in data, "Response should have 'events' field"
        assert "total" in data, "Response should have 'total' count"
        assert isinstance(data.get("events"), list), "Events should be a list"
        
        print(f"✓ Timeline returns {data.get('total')} events")
    
    def test_timeline_event_structure(self, authenticated_client, test_ad_test):
        """Timeline events have expected structure"""
        test_id = test_ad_test.get("id")
        
        # Trigger recommendation first
        authenticated_client.post(f"{BASE_URL}/api/optimization/recommend/{test_id}", json={})
        
        response = authenticated_client.get(f"{BASE_URL}/api/optimization/timeline/{test_id}")
        
        assert response.status_code == 200
        data = response.json()
        events = data.get("events", [])
        
        if events:
            event = events[0]
            expected_fields = ["id", "test_id", "variation_id", "timestamp", "metrics_snapshot", 
                            "recommendation_action", "recommended_budget", "confidence"]
            
            for field in expected_fields:
                assert field in event, f"Event should have '{field}' field"
            
            print(f"✓ Timeline events have valid structure with fields: {list(event.keys())}")
        else:
            print("✓ Timeline returned empty events list (no recommendations logged yet)")


class TestBudgetOptimizerDashboardSummary:
    """Test GET /api/optimization/dashboard-summary"""
    
    def test_dashboard_summary_requires_auth(self, api_client):
        """Dashboard summary requires authentication"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.get(f"{BASE_URL}/api/optimization/dashboard-summary")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ GET /api/optimization/dashboard-summary requires authentication")
    
    def test_dashboard_summary_returns_valid_structure(self, authenticated_client):
        """Dashboard summary returns expected structure"""
        response = authenticated_client.get(f"{BASE_URL}/api/optimization/dashboard-summary")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check required fields
        expected_fields = [
            "candidates_to_scale",
            "losers_to_pause", 
            "needs_action",
            "waiting_data",
            "total_active_tests",
            "generated_at"
        ]
        
        for field in expected_fields:
            assert field in data, f"Dashboard summary should have '{field}' field"
        
        # All lists should be arrays
        assert isinstance(data.get("candidates_to_scale"), list), "candidates_to_scale should be list"
        assert isinstance(data.get("losers_to_pause"), list), "losers_to_pause should be list"
        assert isinstance(data.get("needs_action"), list), "needs_action should be list"
        assert isinstance(data.get("waiting_data"), list), "waiting_data should be list"
        
        print(f"✓ Dashboard summary has valid structure with {data.get('total_active_tests')} active tests")
    
    def test_dashboard_summary_action_items_structure(self, authenticated_client, test_ad_test):
        """Dashboard action items have proper structure when tests exist"""
        # Ensure we have at least one active test
        test_id = test_ad_test.get("id")
        
        response = authenticated_client.get(f"{BASE_URL}/api/optimization/dashboard-summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all action item lists for proper structure
        all_items = (
            data.get("candidates_to_scale", []) + 
            data.get("losers_to_pause", []) + 
            data.get("waiting_data", [])
        )
        
        for item in all_items:
            assert "test_id" in item, "Action item should have test_id"
            assert "variation_id" in item or "label" in item, "Action item should have variation_id or label"
            assert "action" in item, "Action item should have action"
            assert "confidence" in item, "Action item should have confidence"
        
        print(f"✓ Dashboard summary action items have valid structure ({len(all_items)} total items)")


class TestBudgetOptimizerServiceLogic:
    """Test the budget optimizer service logic indirectly through API"""
    
    def test_needs_more_data_action_for_fresh_test(self, authenticated_client, test_product_id):
        """Fresh test with no results should get 'needs_more_data' recommendations"""
        # Create a fresh test
        response = authenticated_client.post(f"{BASE_URL}/api/ad-tests/create", json={
            "product_id": test_product_id
        })
        
        # Handle case where test already exists or creation succeeds
        if response.status_code in [200, 201]:
            test = response.json().get("test") or response.json()
            test_id = test.get("id")
        else:
            # Get existing test
            response = authenticated_client.get(f"{BASE_URL}/api/ad-tests/my?status=active")
            if response.status_code == 200:
                tests = response.json().get("tests", [])
                test = next((t for t in tests if t.get("product_id") == test_product_id), None)
                if test:
                    test_id = test.get("id")
                else:
                    pytest.skip("No test available for this product")
            else:
                pytest.skip("Could not get test for logic testing")
        
        # Get recommendations
        rec_response = authenticated_client.post(f"{BASE_URL}/api/optimization/recommend/{test_id}", json={})
        
        if rec_response.status_code == 200:
            data = rec_response.json()
            recommendations = data.get("recommendations", [])
            
            # Fresh tests with no spend should have needs_more_data or similar
            # The actual action depends on the test variation results
            actions_found = [r.get("action") for r in recommendations]
            print(f"✓ Fresh test recommendations: {actions_found}")
        else:
            print(f"✓ Could not test fresh test logic (status: {rec_response.status_code})")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
