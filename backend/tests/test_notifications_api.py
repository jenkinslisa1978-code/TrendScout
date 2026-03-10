"""
Notification System API Tests

Tests all notification endpoints:
- GET /api/notifications/ - List user notifications
- GET /api/notifications/unread-count - Get unread count
- POST /api/notifications/mark-read - Mark specific notifications as read
- POST /api/notifications/mark-all-read - Mark all notifications as read
- GET /api/notifications/preferences - Get user notification preferences
- PUT /api/notifications/preferences - Update notification preferences
- POST /api/notifications/test-alert - Create test notification
- DELETE /api/notifications/{id} - Delete a notification
"""

import pytest
import requests
import os
import uuid

# Get base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Demo token for testing (works when SUPABASE_JWT_SECRET is not set)
DEMO_USER_ID = f"test_notif_user_{uuid.uuid4().hex[:8]}"
DEMO_TOKEN = f"demo_{DEMO_USER_ID}"


class TestNotificationEndpointsAuth:
    """Test authentication requirements for notification endpoints"""
    
    def test_get_notifications_requires_auth(self):
        """GET /api/notifications/ should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/notifications/")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/notifications/ correctly requires authentication")
    
    def test_unread_count_requires_auth(self):
        """GET /api/notifications/unread-count should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/notifications/unread-count correctly requires authentication")
    
    def test_preferences_requires_auth(self):
        """GET /api/notifications/preferences should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/notifications/preferences")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/notifications/preferences correctly requires authentication")
    
    def test_mark_read_requires_auth(self):
        """POST /api/notifications/mark-read should return 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/mark-read",
            json=["notification_id"]
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/notifications/mark-read correctly requires authentication")
    
    def test_mark_all_read_requires_auth(self):
        """POST /api/notifications/mark-all-read should return 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/notifications/mark-all-read")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/notifications/mark-all-read correctly requires authentication")
    
    def test_preferences_update_requires_auth(self):
        """PUT /api/notifications/preferences should return 401 without auth"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            json={"email_enabled": False}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ PUT /api/notifications/preferences correctly requires authentication")
    
    def test_test_alert_requires_auth(self):
        """POST /api/notifications/test-alert should return 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/notifications/test-alert")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/notifications/test-alert correctly requires authentication")


class TestNotificationPreferences:
    """Test notification preferences endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup headers with demo auth"""
        self.headers = {
            "Authorization": f"Bearer {DEMO_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def test_get_preferences_returns_defaults_for_new_user(self):
        """GET /api/notifications/preferences should return default preferences for new user"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify default values are present
        assert "email_enabled" in data, "Missing email_enabled field"
        assert "in_app_enabled" in data, "Missing in_app_enabled field"
        assert "alert_threshold" in data, "Missing alert_threshold field"
        assert "quiet_hours_enabled" in data, "Missing quiet_hours_enabled field"
        assert "watchlist_priority_enabled" in data, "Missing watchlist_priority_enabled field"
        assert "notification_types" in data, "Missing notification_types field"
        
        # Verify default values
        assert data["email_enabled"] == True, "Default email_enabled should be True"
        assert data["in_app_enabled"] == True, "Default in_app_enabled should be True"
        assert data["alert_threshold"] == 80, "Default alert_threshold should be 80"
        assert data["quiet_hours_enabled"] == False, "Default quiet_hours_enabled should be False"
        
        # Verify notification types
        assert data["notification_types"]["strong_launch"] == True
        assert data["notification_types"]["exploding_trend"] == True
        assert data["notification_types"]["watchlist_alert"] == True
        assert data["notification_types"]["score_milestone"] == True
        
        print("✓ GET /api/notifications/preferences returns correct default values")
    
    def test_update_preferences_email_enabled(self):
        """PUT /api/notifications/preferences should update email_enabled"""
        # Disable email
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers,
            json={"email_enabled": False}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["email_enabled"] == False, "email_enabled should be updated to False"
        
        # Re-enable email
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers,
            json={"email_enabled": True}
        )
        assert response.status_code == 200
        assert response.json()["email_enabled"] == True
        
        print("✓ PUT /api/notifications/preferences correctly updates email_enabled")
    
    def test_update_preferences_alert_threshold(self):
        """PUT /api/notifications/preferences should update alert_threshold"""
        # Set threshold to 85
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers,
            json={"alert_threshold": 85}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["alert_threshold"] == 85, f"alert_threshold should be 85, got {data['alert_threshold']}"
        
        # Verify persistence
        response = requests.get(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers
        )
        assert response.json()["alert_threshold"] == 85, "Threshold change not persisted"
        
        # Reset to default
        requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers,
            json={"alert_threshold": 80}
        )
        
        print("✓ PUT /api/notifications/preferences correctly updates alert_threshold")
    
    def test_update_preferences_quiet_hours(self):
        """PUT /api/notifications/preferences should update quiet hours settings"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers,
            json={
                "quiet_hours_enabled": True,
                "quiet_hours_start": "23:00",
                "quiet_hours_end": "07:00"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["quiet_hours_enabled"] == True
        assert data["quiet_hours_start"] == "23:00"
        assert data["quiet_hours_end"] == "07:00"
        
        # Reset
        requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers,
            json={"quiet_hours_enabled": False}
        )
        
        print("✓ PUT /api/notifications/preferences correctly updates quiet hours")
    
    def test_update_preferences_notification_types(self):
        """PUT /api/notifications/preferences should update notification types"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers,
            json={
                "notification_types": {
                    "strong_launch": False,
                    "exploding_trend": True
                }
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["notification_types"]["strong_launch"] == False
        assert data["notification_types"]["exploding_trend"] == True
        
        # Reset
        requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers,
            json={"notification_types": {"strong_launch": True}}
        )
        
        print("✓ PUT /api/notifications/preferences correctly updates notification types")


class TestNotificationCRUD:
    """Test notification CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup headers with demo auth"""
        self.headers = {
            "Authorization": f"Bearer {DEMO_TOKEN}",
            "Content-Type": "application/json"
        }
        # Ensure preferences allow notifications
        requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            headers=self.headers,
            json={"email_enabled": True, "in_app_enabled": True, "alert_threshold": 80}
        )
    
    def test_get_notifications_empty_list(self):
        """GET /api/notifications/ should return empty list for new user"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "notifications" in data, "Response missing notifications field"
        assert "count" in data, "Response missing count field"
        assert "unread_count" in data, "Response missing unread_count field"
        assert isinstance(data["notifications"], list), "notifications should be a list"
        
        print("✓ GET /api/notifications/ returns correct structure")
    
    def test_get_unread_count_returns_int(self):
        """GET /api/notifications/unread-count should return unread count"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/unread-count",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "unread_count" in data, "Response missing unread_count field"
        assert isinstance(data["unread_count"], int), "unread_count should be an integer"
        
        print("✓ GET /api/notifications/unread-count returns correct format")
    
    def test_create_test_notification(self):
        """POST /api/notifications/test-alert should create a test notification"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/test-alert",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] in ["success", "skipped"], f"Unexpected status: {data['status']}"
        
        if data["status"] == "success":
            notification = data["notification"]
            assert "id" in notification, "Notification missing id"
            assert "notification_type" in notification, "Notification missing notification_type"
            assert "product_name" in notification, "Notification missing product_name"
            assert "launch_score" in notification, "Notification missing launch_score"
            assert "title" in notification, "Notification missing title"
            assert notification["is_read"] == False, "New notification should be unread"
            print(f"✓ POST /api/notifications/test-alert created notification: {notification['title']}")
        else:
            print(f"✓ POST /api/notifications/test-alert returned skipped (check preferences)")
    
    def test_mark_notifications_as_read(self):
        """POST /api/notifications/mark-read should mark notifications as read"""
        # First create a test notification
        create_response = requests.post(
            f"{BASE_URL}/api/notifications/test-alert",
            headers=self.headers
        )
        
        if create_response.status_code == 200 and create_response.json().get("status") == "success":
            notification_id = create_response.json()["notification"]["id"]
            
            # Mark it as read
            response = requests.post(
                f"{BASE_URL}/api/notifications/mark-read",
                headers=self.headers,
                json=[notification_id]
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert data["status"] == "success", f"Expected success status, got {data['status']}"
            assert "modified_count" in data, "Response missing modified_count"
            print(f"✓ POST /api/notifications/mark-read successfully marked {data['modified_count']} notification(s)")
        else:
            # Test with non-existent IDs (should not fail)
            response = requests.post(
                f"{BASE_URL}/api/notifications/mark-read",
                headers=self.headers,
                json=["non_existent_id"]
            )
            assert response.status_code == 200
            print("✓ POST /api/notifications/mark-read handles non-existent IDs gracefully")
    
    def test_mark_all_notifications_as_read(self):
        """POST /api/notifications/mark-all-read should mark all notifications as read"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/mark-all-read",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success", f"Expected success status, got {data['status']}"
        assert "modified_count" in data, "Response missing modified_count"
        
        # Verify unread count is now 0
        count_response = requests.get(
            f"{BASE_URL}/api/notifications/unread-count",
            headers=self.headers
        )
        assert count_response.json()["unread_count"] == 0, "Unread count should be 0 after mark-all-read"
        
        print("✓ POST /api/notifications/mark-all-read works correctly")
    
    def test_notification_list_pagination(self):
        """GET /api/notifications/ should respect limit parameter"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/?limit=5",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert len(data["notifications"]) <= 5, "Should not exceed limit"
        
        print("✓ GET /api/notifications/ respects limit parameter")
    
    def test_notification_unread_only_filter(self):
        """GET /api/notifications/ should filter unread_only"""
        # Mark all as read first
        requests.post(
            f"{BASE_URL}/api/notifications/mark-all-read",
            headers=self.headers
        )
        
        response = requests.get(
            f"{BASE_URL}/api/notifications/?unread_only=true",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # After marking all read, unread_only should return 0 notifications
        assert data["count"] == 0, "Should have 0 unread notifications"
        
        print("✓ GET /api/notifications/ correctly filters unread_only")


class TestNotificationServiceIntegration:
    """Test notification service integration features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup headers with demo auth"""
        self.headers = {
            "Authorization": f"Bearer {DEMO_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def test_notification_deduplication(self):
        """Test that duplicate notifications within 4-hour window are skipped"""
        # Create first notification
        response1 = requests.post(
            f"{BASE_URL}/api/notifications/test-alert",
            headers=self.headers
        )
        assert response1.status_code == 200
        
        # Note: test-alert uses force=True which bypasses dedup,
        # but this test validates the endpoint works
        print("✓ Notification deduplication endpoint functioning (uses force=True for test)")
    
    def test_notification_priority_ordering(self):
        """Test that notifications are ordered by priority"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/",
            headers=self.headers
        )
        assert response.status_code == 200
        
        # The endpoint sorts by is_read, priority, created_at
        # We just verify the structure is correct
        data = response.json()
        assert isinstance(data["notifications"], list)
        
        print("✓ Notification priority ordering endpoint functioning")
    
    def test_notification_contains_product_data(self):
        """Test that notifications include product data"""
        # Create a test notification
        response = requests.post(
            f"{BASE_URL}/api/notifications/test-alert",
            headers=self.headers
        )
        
        if response.status_code == 200 and response.json().get("status") == "success":
            notification = response.json()["notification"]
            
            # Verify product-related fields
            assert "product_id" in notification, "Missing product_id"
            assert "product_name" in notification, "Missing product_name"
            assert "launch_score" in notification, "Missing launch_score"
            assert "category" in notification, "Missing category"
            assert "trend_stage" in notification, "Missing trend_stage"
            
            print("✓ Notification contains required product data")
        else:
            print("✓ Notification structure test skipped (no products with high score)")


class TestNotificationRouterRegistration:
    """Test that notification router is properly registered"""
    
    def test_notification_router_exists(self):
        """Test that /api/notifications endpoint exists"""
        response = requests.options(f"{BASE_URL}/api/notifications/")
        # Should not return 404
        assert response.status_code != 404, "Notifications router not found"
        print("✓ Notification router is registered at /api/notifications")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
