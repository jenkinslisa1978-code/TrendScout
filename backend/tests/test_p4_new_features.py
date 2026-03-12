"""
Tests for P4 New Features:
- P0 Prediction Accuracy System (GET /api/outcomes/prediction-accuracy)
- P1 Opportunity Radar Live Feed (GET /api/radar/live-events)
- P2 Saturation Radar (GET /api/products/{id}/saturation)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "testref@test.com"
TEST_PASSWORD = "Test1234!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Create session with auth header"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


@pytest.fixture(scope="module")
def sample_product_id(api_client):
    """Get a valid product ID for testing"""
    response = api_client.get(f"{BASE_URL}/api/products?limit=1")
    if response.status_code == 200:
        data = response.json()
        products = data.get("data") or data.get("products", [])
        if products:
            return products[0].get("id")
    pytest.skip("No products found for testing")


# ═══════════════════════════════════════════════════════════════════
# P0: Prediction Accuracy System Tests
# ═══════════════════════════════════════════════════════════════════

class TestPredictionAccuracy:
    """Tests for GET /api/outcomes/prediction-accuracy"""

    def test_prediction_accuracy_requires_auth(self):
        """Prediction accuracy endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/outcomes/prediction-accuracy")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Prediction accuracy endpoint requires auth (401/403)")

    def test_prediction_accuracy_returns_correct_structure(self, api_client):
        """Prediction accuracy returns expected fields"""
        response = api_client.get(f"{BASE_URL}/api/outcomes/prediction-accuracy")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Required fields
        assert "accuracy_pct" in data, "Missing accuracy_pct"
        assert "sample_size" in data, "Missing sample_size"
        assert "successful_predictions" in data, "Missing successful_predictions"
        assert "failed_predictions" in data, "Missing failed_predictions"
        assert "score_buckets" in data, "Missing score_buckets"
        assert "insights" in data, "Missing insights"
        assert "insufficient_data" in data, "Missing insufficient_data"
        
        # Type validation
        assert isinstance(data["accuracy_pct"], (int, float)), "accuracy_pct should be numeric"
        assert isinstance(data["sample_size"], int), "sample_size should be int"
        assert isinstance(data["successful_predictions"], int), "successful_predictions should be int"
        assert isinstance(data["failed_predictions"], int), "failed_predictions should be int"
        assert isinstance(data["score_buckets"], list), "score_buckets should be array"
        assert isinstance(data["insights"], list), "insights should be array"
        assert isinstance(data["insufficient_data"], bool), "insufficient_data should be bool"
        
        print(f"✓ Prediction accuracy returns correct structure")
        print(f"  - accuracy_pct: {data['accuracy_pct']}%")
        print(f"  - sample_size: {data['sample_size']}")
        print(f"  - successful_predictions: {data['successful_predictions']}")
        print(f"  - failed_predictions: {data['failed_predictions']}")
        print(f"  - score_buckets: {len(data['score_buckets'])} buckets")
        print(f"  - insufficient_data: {data['insufficient_data']}")

    def test_prediction_accuracy_score_buckets_structure(self, api_client):
        """Score buckets have correct structure if present"""
        response = api_client.get(f"{BASE_URL}/api/outcomes/prediction-accuracy")
        assert response.status_code == 200
        
        data = response.json()
        for bucket in data.get("score_buckets", []):
            assert "range" in bucket, "Bucket missing range"
            assert "total" in bucket, "Bucket missing total"
            assert "success" in bucket, "Bucket missing success"
            assert "success_rate" in bucket, "Bucket missing success_rate"
            assert bucket["range"] in ["80+", "60-79", "40-59", "<40"], f"Invalid bucket range: {bucket['range']}"
        
        print(f"✓ Score buckets have correct structure")

    def test_prediction_accuracy_insights_structure(self, api_client):
        """Insights have correct structure if present"""
        response = api_client.get(f"{BASE_URL}/api/outcomes/prediction-accuracy")
        assert response.status_code == 200
        
        data = response.json()
        for insight in data.get("insights", []):
            assert "text" in insight, "Insight missing text"
            assert "bucket" in insight, "Insight missing bucket"
            assert isinstance(insight["text"], str), "Insight text should be string"
        
        print(f"✓ Insights have correct structure ({len(data.get('insights', []))} insights)")


# ═══════════════════════════════════════════════════════════════════
# P1: Opportunity Radar Live Feed Tests
# ═══════════════════════════════════════════════════════════════════

class TestOpportunityRadar:
    """Tests for GET /api/radar/live-events"""

    def test_radar_live_events_requires_auth(self):
        """Live events endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/radar/live-events")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Radar live-events endpoint requires auth (401/403)")

    def test_radar_live_events_returns_correct_structure(self, api_client):
        """Live events returns expected fields"""
        response = api_client.get(f"{BASE_URL}/api/radar/live-events?limit=15")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Required fields
        assert "events" in data, "Missing events array"
        assert "total" in data, "Missing total count"
        assert "generated_at" in data, "Missing generated_at timestamp"
        
        # Type validation
        assert isinstance(data["events"], list), "events should be array"
        assert isinstance(data["total"], int), "total should be int"
        assert isinstance(data["generated_at"], str), "generated_at should be string"
        
        print(f"✓ Live events returns correct structure")
        print(f"  - events count: {len(data['events'])}")
        print(f"  - total: {data['total']}")
        print(f"  - generated_at: {data['generated_at']}")

    def test_radar_live_events_event_structure(self, api_client):
        """Each event has required fields"""
        response = api_client.get(f"{BASE_URL}/api/radar/live-events?limit=15")
        assert response.status_code == 200
        
        data = response.json()
        events = data.get("events", [])
        
        valid_types = ["trend_spike", "new_ads", "supplier_demand", "competition_drop"]
        
        for event in events:
            assert "type" in event, "Event missing type"
            assert event["type"] in valid_types, f"Invalid event type: {event['type']}"
            assert "title" in event, "Event missing title"
            assert "detail" in event, "Event missing detail"
            assert "product_id" in event, "Event missing product_id"
            assert "product_name" in event, "Event missing product_name"
            assert "launch_score" in event, "Event missing launch_score"
            assert "trend_stage" in event, "Event missing trend_stage"
            assert "timestamp" in event, "Event missing timestamp"
            # image_url can be empty string or None
            assert "image_url" in event, "Event missing image_url field"
        
        # Count event types
        type_counts = {}
        for event in events:
            t = event["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        
        print(f"✓ All events have correct structure")
        print(f"  - Event types: {type_counts}")

    def test_radar_live_events_limit_parameter(self, api_client):
        """Limit parameter works correctly"""
        response = api_client.get(f"{BASE_URL}/api/radar/live-events?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        events = data.get("events", [])
        
        assert len(events) <= 5, f"Expected max 5 events, got {len(events)}"
        print(f"✓ Limit parameter works correctly ({len(events)} events returned)")


# ═══════════════════════════════════════════════════════════════════
# P2: Saturation Radar Tests (Public endpoint - no auth needed)
# ═══════════════════════════════════════════════════════════════════

class TestSaturationRadar:
    """Tests for GET /api/products/{product_id}/saturation"""

    def test_saturation_endpoint_is_public(self, sample_product_id):
        """Saturation endpoint is publicly accessible (no auth needed)"""
        # No auth header
        response = requests.get(f"{BASE_URL}/api/products/{sample_product_id}/saturation")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Should be public endpoint."
        print(f"✓ Saturation endpoint is public (no auth required)")

    def test_saturation_returns_404_for_invalid_product(self):
        """Saturation returns 404 for non-existent product"""
        response = requests.get(f"{BASE_URL}/api/products/nonexistent-product-id-12345/saturation")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Saturation returns 404 for invalid product")

    def test_saturation_returns_correct_structure(self, sample_product_id):
        """Saturation returns expected fields"""
        response = requests.get(f"{BASE_URL}/api/products/{sample_product_id}/saturation")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Required fields
        assert "product_id" in data, "Missing product_id"
        assert "saturation_score" in data, "Missing saturation_score"
        assert "risk_level" in data, "Missing risk_level"
        assert "stores_detected" in data, "Missing stores_detected"
        assert "ads_detected" in data, "Missing ads_detected"
        assert "search_growth" in data, "Missing search_growth"
        assert "trend_stage" in data, "Missing trend_stage"
        assert "signals" in data, "Missing signals object"
        
        print(f"✓ Saturation returns correct structure")
        print(f"  - product_id: {data['product_id']}")
        print(f"  - saturation_score: {data['saturation_score']}/100")
        print(f"  - risk_level: {data['risk_level']}")
        print(f"  - stores_detected: {data['stores_detected']}")
        print(f"  - ads_detected: {data['ads_detected']}")
        print(f"  - search_growth: {data['search_growth']}")
        print(f"  - trend_stage: {data['trend_stage']}")

    def test_saturation_score_is_valid_range(self, sample_product_id):
        """Saturation score is between 0 and 100"""
        response = requests.get(f"{BASE_URL}/api/products/{sample_product_id}/saturation")
        assert response.status_code == 200
        
        data = response.json()
        score = data["saturation_score"]
        
        assert isinstance(score, (int, float)), "saturation_score should be numeric"
        assert 0 <= score <= 100, f"saturation_score should be 0-100, got {score}"
        print(f"✓ Saturation score is valid (0-100): {score}")

    def test_saturation_risk_level_is_valid(self, sample_product_id):
        """Risk level is one of Low/Medium/High"""
        response = requests.get(f"{BASE_URL}/api/products/{sample_product_id}/saturation")
        assert response.status_code == 200
        
        data = response.json()
        risk = data["risk_level"]
        
        valid_levels = ["Low", "Medium", "High"]
        assert risk in valid_levels, f"risk_level should be one of {valid_levels}, got {risk}"
        print(f"✓ Risk level is valid: {risk}")

    def test_saturation_signals_object(self, sample_product_id):
        """Signals object contains expected fields"""
        response = requests.get(f"{BASE_URL}/api/products/{sample_product_id}/saturation")
        assert response.status_code == 200
        
        data = response.json()
        signals = data["signals"]
        
        assert "stores" in signals, "Missing signals.stores"
        assert "ads" in signals, "Missing signals.ads"
        assert "search" in signals, "Missing signals.search"
        assert "trend" in signals, "Missing signals.trend"
        
        # Each signal should have value and label
        for signal_name, signal_data in signals.items():
            assert "value" in signal_data, f"signals.{signal_name} missing value"
            assert "label" in signal_data, f"signals.{signal_name} missing label"
        
        print("✓ Signals object has correct structure")


# ═══════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════

class TestIntegration:
    """Integration tests across new features"""

    def test_complete_workflow(self, api_client, sample_product_id):
        """Test complete workflow: get accuracy → get radar events → check saturation"""
        # 1. Get prediction accuracy
        acc_response = api_client.get(f"{BASE_URL}/api/outcomes/prediction-accuracy")
        assert acc_response.status_code == 200, "Failed to get prediction accuracy"
        
        # 2. Get radar events
        radar_response = api_client.get(f"{BASE_URL}/api/radar/live-events?limit=10")
        assert radar_response.status_code == 200, "Failed to get radar events"
        
        # 3. Get saturation for a product (public)
        sat_response = requests.get(f"{BASE_URL}/api/products/{sample_product_id}/saturation")
        assert sat_response.status_code == 200, "Failed to get saturation"
        
        print("✓ Complete workflow test passed")
        print(f"  - Prediction accuracy: {acc_response.json().get('accuracy_pct')}%")
        print(f"  - Radar events: {len(radar_response.json().get('events', []))} events")
        print(f"  - Saturation score: {sat_response.json().get('saturation_score')}/100")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
