"""
Product Alerts API Tests
Tests for the Product Alert Email feature:
- GET /api/product-alerts/subscriptions - list user's alert subscriptions (requires auth + paid plan)
- POST /api/product-alerts/subscriptions - create new subscription with categories and min_score
- PUT /api/product-alerts/subscriptions/{id}/toggle - toggle active/inactive
- PUT /api/product-alerts/subscriptions/{id} - update subscription
- DELETE /api/product-alerts/subscriptions/{id} - delete subscription
- GET /api/product-alerts/history - get alert history
- GET /api/product-alerts/categories - get available categories
"""
import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Module-level token cache to avoid rate limiting
_auth_token = None
_token_expiry = 0

def get_auth_token():
    """Get auth token with caching to avoid rate limits"""
    global _auth_token, _token_expiry
    
    current_time = time.time()
    if _auth_token and current_time < _token_expiry:
        return _auth_token
    
    # Login to get fresh token
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "reviewer@trendscout.click",
        "password": "ShopifyReview2026!"
    })
    
    if response.status_code == 200:
        data = response.json()
        _auth_token = data.get("token") or data.get("access_token")
        _token_expiry = current_time + 600  # Cache for 10 minutes
        return _auth_token
    elif response.status_code == 429:
        # Rate limited - wait and retry
        retry_after = response.json().get("error", {}).get("retry_after", 60)
        time.sleep(retry_after + 1)
        return get_auth_token()
    else:
        pytest.skip(f"Could not authenticate: {response.status_code} - {response.text}")


class TestProductAlertsAPI:
    """Product Alerts API endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.token = get_auth_token()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.created_subscription_ids = []
        yield
        
        # Cleanup: delete test subscriptions
        for sub_id in self.created_subscription_ids:
            try:
                requests.delete(
                    f"{BASE_URL}/api/product-alerts/subscriptions/{sub_id}",
                    headers=self.headers
                )
            except:
                pass
    
    # ── Categories endpoint ──
    
    def test_get_categories_requires_auth(self):
        """GET /api/product-alerts/categories requires authentication"""
        response = requests.get(f"{BASE_URL}/api/product-alerts/categories")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Categories endpoint requires auth")
    
    def test_get_categories_with_auth(self):
        """GET /api/product-alerts/categories returns available categories"""
        response = requests.get(f"{BASE_URL}/api/product-alerts/categories", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)
        assert len(data["categories"]) > 0, "Should have at least one category"
        print(f"PASS: Got {len(data['categories'])} categories: {data['categories'][:5]}...")
    
    # ── Subscriptions CRUD ──
    
    def test_list_subscriptions_requires_auth(self):
        """GET /api/product-alerts/subscriptions requires authentication"""
        response = requests.get(f"{BASE_URL}/api/product-alerts/subscriptions")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Subscriptions list requires auth")
    
    def test_list_subscriptions_with_auth(self):
        """GET /api/product-alerts/subscriptions returns user's subscriptions"""
        response = requests.get(f"{BASE_URL}/api/product-alerts/subscriptions", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "subscriptions" in data
        assert isinstance(data["subscriptions"], list)
        print(f"PASS: Found {len(data['subscriptions'])} existing subscriptions")
    
    def test_create_subscription_requires_auth(self):
        """POST /api/product-alerts/subscriptions requires authentication"""
        response = requests.post(f"{BASE_URL}/api/product-alerts/subscriptions", json={
            "categories": ["Beauty"],
            "min_score": 50
        })
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Create subscription requires auth")
    
    def test_create_subscription_success(self):
        """POST /api/product-alerts/subscriptions creates a new subscription"""
        payload = {
            "categories": ["TEST_Beauty", "TEST_Electronics"],
            "min_score": 60,
            "label": "TEST_Alert_Subscription"
        }
        response = requests.post(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers,
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "subscription" in data
        sub = data["subscription"]
        assert sub["categories"] == ["TEST_Beauty", "TEST_Electronics"]
        assert sub["min_score"] == 60
        assert sub["label"] == "TEST_Alert_Subscription"
        assert sub["active"] == True
        assert "id" in sub
        
        self.created_subscription_ids.append(sub["id"])
        print(f"PASS: Created subscription {sub['id']}")
    
    def test_create_subscription_validates_categories(self):
        """POST /api/product-alerts/subscriptions requires at least one category"""
        response = requests.post(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers,
            json={"categories": [], "min_score": 50}
        )
        assert response.status_code == 422, f"Expected 422 for empty categories, got {response.status_code}"
        print("PASS: Empty categories validation works")
    
    def test_create_subscription_validates_min_score_range(self):
        """POST /api/product-alerts/subscriptions validates min_score 1-100"""
        # Test score > 100
        response = requests.post(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers,
            json={"categories": ["TEST_Category"], "min_score": 150}
        )
        assert response.status_code == 422, f"Expected 422 for score > 100, got {response.status_code}"
        
        # Test score < 1
        response = requests.post(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers,
            json={"categories": ["TEST_Category"], "min_score": 0}
        )
        assert response.status_code == 422, f"Expected 422 for score < 1, got {response.status_code}"
        print("PASS: Score range validation works")
    
    def test_toggle_subscription(self):
        """PUT /api/product-alerts/subscriptions/{id}/toggle toggles active state"""
        # First create a subscription
        create_response = requests.post(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers,
            json={"categories": ["TEST_Toggle"], "min_score": 50}
        )
        assert create_response.status_code == 200
        sub_id = create_response.json()["subscription"]["id"]
        self.created_subscription_ids.append(sub_id)
        
        # Toggle to inactive
        toggle_response = requests.put(
            f"{BASE_URL}/api/product-alerts/subscriptions/{sub_id}/toggle",
            headers=self.headers
        )
        assert toggle_response.status_code == 200, f"Expected 200, got {toggle_response.status_code}: {toggle_response.text}"
        data = toggle_response.json()
        assert "active" in data
        assert data["active"] == False
        
        # Toggle back to active
        toggle_response2 = requests.put(
            f"{BASE_URL}/api/product-alerts/subscriptions/{sub_id}/toggle",
            headers=self.headers
        )
        assert toggle_response2.status_code == 200
        assert toggle_response2.json()["active"] == True
        print(f"PASS: Toggle works for subscription {sub_id}")
    
    def test_toggle_nonexistent_subscription(self):
        """PUT /api/product-alerts/subscriptions/{id}/toggle returns 404 for invalid ID"""
        response = requests.put(
            f"{BASE_URL}/api/product-alerts/subscriptions/nonexistent-id/toggle",
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Toggle returns 404 for nonexistent subscription")
    
    def test_update_subscription(self):
        """PUT /api/product-alerts/subscriptions/{id} updates subscription fields"""
        # First create a subscription
        create_response = requests.post(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers,
            json={"categories": ["TEST_Update"], "min_score": 50, "label": "Original Label"}
        )
        assert create_response.status_code == 200
        sub_id = create_response.json()["subscription"]["id"]
        self.created_subscription_ids.append(sub_id)
        
        # Update the subscription
        update_response = requests.put(
            f"{BASE_URL}/api/product-alerts/subscriptions/{sub_id}",
            headers=self.headers,
            json={"categories": ["TEST_Updated", "TEST_NewCategory"], "min_score": 75, "label": "Updated Label"}
        )
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}: {update_response.text}"
        
        updated = update_response.json()["subscription"]
        assert updated["categories"] == ["TEST_Updated", "TEST_NewCategory"]
        assert updated["min_score"] == 75
        assert updated["label"] == "Updated Label"
        print(f"PASS: Update works for subscription {sub_id}")
    
    def test_update_nonexistent_subscription(self):
        """PUT /api/product-alerts/subscriptions/{id} returns 404 for invalid ID"""
        response = requests.put(
            f"{BASE_URL}/api/product-alerts/subscriptions/nonexistent-id",
            headers=self.headers,
            json={"min_score": 60}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Update returns 404 for nonexistent subscription")
    
    def test_delete_subscription(self):
        """DELETE /api/product-alerts/subscriptions/{id} deletes a subscription"""
        # First create a subscription
        create_response = requests.post(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers,
            json={"categories": ["TEST_Delete"], "min_score": 50}
        )
        assert create_response.status_code == 200
        sub_id = create_response.json()["subscription"]["id"]
        
        # Delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/product-alerts/subscriptions/{sub_id}",
            headers=self.headers
        )
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        assert delete_response.json()["deleted"] == True
        
        # Verify it's gone
        toggle_response = requests.put(
            f"{BASE_URL}/api/product-alerts/subscriptions/{sub_id}/toggle",
            headers=self.headers
        )
        assert toggle_response.status_code == 404
        print(f"PASS: Delete works for subscription {sub_id}")
    
    def test_delete_nonexistent_subscription(self):
        """DELETE /api/product-alerts/subscriptions/{id} returns 404 for invalid ID"""
        response = requests.delete(
            f"{BASE_URL}/api/product-alerts/subscriptions/nonexistent-id",
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Delete returns 404 for nonexistent subscription")
    
    # ── Alert History ──
    
    def test_get_history_requires_auth(self):
        """GET /api/product-alerts/history requires authentication"""
        response = requests.get(f"{BASE_URL}/api/product-alerts/history")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: History endpoint requires auth")
    
    def test_get_history_with_auth(self):
        """GET /api/product-alerts/history returns alert history"""
        response = requests.get(f"{BASE_URL}/api/product-alerts/history", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "alerts" in data
        assert isinstance(data["alerts"], list)
        print(f"PASS: Found {len(data['alerts'])} alerts in history")
    
    def test_get_history_with_limit(self):
        """GET /api/product-alerts/history?limit=5 respects limit parameter"""
        response = requests.get(f"{BASE_URL}/api/product-alerts/history?limit=5", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) <= 5
        print("PASS: History limit parameter works")


class TestProductAlertsPlanGating:
    """Tests for plan gating - free users should get 403"""
    
    def test_unauthenticated_blocked(self):
        """Unauthenticated users should get 401 on subscriptions endpoint"""
        response = requests.get(f"{BASE_URL}/api/product-alerts/subscriptions")
        assert response.status_code in [401, 403], f"Expected 401/403 for unauthenticated, got {response.status_code}"
        print("PASS: Unauthenticated users correctly blocked")


class TestProductAlertsDataPersistence:
    """Tests for data persistence - Create → GET verification pattern"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.token = get_auth_token()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.created_subscription_ids = []
        yield
        
        # Cleanup
        for sub_id in self.created_subscription_ids:
            try:
                requests.delete(
                    f"{BASE_URL}/api/product-alerts/subscriptions/{sub_id}",
                    headers=self.headers
                )
            except:
                pass
    
    def test_create_and_verify_persistence(self):
        """Create subscription and verify it appears in list"""
        unique_label = f"TEST_Persistence_{uuid.uuid4().hex[:8]}"
        
        # Create
        create_response = requests.post(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers,
            json={"categories": ["TEST_Persist"], "min_score": 55, "label": unique_label}
        )
        assert create_response.status_code == 200
        sub_id = create_response.json()["subscription"]["id"]
        self.created_subscription_ids.append(sub_id)
        
        # Verify in list
        list_response = requests.get(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers
        )
        assert list_response.status_code == 200
        subs = list_response.json()["subscriptions"]
        
        found = next((s for s in subs if s["id"] == sub_id), None)
        assert found is not None, f"Created subscription {sub_id} not found in list"
        assert found["label"] == unique_label
        assert found["min_score"] == 55
        print(f"PASS: Persistence verified for subscription {sub_id}")
    
    def test_update_and_verify_persistence(self):
        """Update subscription and verify changes persist"""
        # Create
        create_response = requests.post(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers,
            json={"categories": ["TEST_UpdatePersist"], "min_score": 50, "label": "Before Update"}
        )
        assert create_response.status_code == 200
        sub_id = create_response.json()["subscription"]["id"]
        self.created_subscription_ids.append(sub_id)
        
        # Update
        update_response = requests.put(
            f"{BASE_URL}/api/product-alerts/subscriptions/{sub_id}",
            headers=self.headers,
            json={"label": "After Update", "min_score": 80}
        )
        assert update_response.status_code == 200
        
        # Verify in list
        list_response = requests.get(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers
        )
        subs = list_response.json()["subscriptions"]
        found = next((s for s in subs if s["id"] == sub_id), None)
        
        assert found is not None
        assert found["label"] == "After Update"
        assert found["min_score"] == 80
        print(f"PASS: Update persistence verified for subscription {sub_id}")
    
    def test_delete_and_verify_removal(self):
        """Delete subscription and verify it's removed from list"""
        # Create
        create_response = requests.post(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers,
            json={"categories": ["TEST_DeletePersist"], "min_score": 50}
        )
        assert create_response.status_code == 200
        sub_id = create_response.json()["subscription"]["id"]
        
        # Delete
        delete_response = requests.delete(
            f"{BASE_URL}/api/product-alerts/subscriptions/{sub_id}",
            headers=self.headers
        )
        assert delete_response.status_code == 200
        
        # Verify not in list
        list_response = requests.get(
            f"{BASE_URL}/api/product-alerts/subscriptions",
            headers=self.headers
        )
        subs = list_response.json()["subscriptions"]
        found = next((s for s in subs if s["id"] == sub_id), None)
        
        assert found is None, f"Deleted subscription {sub_id} still found in list"
        print(f"PASS: Delete persistence verified for subscription {sub_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
