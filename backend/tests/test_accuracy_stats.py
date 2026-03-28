"""
Test suite for Accuracy Stats API endpoint
Tests the new prediction accuracy tracking system that replaces fabricated stats
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://db-seeding-async.preview.emergentagent.com')


class TestAccuracyStatsEndpoint:
    """Tests for GET /api/accuracy/stats endpoint"""
    
    def test_accuracy_stats_returns_ok_status(self):
        """Verify endpoint returns status:ok"""
        response = requests.get(f"{BASE_URL}/api/accuracy/stats")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok", f"Expected status 'ok', got {data.get('status')}"
        print("SUCCESS: /api/accuracy/stats returns status:ok")
    
    def test_accuracy_stats_has_required_fields(self):
        """Verify response contains all required fields"""
        response = requests.get(f"{BASE_URL}/api/accuracy/stats")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "status",
            "total_tracked",
            "total_reviewed",
            "has_enough_data",
            "margin_accuracy_pct",
            "trend_accuracy_pct",
            "last_updated"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        print(f"SUCCESS: All required fields present: {required_fields}")
    
    def test_accuracy_stats_no_fabricated_numbers(self):
        """Verify no fabricated stats (85% accuracy, 2000+ sellers)"""
        response = requests.get(f"{BASE_URL}/api/accuracy/stats")
        assert response.status_code == 200
        data = response.json()
        
        # With no tracked predictions, should show has_enough_data: false
        # and null accuracy percentages
        total_tracked = data.get("total_tracked", 0)
        total_reviewed = data.get("total_reviewed", 0)
        has_enough_data = data.get("has_enough_data")
        
        # If less than 5 reviewed predictions, has_enough_data should be false
        if total_reviewed < 5:
            assert has_enough_data == False, f"Expected has_enough_data=false when total_reviewed={total_reviewed}"
            assert data.get("margin_accuracy_pct") is None, "margin_accuracy_pct should be null when not enough data"
            assert data.get("trend_accuracy_pct") is None, "trend_accuracy_pct should be null when not enough data"
            print(f"SUCCESS: No fabricated stats - total_tracked={total_tracked}, has_enough_data={has_enough_data}")
        else:
            # If we have enough data, percentages should be real numbers
            assert isinstance(data.get("margin_accuracy_pct"), (int, float)), "margin_accuracy_pct should be a number"
            assert isinstance(data.get("trend_accuracy_pct"), (int, float)), "trend_accuracy_pct should be a number"
            print(f"SUCCESS: Real stats returned - margin={data.get('margin_accuracy_pct')}%, trend={data.get('trend_accuracy_pct')}%")
    
    def test_accuracy_stats_total_tracked_is_integer(self):
        """Verify total_tracked is a non-negative integer"""
        response = requests.get(f"{BASE_URL}/api/accuracy/stats")
        assert response.status_code == 200
        data = response.json()
        
        total_tracked = data.get("total_tracked")
        assert isinstance(total_tracked, int), f"total_tracked should be int, got {type(total_tracked)}"
        assert total_tracked >= 0, f"total_tracked should be non-negative, got {total_tracked}"
        print(f"SUCCESS: total_tracked is valid integer: {total_tracked}")
    
    def test_accuracy_stats_building_state(self):
        """Verify 'building track record' state when not enough data"""
        response = requests.get(f"{BASE_URL}/api/accuracy/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Currently we expect 0 tracked predictions (new system)
        if data.get("total_reviewed", 0) < 5:
            assert data.get("has_enough_data") == False
            print("SUCCESS: System correctly shows 'building' state with has_enough_data=false")
        else:
            assert data.get("has_enough_data") == True
            print("SUCCESS: System has enough data for real accuracy metrics")


class TestAccuracyEndpointIntegrity:
    """Tests for endpoint integrity and error handling"""
    
    def test_accuracy_stats_response_time(self):
        """Verify endpoint responds within acceptable time"""
        import time
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/accuracy/stats", timeout=10)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 5, f"Response took too long: {elapsed:.2f}s"
        print(f"SUCCESS: Response time acceptable: {elapsed:.2f}s")
    
    def test_accuracy_stats_content_type(self):
        """Verify response is JSON"""
        response = requests.get(f"{BASE_URL}/api/accuracy/stats")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        print("SUCCESS: Response Content-Type is application/json")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
