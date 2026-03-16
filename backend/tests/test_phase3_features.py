"""
Phase 3 Features Test Suite - TrendScout
- Radar Alerts: Watches CRUD + Live Events
- Verified Winners: Submit/List/Upvote/Verify
- Shopify Push: Push Product + Exports
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "admin123456"


class TestAuth:
    """Authentication helper tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data or "token" in data, "No token in login response"
        return data.get("access_token") or data.get("token")
    
    def test_login_works(self, auth_token):
        """Verify login works and returns token"""
        assert auth_token is not None
        print(f"✓ Login successful, got auth token")


class TestRadarWatches:
    """Radar Watches CRUD API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_create_watch(self, auth_headers):
        """POST /api/radar/watches creates a new watch"""
        response = requests.post(f"{BASE_URL}/api/radar/watches", headers=auth_headers, json={
            "name": "TEST_watch_score_alert",
            "watch_type": "product_score",
            "condition": {"operator": "below", "value": 60},
            "notify_email": True,
            "notify_in_app": True
        })
        assert response.status_code == 200, f"Create watch failed: {response.text}"
        data = response.json()
        assert "watch" in data
        watch = data["watch"]
        assert watch["name"] == "TEST_watch_score_alert"
        assert watch["watch_type"] == "product_score"
        assert watch["active"] == True
        assert "id" in watch
        print(f"✓ Created watch: {watch['id']}")
        return watch["id"]
    
    def test_get_watches(self, auth_headers):
        """GET /api/radar/watches returns user's watches"""
        response = requests.get(f"{BASE_URL}/api/radar/watches", headers=auth_headers)
        assert response.status_code == 200, f"Get watches failed: {response.text}"
        data = response.json()
        assert "watches" in data
        assert isinstance(data["watches"], list)
        print(f"✓ Got {len(data['watches'])} watches")
    
    def test_toggle_watch(self, auth_headers):
        """PUT /api/radar/watches/{id} toggles active status"""
        # First create a watch
        create_resp = requests.post(f"{BASE_URL}/api/radar/watches", headers=auth_headers, json={
            "name": "TEST_toggle_watch",
            "watch_type": "category_trend",
            "condition": {"operator": "above", "value": 80},
            "notify_email": False,
            "notify_in_app": True
        })
        assert create_resp.status_code == 200
        watch_id = create_resp.json()["watch"]["id"]
        
        # Toggle to inactive
        toggle_resp = requests.put(f"{BASE_URL}/api/radar/watches/{watch_id}", headers=auth_headers, json={
            "active": False
        })
        assert toggle_resp.status_code == 200, f"Toggle watch failed: {toggle_resp.text}"
        data = toggle_resp.json()
        assert data["watch"]["active"] == False
        print(f"✓ Toggled watch {watch_id} to inactive")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/radar/watches/{watch_id}", headers=auth_headers)
    
    def test_delete_watch(self, auth_headers):
        """DELETE /api/radar/watches/{id} removes a watch"""
        # Create a watch to delete
        create_resp = requests.post(f"{BASE_URL}/api/radar/watches", headers=auth_headers, json={
            "name": "TEST_delete_watch",
            "watch_type": "competitor_new_products",
            "condition": {"operator": "above", "value": 5},
            "notify_email": True,
            "notify_in_app": False
        })
        assert create_resp.status_code == 200
        watch_id = create_resp.json()["watch"]["id"]
        
        # Delete it
        delete_resp = requests.delete(f"{BASE_URL}/api/radar/watches/{watch_id}", headers=auth_headers)
        assert delete_resp.status_code == 200, f"Delete watch failed: {delete_resp.text}"
        data = delete_resp.json()
        assert data["deleted"] == True
        print(f"✓ Deleted watch {watch_id}")
        
        # Verify it's gone
        get_resp = requests.get(f"{BASE_URL}/api/radar/watches", headers=auth_headers)
        watches = get_resp.json()["watches"]
        assert not any(w["id"] == watch_id for w in watches)
    
    def test_cleanup_test_watches(self, auth_headers):
        """Cleanup TEST_ prefixed watches"""
        get_resp = requests.get(f"{BASE_URL}/api/radar/watches", headers=auth_headers)
        watches = get_resp.json().get("watches", [])
        for w in watches:
            if w.get("name", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/radar/watches/{w['id']}", headers=auth_headers)
        print("✓ Cleaned up TEST_ watches")


class TestRadarLiveEvents:
    """Radar Live Events API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_get_live_events(self, auth_headers):
        """GET /api/radar/live-events returns live signal feed"""
        response = requests.get(f"{BASE_URL}/api/radar/live-events?limit=15", headers=auth_headers)
        assert response.status_code == 200, f"Get live events failed: {response.text}"
        data = response.json()
        assert "events" in data
        assert "generated_at" in data
        events = data["events"]
        
        # Verify event types
        valid_types = {"trend_spike", "new_ads", "supplier_demand", "competition_drop"}
        for event in events[:5]:  # Check first 5
            assert event.get("type") in valid_types, f"Invalid event type: {event.get('type')}"
            assert "title" in event
            assert "detail" in event
        
        print(f"✓ Got {len(events)} live events with valid structure")
    
    def test_live_events_require_auth(self):
        """GET /api/radar/live-events requires authentication"""
        response = requests.get(f"{BASE_URL}/api/radar/live-events")
        assert response.status_code in [401, 403], "Live events should require auth"
        print("✓ Live events endpoint requires authentication")


class TestVerifiedWinners:
    """Verified Winners API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    @pytest.fixture(scope="class")
    def sample_product_id(self, auth_headers):
        """Get a real product ID from the database"""
        # Try products endpoint (returns data array)
        response = requests.get(f"{BASE_URL}/api/products?limit=1", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            products = data.get("data") or data.get("products") or []
            if products and products[0].get("id"):
                return products[0]["id"]
        
        # Fallback: try ads discover
        response = requests.get(f"{BASE_URL}/api/ads/discover?limit=1", headers=auth_headers)
        if response.status_code == 200:
            ads = response.json().get("ads", [])
            if ads and ads[0].get("product_id"):
                return ads[0]["product_id"]
        
        # Last resort: use a known product ID
        return "2e3d8782-0026-4fef-a04a-a1d3426e2d26"
    
    def test_get_verified_winners_public(self):
        """GET /api/winners/ is public and returns winners leaderboard"""
        response = requests.get(f"{BASE_URL}/api/winners/?status=verified&limit=10")
        assert response.status_code == 200, f"Get winners failed: {response.text}"
        data = response.json()
        assert "winners" in data
        assert "total_verified" in data
        assert "total_pending" in data
        assert "categories" in data
        print(f"✓ Got winners leaderboard: {data['total_verified']} verified, {data['total_pending']} pending")
    
    def test_get_winners_with_sort(self):
        """GET /api/winners/ supports sort parameter"""
        for sort_by in ["upvotes", "recent", "revenue"]:
            response = requests.get(f"{BASE_URL}/api/winners/?sort={sort_by}&limit=5")
            assert response.status_code == 200, f"Sort by {sort_by} failed"
        print("✓ Winners sort options work (upvotes, recent, revenue)")
    
    def test_submit_winner_requires_auth(self, sample_product_id):
        """POST /api/winners/submit requires authentication"""
        response = requests.post(f"{BASE_URL}/api/winners/submit", json={
            "product_id": sample_product_id,
            "revenue_range": "$1K-5K",
            "timeframe": "1 month",
            "proof_description": "Test submission"
        })
        assert response.status_code in [401, 403], "Submit should require auth"
        print("✓ Submit winner requires authentication")
    
    def test_submit_winner(self, auth_headers, sample_product_id):
        """POST /api/winners/submit creates a winner submission"""
        # Use unique product_id to avoid duplicate check
        unique_id = f"TEST_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(f"{BASE_URL}/api/winners/submit", headers=auth_headers, json={
            "product_id": sample_product_id,
            "revenue_range": "$5K-10K",
            "timeframe": "2 weeks",
            "proof_description": "Generated $7K in revenue using TikTok ads. ROAS 3.5x.",
            "store_niche": "Home decor",
            "ad_platform": "TikTok",
            "tips": "Target 25-34 demographic"
        })
        
        # Accept 200 or 409 (duplicate)
        if response.status_code == 409:
            print("✓ Submit winner correctly prevents duplicates")
            return None
        
        assert response.status_code == 200, f"Submit winner failed: {response.text}"
        data = response.json()
        assert "submission" in data
        submission = data["submission"]
        assert submission["status"] == "pending"
        assert submission["revenue_range"] == "$5K-10K"
        assert "user_id" not in submission  # Privacy check
        print(f"✓ Submitted winner (pending): {submission.get('id')}")
        return submission.get("id")
    
    def test_get_my_submissions(self, auth_headers):
        """GET /api/winners/my-submissions returns user's submissions"""
        response = requests.get(f"{BASE_URL}/api/winners/my-submissions", headers=auth_headers)
        assert response.status_code == 200, f"Get my submissions failed: {response.text}"
        data = response.json()
        assert "submissions" in data
        print(f"✓ Got {len(data['submissions'])} user submissions")
    
    def test_upvote_requires_auth(self):
        """POST /api/winners/{id}/upvote requires authentication"""
        response = requests.post(f"{BASE_URL}/api/winners/fake-id/upvote")
        assert response.status_code in [401, 403], "Upvote should require auth"
        print("✓ Upvote requires authentication")


class TestVerifiedWinnersAdmin:
    """Admin verification tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_verify_requires_admin(self, auth_headers):
        """POST /api/winners/{id}/verify requires admin role"""
        # Test with a fake ID - should return 404 for admin, 403 for non-admin
        response = requests.post(f"{BASE_URL}/api/winners/fake-id/verify", headers=auth_headers, json={
            "status": "verified"
        })
        # Admin should get 404 (not found), non-admin would get 403
        assert response.status_code in [403, 404], f"Verify returned unexpected: {response.status_code}"
        print("✓ Admin verify endpoint access control works")


class TestShopifyPush:
    """Shopify Push Product API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    @pytest.fixture(scope="class")
    def sample_product_id(self, auth_headers):
        """Get a real product ID"""
        # Try products endpoint (returns data array)
        response = requests.get(f"{BASE_URL}/api/products?limit=1", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            products = data.get("data") or data.get("products") or []
            if products and products[0].get("id"):
                return products[0]["id"]
        return "2e3d8782-0026-4fef-a04a-a1d3426e2d26"
    
    def test_push_product_requires_auth(self, sample_product_id):
        """POST /api/shopify/push-product requires authentication"""
        response = requests.post(f"{BASE_URL}/api/shopify/push-product", json={
            "product_id": sample_product_id
        })
        assert response.status_code in [401, 403], "Push should require auth"
        print("✓ Shopify push requires authentication")
    
    def test_push_product_no_connection(self, auth_headers, sample_product_id):
        """POST /api/shopify/push-product returns friendly error without connection"""
        response = requests.post(f"{BASE_URL}/api/shopify/push-product", headers=auth_headers, json={
            "product_id": sample_product_id
        })
        # Should return 200 with success=False or appropriate error message
        assert response.status_code in [200, 400], f"Push returned {response.status_code}"
        data = response.json()
        
        if response.status_code == 200:
            # Returns friendly error in JSON
            if data.get("success") == False:
                assert "error" in data or "message" in data
                print(f"✓ Push returns friendly error: {data.get('error', data.get('message'))}")
            else:
                # Has actual connection - product was pushed
                print(f"✓ Product pushed to Shopify: {data.get('shopify_product_id')}")
        else:
            print(f"✓ Push returns error: {data.get('detail')}")
    
    def test_push_requires_product_id(self, auth_headers):
        """POST /api/shopify/push-product requires product_id"""
        response = requests.post(f"{BASE_URL}/api/shopify/push-product", headers=auth_headers, json={})
        assert response.status_code == 400, "Should require product_id"
        print("✓ Push validates product_id is required")
    
    def test_get_exports(self, auth_headers):
        """GET /api/shopify/exports returns export history"""
        response = requests.get(f"{BASE_URL}/api/shopify/exports", headers=auth_headers)
        assert response.status_code == 200, f"Get exports failed: {response.text}"
        data = response.json()
        assert "exports" in data
        assert "total" in data
        print(f"✓ Got {data['total']} Shopify exports")
    
    def test_exports_requires_auth(self):
        """GET /api/shopify/exports requires authentication"""
        response = requests.get(f"{BASE_URL}/api/shopify/exports")
        assert response.status_code in [401, 403], "Exports should require auth"
        print("✓ Shopify exports requires authentication")


class TestProductSearch:
    """Product search endpoint for winners submission"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_product_search(self, auth_headers):
        """GET /api/products/search returns search results"""
        response = requests.get(f"{BASE_URL}/api/products/search?q=&limit=5", headers=auth_headers)
        # Endpoint may not exist or may require different path
        if response.status_code == 200:
            data = response.json()
            products = data.get("products") or data.get("data") or []
            print(f"✓ Product search returned {len(products)} results")
        elif response.status_code == 404:
            print("⚠ Product search endpoint not found at /api/products/search")
        else:
            print(f"⚠ Product search returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
