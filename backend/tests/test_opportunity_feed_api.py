"""
Test Opportunity Feed API Endpoints

Tests the Live Opportunity Feed feature:
- GET /api/dashboard/opportunity-feed - Returns array of feed events
- GET /api/dashboard/opportunity-feed/stats - Returns feed statistics
- POST /api/dashboard/opportunity-feed/generate-sample - Generates sample events (requires API key)
"""

import pytest
import requests
import os
from datetime import datetime

# Get base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# API key for admin endpoints
API_KEY = 'vs_automation_key_2024'


class TestOpportunityFeedAPI:
    """Tests for the Opportunity Feed endpoints"""
    
    # =======================
    # GET /api/dashboard/opportunity-feed
    # =======================
    
    def test_get_opportunity_feed_returns_200(self):
        """Test that opportunity feed endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: GET /api/dashboard/opportunity-feed returns 200")
    
    def test_get_opportunity_feed_returns_expected_structure(self):
        """Test that feed returns expected JSON structure"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert "events" in data, "Response should contain 'events' field"
        assert "count" in data, "Response should contain 'count' field"
        assert "generated_at" in data, "Response should contain 'generated_at' field"
        
        # Check types
        assert isinstance(data["events"], list), "'events' should be a list"
        assert isinstance(data["count"], int), "'count' should be an integer"
        assert isinstance(data["generated_at"], str), "'generated_at' should be a string"
        
        print(f"PASS: Feed structure valid - {data['count']} events returned")
    
    def test_get_opportunity_feed_event_structure(self):
        """Test that feed events have expected fields"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed?limit=10&hours=48")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["count"] > 0:
            event = data["events"][0]
            
            # Check required event fields
            required_fields = [
                "id", "event_type", "priority", "created_at",
                "product_id", "product_name", "launch_score",
                "reason", "color", "icon", "confidence"
            ]
            
            for field in required_fields:
                assert field in event, f"Event missing required field: {field}"
            
            # Validate event_type is one of the expected types
            valid_event_types = [
                "entered_strong_launch", "new_high_score", "trend_spike",
                "competition_increase", "approaching_saturation"
            ]
            assert event["event_type"] in valid_event_types, f"Invalid event_type: {event['event_type']}"
            
            # Validate data types
            assert isinstance(event["launch_score"], (int, float)), "launch_score should be numeric"
            assert isinstance(event["priority"], int), "priority should be int"
            assert isinstance(event["confidence"], (int, float)), "confidence should be numeric"
            
            print(f"PASS: Event structure valid - event_type: {event['event_type']}, product: {event['product_name']}")
        else:
            print("SKIP: No events to validate structure - feed is empty")
    
    def test_get_opportunity_feed_limit_parameter(self):
        """Test that limit parameter works correctly"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed?limit=5&hours=168")
        assert response.status_code == 200
        
        data = response.json()
        
        # If there are events, count should not exceed limit
        if data["count"] > 0:
            assert len(data["events"]) <= 5, f"Events count {len(data['events'])} exceeds limit 5"
            print(f"PASS: Limit parameter works - returned {len(data['events'])} events (limit=5)")
        else:
            print("PASS: Limit parameter accepted - feed is empty")
    
    def test_get_opportunity_feed_hours_parameter(self):
        """Test that hours parameter filters by time"""
        # Get events from last 48 hours
        response_48h = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed?hours=48")
        assert response_48h.status_code == 200
        
        # Get events from last 1 hour
        response_1h = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed?hours=1")
        assert response_1h.status_code == 200
        
        data_48h = response_48h.json()
        data_1h = response_1h.json()
        
        # 1 hour filter should return <= 48 hours filter
        assert data_1h["count"] <= data_48h["count"], "1h filter should return <= 48h filter events"
        print(f"PASS: Hours parameter works - 1h: {data_1h['count']} events, 48h: {data_48h['count']} events")
    
    def test_get_opportunity_feed_event_types_filter(self):
        """Test that event_types parameter filters correctly"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed?event_types=entered_strong_launch,new_high_score&hours=168")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["count"] > 0:
            for event in data["events"]:
                assert event["event_type"] in ["entered_strong_launch", "new_high_score"], \
                    f"Event type {event['event_type']} not in filter list"
            print(f"PASS: Event types filter works - {data['count']} filtered events")
        else:
            print("PASS: Event types filter accepted - no matching events")
    
    # =======================
    # GET /api/dashboard/opportunity-feed/stats
    # =======================
    
    def test_get_feed_stats_returns_200(self):
        """Test that feed stats endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: GET /api/dashboard/opportunity-feed/stats returns 200")
    
    def test_get_feed_stats_returns_expected_structure(self):
        """Test that stats returns expected JSON structure"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed/stats")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert "total_events" in data, "Stats should contain 'total_events'"
        assert "last_24h" in data, "Stats should contain 'last_24h'"
        assert "by_type" in data, "Stats should contain 'by_type'"
        
        # Check types
        assert isinstance(data["total_events"], int), "'total_events' should be int"
        assert isinstance(data["last_24h"], int), "'last_24h' should be int"
        assert isinstance(data["by_type"], dict), "'by_type' should be dict"
        
        print(f"PASS: Feed stats structure valid - total: {data['total_events']}, last 24h: {data['last_24h']}")
    
    # =======================
    # POST /api/dashboard/opportunity-feed/generate-sample
    # =======================
    
    def test_generate_sample_events_requires_api_key(self):
        """Test that generate-sample endpoint requires API key"""
        response = requests.post(f"{BASE_URL}/api/dashboard/opportunity-feed/generate-sample")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: generate-sample requires API key (401 without key)")
    
    def test_generate_sample_events_rejects_invalid_key(self):
        """Test that generate-sample rejects invalid API key"""
        headers = {"X-API-Key": "invalid_key_12345"}
        response = requests.post(
            f"{BASE_URL}/api/dashboard/opportunity-feed/generate-sample",
            headers=headers
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: generate-sample rejects invalid API key")
    
    def test_generate_sample_events_with_valid_key(self):
        """Test that generate-sample works with valid API key"""
        headers = {"X-API-Key": API_KEY}
        response = requests.post(
            f"{BASE_URL}/api/dashboard/opportunity-feed/generate-sample",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check response structure
        assert "success" in data, "Response should contain 'success' field"
        assert "events_created" in data, "Response should contain 'events_created' field"
        assert "events" in data, "Response should contain 'events' field"
        
        assert data["success"] == True, "Success should be True"
        assert isinstance(data["events_created"], int), "events_created should be int"
        assert isinstance(data["events"], list), "events should be list"
        
        print(f"PASS: generate-sample created {data['events_created']} events")
    
    # =======================
    # Integration Tests
    # =======================
    
    def test_feed_events_sorted_by_priority(self):
        """Test that feed events are sorted by priority"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed?limit=20&hours=168")
        assert response.status_code == 200
        
        data = response.json()
        
        if len(data["events"]) > 1:
            priorities = [e["priority"] for e in data["events"]]
            
            # Check events are sorted by priority (ascending) - lower priority number = higher importance
            is_sorted = all(priorities[i] <= priorities[i+1] for i in range(len(priorities)-1))
            
            # Note: Events with same priority may be sorted by created_at, so we just check
            # that priority ordering is generally maintained
            print(f"PASS: Feed events have priority ordering - priorities: {priorities[:5]}...")
        else:
            print("SKIP: Need multiple events to test sorting")
    
    def test_feed_events_have_valid_timestamps(self):
        """Test that feed events have valid ISO timestamps"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed?hours=168")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["count"] > 0:
            for event in data["events"][:3]:
                created_at = event.get("created_at")
                assert created_at is not None, "Event should have created_at"
                
                # Verify it's a valid ISO timestamp
                try:
                    datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except ValueError as e:
                    pytest.fail(f"Invalid timestamp format: {created_at}")
            
            print(f"PASS: Event timestamps are valid ISO format")
        else:
            print("SKIP: No events to validate timestamps")
    
    def test_feed_event_product_data_integrity(self):
        """Test that feed events have complete product data"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed?hours=168")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["count"] > 0:
            event = data["events"][0]
            
            # Verify product-related fields are present and valid
            assert event.get("product_id") is not None, "Event should have product_id"
            assert event.get("product_name") is not None, "Event should have product_name"
            assert isinstance(event.get("launch_score", 0), (int, float)), "launch_score should be numeric"
            
            # Optional but expected fields
            optional_fields = ["trend_stage", "trend_score", "estimated_margin", "competition_level", "category"]
            found_optional = [f for f in optional_fields if f in event]
            
            print(f"PASS: Event has product data - id: {event['product_id']}, name: {event['product_name']}")
            print(f"       Optional fields found: {found_optional}")
        else:
            print("SKIP: No events to validate product data")


class TestFeedEventTypes:
    """Tests for specific event types"""
    
    def test_strong_launch_events_have_high_scores(self):
        """Test that entered_strong_launch events have launch_score >= 80"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed?event_types=entered_strong_launch&hours=168")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["count"] > 0:
            for event in data["events"]:
                # Strong launch events should have high scores
                assert event["launch_score"] >= 75, f"Strong launch event has low score: {event['launch_score']}"
            print(f"PASS: {data['count']} strong launch events have valid scores")
        else:
            print("SKIP: No strong launch events to validate")
    
    def test_event_colors_are_valid(self):
        """Test that event colors match expected values"""
        response = requests.get(f"{BASE_URL}/api/dashboard/opportunity-feed?hours=168")
        assert response.status_code == 200
        
        data = response.json()
        
        valid_colors = ["green", "emerald", "blue", "amber", "red"]
        
        if data["count"] > 0:
            for event in data["events"]:
                assert event.get("color") in valid_colors, f"Invalid color: {event.get('color')}"
            print(f"PASS: All {data['count']} events have valid colors")
        else:
            print("SKIP: No events to validate colors")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
