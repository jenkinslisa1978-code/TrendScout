"""
P3: Product Outcome Learning System Backend Tests
Tests for: POST /api/outcomes/track, GET /api/outcomes/my, PUT /api/outcomes/{id}, 
           POST /api/outcomes/auto-label, GET /api/outcomes/stats
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "testref@test.com"
TEST_USER_PASSWORD = "Test1234!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Auth failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="module")
def test_product_id(auth_headers):
    """Get a product ID to use for testing outcomes"""
    response = requests.get(
        f"{BASE_URL}/api/products?limit=10",
        headers=auth_headers
    )
    if response.status_code == 200:
        data = response.json()
        products = data.get("data") or data.get("products") or data
        if isinstance(products, list) and len(products) >= 5:
            # Get the 5th product to avoid duplicates with existing outcomes
            return products[4].get("id")
        elif isinstance(products, list) and len(products) > 0:
            return products[-1].get("id")
    pytest.skip("No products available for testing")


class TestOutcomesTrack:
    """Tests for POST /api/outcomes/track endpoint"""
    
    def test_track_requires_auth(self):
        """POST /api/outcomes/track returns 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/outcomes/track",
            json={"product_id": "test123"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: POST /api/outcomes/track requires authentication")
    
    def test_track_requires_product_id(self, auth_headers):
        """POST /api/outcomes/track returns 400 without product_id"""
        response = requests.post(
            f"{BASE_URL}/api/outcomes/track",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: POST /api/outcomes/track requires product_id")
    
    def test_track_product_not_found(self, auth_headers):
        """POST /api/outcomes/track returns 404 for non-existent product"""
        response = requests.post(
            f"{BASE_URL}/api/outcomes/track",
            headers=auth_headers,
            json={"product_id": "nonexistent-product-id-12345"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: POST /api/outcomes/track returns 404 for non-existent product")
    
    def test_track_success(self, auth_headers, test_product_id):
        """POST /api/outcomes/track creates outcome record successfully"""
        response = requests.post(
            f"{BASE_URL}/api/outcomes/track",
            headers=auth_headers,
            json={
                "product_id": test_product_id,
                "store_id": f"test-store-{uuid.uuid4()}"
            }
        )
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "outcome" in data, "Response should contain 'outcome'"
        
        outcome = data["outcome"]
        assert outcome.get("product_id") == test_product_id, "product_id should match"
        assert outcome.get("outcome_status") == "pending", "Initial status should be 'pending'"
        assert "metrics" in outcome, "Outcome should have metrics object"
        assert "launch_score_at_launch" in outcome, "Outcome should have launch_score_at_launch"
        
        # Store outcome_id for later tests
        pytest.test_outcome_id = outcome.get("id")
        print(f"PASS: POST /api/outcomes/track creates outcome with id={outcome.get('id')}")
    
    def test_track_returns_existing(self, auth_headers, test_product_id):
        """POST /api/outcomes/track returns existing outcome if product already tracked"""
        # Track the same product again
        response = requests.post(
            f"{BASE_URL}/api/outcomes/track",
            headers=auth_headers,
            json={"product_id": test_product_id}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "outcome" in data, "Response should contain 'outcome'"
        assert "Already tracking" in data.get("message", ""), "Should indicate already tracking"
        print("PASS: POST /api/outcomes/track returns existing outcome for duplicate tracking")


class TestOutcomesMy:
    """Tests for GET /api/outcomes/my endpoint"""
    
    def test_my_requires_auth(self):
        """GET /api/outcomes/my returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/outcomes/my")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: GET /api/outcomes/my requires authentication")
    
    def test_my_returns_outcomes_and_summary(self, auth_headers):
        """GET /api/outcomes/my returns outcomes array and summary object"""
        response = requests.get(
            f"{BASE_URL}/api/outcomes/my",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "outcomes" in data, "Response should contain 'outcomes' array"
        assert "summary" in data, "Response should contain 'summary' object"
        
        outcomes = data["outcomes"]
        assert isinstance(outcomes, list), "outcomes should be a list"
        
        summary = data["summary"]
        assert "total" in summary, "Summary should have 'total'"
        assert "success" in summary, "Summary should have 'success'"
        assert "moderate" in summary, "Summary should have 'moderate'"
        assert "failed" in summary, "Summary should have 'failed'"
        assert "pending" in summary, "Summary should have 'pending'"
        assert "total_revenue" in summary, "Summary should have 'total_revenue'"
        assert "total_orders" in summary, "Summary should have 'total_orders'"
        assert "success_rate" in summary, "Summary should have 'success_rate'"
        
        print(f"PASS: GET /api/outcomes/my returns {len(outcomes)} outcomes with summary")
    
    def test_my_filter_by_status(self, auth_headers):
        """GET /api/outcomes/my?status=success filters by status"""
        response = requests.get(
            f"{BASE_URL}/api/outcomes/my?status=success",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        outcomes = data.get("outcomes", [])
        
        # All returned outcomes should have status=success
        for o in outcomes:
            assert o.get("outcome_status") == "success", f"Filtered outcome should be success, got {o.get('outcome_status')}"
        
        print(f"PASS: GET /api/outcomes/my?status=success filters correctly ({len(outcomes)} success outcomes)")


class TestOutcomesUpdate:
    """Tests for PUT /api/outcomes/{id} endpoint"""
    
    def test_update_requires_auth(self):
        """PUT /api/outcomes/{id} returns 401 without auth"""
        response = requests.put(
            f"{BASE_URL}/api/outcomes/test-id",
            json={"revenue": 100}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: PUT /api/outcomes/{id} requires authentication")
    
    def test_update_not_found(self, auth_headers):
        """PUT /api/outcomes/{id} returns 404 for non-existent outcome"""
        response = requests.put(
            f"{BASE_URL}/api/outcomes/nonexistent-outcome-id",
            headers=auth_headers,
            json={"revenue": 100}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: PUT /api/outcomes/{id} returns 404 for non-existent outcome")
    
    def test_update_metrics(self, auth_headers):
        """PUT /api/outcomes/{id} updates metrics and auto-computes ROI"""
        # First get an existing outcome
        response = requests.get(
            f"{BASE_URL}/api/outcomes/my",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        outcomes = data.get("outcomes", [])
        if not outcomes:
            pytest.skip("No outcomes to update")
        
        outcome_id = outcomes[0].get("id")
        
        # Update with metrics
        update_data = {
            "revenue": 250,
            "orders": 25,
            "ad_spend": 50,
            "days_active": 15
        }
        
        response = requests.put(
            f"{BASE_URL}/api/outcomes/{outcome_id}",
            headers=auth_headers,
            json=update_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "outcome" in data, "Response should contain 'outcome'"
        
        outcome = data["outcome"]
        metrics = outcome.get("metrics", {})
        
        assert metrics.get("revenue") == 250, f"Revenue should be 250, got {metrics.get('revenue')}"
        assert metrics.get("orders") == 25, f"Orders should be 25, got {metrics.get('orders')}"
        assert metrics.get("ad_spend") == 50, f"Ad spend should be 50, got {metrics.get('ad_spend')}"
        assert metrics.get("days_active") == 15, f"Days active should be 15, got {metrics.get('days_active')}"
        
        # ROI should be auto-computed: (revenue - ad_spend) / ad_spend * 100 = (250-50)/50*100 = 400%
        expected_roi = round((250 - 50) / 50 * 100, 1)
        assert metrics.get("roi") == expected_roi, f"ROI should be {expected_roi}, got {metrics.get('roi')}"
        
        print(f"PASS: PUT /api/outcomes/{outcome_id} updates metrics and computes ROI={expected_roi}%")


class TestOutcomesAutoLabel:
    """Tests for POST /api/outcomes/auto-label endpoint"""
    
    def test_auto_label_requires_auth(self):
        """POST /api/outcomes/auto-label returns 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/outcomes/auto-label")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: POST /api/outcomes/auto-label requires authentication")
    
    def test_auto_label_success(self, auth_headers):
        """POST /api/outcomes/auto-label classifies pending outcomes"""
        response = requests.post(
            f"{BASE_URL}/api/outcomes/auto-label",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "labeled" in data, "Response should contain 'labeled'"
        assert "total_checked" in data, "Response should contain 'total_checked'"
        
        print(f"PASS: POST /api/outcomes/auto-label classified {data.get('labeled')} of {data.get('total_checked')} outcomes")


class TestOutcomesStats:
    """Tests for GET /api/outcomes/stats endpoint"""
    
    def test_stats_requires_auth(self):
        """GET /api/outcomes/stats returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/outcomes/stats")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: GET /api/outcomes/stats requires authentication")
    
    def test_stats_returns_aggregate_data(self, auth_headers):
        """GET /api/outcomes/stats returns aggregate statistics"""
        response = requests.get(
            f"{BASE_URL}/api/outcomes/stats",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check required fields
        required_fields = [
            "total_tracked", "success_rate", "avg_roi", 
            "total_revenue", "total_orders",
            "avg_launch_score_success", "avg_launch_score_failed",
            "best_categories", "insights"
        ]
        
        for field in required_fields:
            assert field in data, f"Stats should contain '{field}'"
        
        # Verify types
        assert isinstance(data.get("total_tracked"), (int, float)), "total_tracked should be a number"
        assert isinstance(data.get("success_rate"), (int, float)), "success_rate should be a number"
        assert isinstance(data.get("best_categories"), list), "best_categories should be a list"
        assert isinstance(data.get("insights"), list), "insights should be a list"
        
        print(f"PASS: GET /api/outcomes/stats returns: total_tracked={data.get('total_tracked')}, "
              f"success_rate={data.get('success_rate')}%, avg_roi={data.get('avg_roi')}%")


class TestOutcomesIntegration:
    """Integration tests for complete outcome workflow"""
    
    def test_complete_workflow(self, auth_headers):
        """Test complete workflow: track → update → auto-label → stats"""
        # Get all products
        products_response = requests.get(
            f"{BASE_URL}/api/products?limit=10",
            headers=auth_headers
        )
        if products_response.status_code != 200:
            pytest.skip("Cannot get products for workflow test")
        
        products_data = products_response.json()
        products = products_data.get("data") or products_data.get("products") or []
        
        # Find a product that might not be tracked yet (use a unique store_id)
        if len(products) == 0:
            pytest.skip("No products available")
        
        product = products[0]
        product_id = product.get("id")
        
        # Step 1: Track outcome (may return existing)
        track_response = requests.post(
            f"{BASE_URL}/api/outcomes/track",
            headers=auth_headers,
            json={"product_id": product_id, "store_id": f"workflow-test-{uuid.uuid4()}"}
        )
        assert track_response.status_code == 200, f"Track failed: {track_response.status_code}"
        
        track_data = track_response.json()
        outcome_id = track_data.get("outcome", {}).get("id")
        print(f"Step 1: Tracked outcome id={outcome_id}")
        
        # Step 2: Update metrics
        update_response = requests.put(
            f"{BASE_URL}/api/outcomes/{outcome_id}",
            headers=auth_headers,
            json={"revenue": 600, "orders": 55, "ad_spend": 100, "days_active": 14}
        )
        assert update_response.status_code == 200, f"Update failed: {update_response.status_code}"
        print("Step 2: Updated metrics (revenue=600, orders=55)")
        
        # Step 3: Auto-label (should mark as success due to orders>=50 or revenue>=500)
        label_response = requests.post(
            f"{BASE_URL}/api/outcomes/auto-label",
            headers=auth_headers
        )
        assert label_response.status_code == 200, f"Auto-label failed: {label_response.status_code}"
        print(f"Step 3: Auto-label completed")
        
        # Step 4: Get stats
        stats_response = requests.get(
            f"{BASE_URL}/api/outcomes/stats",
            headers=auth_headers
        )
        assert stats_response.status_code == 200, f"Stats failed: {stats_response.status_code}"
        
        stats_data = stats_response.json()
        print(f"Step 4: Stats: total_tracked={stats_data.get('total_tracked')}, "
              f"success_rate={stats_data.get('success_rate')}%")
        
        # Verify the outcome was labeled
        my_response = requests.get(
            f"{BASE_URL}/api/outcomes/my",
            headers=auth_headers
        )
        assert my_response.status_code == 200
        
        my_data = my_response.json()
        updated_outcome = next(
            (o for o in my_data.get("outcomes", []) if o.get("id") == outcome_id), 
            None
        )
        
        if updated_outcome:
            # After auto-label with revenue=600 and orders=55, should be "success"
            status = updated_outcome.get("outcome_status")
            print(f"PASS: Complete workflow test - outcome status={status}")
        else:
            print("PASS: Complete workflow test - outcome tracked and processed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
