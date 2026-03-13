"""
Backend tests for TrendScout Workspace and Email Subscription features.

Tests:
1. Workspace endpoints - CRUD for saved products with notes and status
2. Email subscription status endpoint

Product IDs for testing:
- '5d241fc9-383b-4dcc-b406-ba40590ed6a3' (Portable Neck Fan, already saved)
- 'f6d631f2-00da-4ea5-9ca2-0ce2469856b0' (Magnetic Phone Mount, already saved)
- 'db5b1d77-84b0-4e74-afff-2b0dcd21e686' (Sunset Projection Lamp, not saved)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "jenkinslisa1978@gmail.com"
TEST_PASSWORD = "test123456"

# Test product IDs
SAVED_PRODUCT_1 = "5d241fc9-383b-4dcc-b406-ba40590ed6a3"  # Portable Neck Fan
SAVED_PRODUCT_2 = "f6d631f2-00da-4ea5-9ca2-0ce2469856b0"  # Magnetic Phone Mount
UNSAVED_PRODUCT = "db5b1d77-84b0-4e74-afff-2b0dcd21e686"  # Sunset Projection Lamp


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data.get("token")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Create headers with auth token."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestWorkspaceListProducts:
    """Test GET /api/workspace/products - List saved products"""
    
    def test_list_workspace_products_returns_200(self, auth_headers):
        """GET /api/workspace/products should return 200 with saved products list."""
        response = requests.get(f"{BASE_URL}/api/workspace/products", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "items" in data, "Response should have 'items' field"
        assert "count" in data, "Response should have 'count' field"
        print(f"✓ GET /api/workspace/products returned {data['count']} items")
    
    def test_workspace_products_have_required_fields(self, auth_headers):
        """Workspace items should have required fields (product_id, launch_status, note, product)."""
        response = requests.get(f"{BASE_URL}/api/workspace/products", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        if data["count"] > 0:
            item = data["items"][0]
            required_fields = ["id", "product_id", "launch_status", "note", "saved_at", "product"]
            for field in required_fields:
                assert field in item, f"Missing required field: {field}"
            print(f"✓ Workspace items have all required fields: {required_fields}")
        else:
            pytest.skip("No workspace items to validate fields")
    
    def test_workspace_products_enriched_with_product_data(self, auth_headers):
        """Workspace items should include enriched product data."""
        response = requests.get(f"{BASE_URL}/api/workspace/products", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        if data["count"] > 0:
            item = data["items"][0]
            product = item.get("product", {})
            if product:
                assert "product_name" in product or "id" in product, "Product data should include name or id"
                print(f"✓ Workspace items enriched with product data: {list(product.keys())[:5]}...")
        else:
            pytest.skip("No workspace items to validate product data")
    
    def test_workspace_products_filter_by_status(self, auth_headers):
        """GET /api/workspace/products?status=researching should filter by status."""
        response = requests.get(f"{BASE_URL}/api/workspace/products?status=researching", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        for item in data["items"]:
            assert item["launch_status"] == "researching", f"Expected status 'researching', got '{item['launch_status']}'"
        print(f"✓ Status filter works: {data['count']} items with status 'researching'")


class TestWorkspaceSaveProduct:
    """Test POST /api/workspace/products - Save a product"""
    
    def test_save_product_success(self, auth_headers):
        """POST /api/workspace/products should save a new product."""
        # First remove if exists to test fresh save
        requests.delete(f"{BASE_URL}/api/workspace/products/{UNSAVED_PRODUCT}", headers=auth_headers)
        
        response = requests.post(
            f"{BASE_URL}/api/workspace/products",
            json={"product_id": UNSAVED_PRODUCT},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data or "message" in data, "Response should have 'id' or 'message'"
        print(f"✓ POST /api/workspace/products saved product successfully")
    
    def test_save_duplicate_product_returns_already_saved(self, auth_headers):
        """POST /api/workspace/products with duplicate should return 'Already saved'."""
        # Ensure product is saved first
        requests.post(
            f"{BASE_URL}/api/workspace/products",
            json={"product_id": SAVED_PRODUCT_1},
            headers=auth_headers
        )
        
        # Try to save again
        response = requests.post(
            f"{BASE_URL}/api/workspace/products",
            json={"product_id": SAVED_PRODUCT_1},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "Already saved" in data.get("message", ""), f"Expected 'Already saved' message, got: {data}"
        print(f"✓ Duplicate save returns 'Already saved' message")
    
    def test_save_product_without_id_returns_400(self, auth_headers):
        """POST /api/workspace/products without product_id should return 400."""
        response = requests.post(
            f"{BASE_URL}/api/workspace/products",
            json={},
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"✓ Missing product_id returns 400")


class TestWorkspaceDeleteProduct:
    """Test DELETE /api/workspace/products/{product_id} - Remove a product"""
    
    def test_delete_product_success(self, auth_headers):
        """DELETE /api/workspace/products/{product_id} should remove saved product."""
        # First save a product to delete
        requests.post(
            f"{BASE_URL}/api/workspace/products",
            json={"product_id": UNSAVED_PRODUCT},
            headers=auth_headers
        )
        
        response = requests.delete(
            f"{BASE_URL}/api/workspace/products/{UNSAVED_PRODUCT}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "Removed" in data.get("message", ""), f"Expected 'Removed' message"
        print(f"✓ DELETE /api/workspace/products successfully removed product")
    
    def test_delete_nonexistent_product_returns_404(self, auth_headers):
        """DELETE /api/workspace/products/{nonexistent_id} should return 404."""
        response = requests.delete(
            f"{BASE_URL}/api/workspace/products/nonexistent-product-12345",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Delete nonexistent product returns 404")


class TestWorkspaceUpdateNote:
    """Test PUT /api/workspace/products/{product_id}/note - Update note"""
    
    def test_update_note_success(self, auth_headers):
        """PUT /api/workspace/products/{product_id}/note should update the note."""
        new_note = "Test note updated at " + str(__import__('time').time())
        
        response = requests.put(
            f"{BASE_URL}/api/workspace/products/{SAVED_PRODUCT_1}/note",
            json={"note": new_note},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "updated" in data.get("message", "").lower(), f"Expected 'updated' in message"
        print(f"✓ PUT /api/workspace/products/.../note updated successfully")
    
    def test_update_note_verify_persistence(self, auth_headers):
        """Note update should persist and be retrievable via GET."""
        test_note = "Persistence test note 12345"
        
        # Update note
        requests.put(
            f"{BASE_URL}/api/workspace/products/{SAVED_PRODUCT_1}/note",
            json={"note": test_note},
            headers=auth_headers
        )
        
        # Verify via GET
        response = requests.get(f"{BASE_URL}/api/workspace/products", headers=auth_headers)
        data = response.json()
        
        found = False
        for item in data["items"]:
            if item["product_id"] == SAVED_PRODUCT_1:
                assert item["note"] == test_note, f"Expected note '{test_note}', got '{item['note']}'"
                found = True
                break
        
        assert found, f"Product {SAVED_PRODUCT_1} not found in workspace"
        print(f"✓ Note update persisted and verified via GET")
    
    def test_update_note_nonexistent_product_returns_404(self, auth_headers):
        """PUT /api/workspace/products/{nonexistent}/note should return 404."""
        response = requests.put(
            f"{BASE_URL}/api/workspace/products/nonexistent-12345/note",
            json={"note": "test"},
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Update note for nonexistent product returns 404")


class TestWorkspaceUpdateStatus:
    """Test PUT /api/workspace/products/{product_id}/status - Update launch status"""
    
    def test_update_status_researching(self, auth_headers):
        """PUT /api/workspace/products/{product_id}/status to 'researching'."""
        response = requests.put(
            f"{BASE_URL}/api/workspace/products/{SAVED_PRODUCT_1}/status",
            json={"launch_status": "researching"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Status updated to 'researching'")
    
    def test_update_status_testing(self, auth_headers):
        """PUT /api/workspace/products/{product_id}/status to 'testing'."""
        response = requests.put(
            f"{BASE_URL}/api/workspace/products/{SAVED_PRODUCT_2}/status",
            json={"launch_status": "testing"},
            headers=auth_headers
        )
        assert response.status_code == 200
        print(f"✓ Status updated to 'testing'")
    
    def test_update_status_launched(self, auth_headers):
        """PUT /api/workspace/products/{product_id}/status to 'launched'."""
        response = requests.put(
            f"{BASE_URL}/api/workspace/products/{SAVED_PRODUCT_1}/status",
            json={"launch_status": "launched"},
            headers=auth_headers
        )
        assert response.status_code == 200
        print(f"✓ Status updated to 'launched'")
    
    def test_update_status_dropped(self, auth_headers):
        """PUT /api/workspace/products/{product_id}/status to 'dropped'."""
        response = requests.put(
            f"{BASE_URL}/api/workspace/products/{SAVED_PRODUCT_1}/status",
            json={"launch_status": "dropped"},
            headers=auth_headers
        )
        assert response.status_code == 200
        print(f"✓ Status updated to 'dropped'")
    
    def test_update_invalid_status_returns_400(self, auth_headers):
        """PUT /api/workspace/products/{product_id}/status with invalid status should return 400."""
        response = requests.put(
            f"{BASE_URL}/api/workspace/products/{SAVED_PRODUCT_1}/status",
            json={"launch_status": "invalid_status"},
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"✓ Invalid status returns 400")
    
    def test_update_status_verify_persistence(self, auth_headers):
        """Status update should persist and be retrievable."""
        # Set to specific status
        requests.put(
            f"{BASE_URL}/api/workspace/products/{SAVED_PRODUCT_1}/status",
            json={"launch_status": "researching"},
            headers=auth_headers
        )
        
        # Verify via GET
        response = requests.get(f"{BASE_URL}/api/workspace/products", headers=auth_headers)
        data = response.json()
        
        for item in data["items"]:
            if item["product_id"] == SAVED_PRODUCT_1:
                assert item["launch_status"] == "researching", f"Expected 'researching', got '{item['launch_status']}'"
                print(f"✓ Status change persisted and verified")
                return
        
        pytest.fail(f"Product {SAVED_PRODUCT_1} not found in workspace")


class TestWorkspaceCheckProduct:
    """Test GET /api/workspace/products/{product_id}/check - Check if saved"""
    
    def test_check_saved_product_returns_true(self, auth_headers):
        """GET /api/workspace/products/{saved_id}/check should return saved=true."""
        response = requests.get(
            f"{BASE_URL}/api/workspace/products/{SAVED_PRODUCT_1}/check",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["saved"] == True, f"Expected saved=True, got {data['saved']}"
        assert "item" in data, "Response should have 'item' field"
        print(f"✓ Check saved product returns saved=True with item details")
    
    def test_check_unsaved_product_returns_false(self, auth_headers):
        """GET /api/workspace/products/{unsaved_id}/check should return saved=false."""
        # First ensure product is not saved
        requests.delete(f"{BASE_URL}/api/workspace/products/{UNSAVED_PRODUCT}", headers=auth_headers)
        
        response = requests.get(
            f"{BASE_URL}/api/workspace/products/{UNSAVED_PRODUCT}/check",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["saved"] == False, f"Expected saved=False, got {data['saved']}"
        print(f"✓ Check unsaved product returns saved=False")


class TestEmailSubscriptionStatus:
    """Test GET /api/email/subscription-status - Get email preferences"""
    
    def test_get_subscription_status_returns_200(self, auth_headers):
        """GET /api/email/subscription-status should return 200 with preferences."""
        response = requests.get(f"{BASE_URL}/api/email/subscription-status", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "email" in data, "Response should have 'email' field"
        assert "preferences" in data, "Response should have 'preferences' field"
        print(f"✓ GET /api/email/subscription-status returns preferences: {data['preferences']}")
    
    def test_subscription_preferences_have_expected_fields(self, auth_headers):
        """Subscription preferences should have weekly_digest and product_alerts."""
        response = requests.get(f"{BASE_URL}/api/email/subscription-status", headers=auth_headers)
        data = response.json()
        
        prefs = data.get("preferences", {})
        # These are expected fields based on the code
        expected_fields = ["weekly_digest", "product_alerts"]
        for field in expected_fields:
            assert field in prefs, f"Missing expected preference field: {field}"
        print(f"✓ Preferences have expected fields: {list(prefs.keys())}")


class TestAuthRequired:
    """Test that workspace endpoints require authentication"""
    
    def test_list_workspace_requires_auth(self):
        """GET /api/workspace/products without auth should return 401."""
        response = requests.get(f"{BASE_URL}/api/workspace/products")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ List workspace requires authentication")
    
    def test_save_workspace_requires_auth(self):
        """POST /api/workspace/products without auth should return 401."""
        response = requests.post(
            f"{BASE_URL}/api/workspace/products",
            json={"product_id": "test"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Save workspace requires authentication")
    
    def test_email_subscription_requires_auth(self):
        """GET /api/email/subscription-status without auth should return 401."""
        response = requests.get(f"{BASE_URL}/api/email/subscription-status")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Email subscription status requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
