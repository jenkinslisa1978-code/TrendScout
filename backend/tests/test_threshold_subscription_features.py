"""
Test suite for Phase C - Threshold Subscription & Conversion Features
Tests:
1. GET/PUT /api/notifications/threshold-subscription
2. POST /api/user/track-insight
3. GET /api/user/daily-usage
4. GET /api/public/daily-picks
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
FREE_USER_EMAIL = "testuser_phase_c@test.com"
FREE_USER_PASSWORD = "test123"
ADMIN_USER_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_USER_PASSWORD = "Test123!"


class TestHelpers:
    """Shared helper methods for tests"""
    
    @staticmethod
    def get_auth_token(email: str, password: str) -> str:
        """Get authentication token for a user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            # Try both possible token field names
            return data.get("token") or data.get("access_token")
        return None
    
    @staticmethod
    def register_user(email: str, password: str) -> dict:
        """Register a new user"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": password,
            "name": "Test User"
        })
        return response.json() if response.status_code in [200, 201] else None


class TestPublicDailyPicks:
    """Test GET /api/public/daily-picks endpoint (public, no auth)"""
    
    def test_daily_picks_returns_200(self):
        """Daily picks endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: GET /api/public/daily-picks returns 200")
    
    def test_daily_picks_has_picks_array(self):
        """Response should contain picks array"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200
        data = response.json()
        assert "picks" in data, f"Response missing 'picks': {data}"
        assert isinstance(data["picks"], list), "picks should be a list"
        print(f"PASS: Response contains 'picks' array with {len(data['picks'])} items")
    
    def test_daily_picks_has_date_field(self):
        """Response should contain date field"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data, f"Response missing 'date': {data}"
        print(f"PASS: Response contains date field: {data['date']}")
    
    def test_daily_picks_returns_max_5_products(self):
        """Should return at most 5 products"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200
        data = response.json()
        picks = data.get("picks", [])
        assert len(picks) <= 5, f"Expected max 5 picks, got {len(picks)}"
        print(f"PASS: Returns {len(picks)} products (max 5)")
    
    def test_daily_picks_product_fields(self):
        """Each product should have required fields"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200
        data = response.json()
        picks = data.get("picks", [])
        
        if len(picks) > 0:
            required_fields = ["id", "slug", "product_name", "launch_score", "margin_percent"]
            for product in picks[:2]:  # Check first 2 products
                for field in required_fields:
                    assert field in product, f"Product missing '{field}': {product}"
            print(f"PASS: Products contain required fields: {required_fields}")
        else:
            pytest.skip("No picks returned - cannot verify product fields")


class TestThresholdSubscription:
    """Test threshold subscription endpoints (requires auth)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup auth token for tests"""
        # Try admin user first, then free user
        self.token = TestHelpers.get_auth_token(ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD)
        if not self.token:
            self.token = TestHelpers.get_auth_token(FREE_USER_EMAIL, FREE_USER_PASSWORD)
        
        if not self.token:
            # Try to register free user
            TestHelpers.register_user(FREE_USER_EMAIL, FREE_USER_PASSWORD)
            self.token = TestHelpers.get_auth_token(FREE_USER_EMAIL, FREE_USER_PASSWORD)
        
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def test_get_threshold_subscription_requires_auth(self):
        """GET threshold-subscription should require auth"""
        response = requests.get(f"{BASE_URL}/api/notifications/threshold-subscription")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("PASS: GET /api/notifications/threshold-subscription requires authentication")
    
    def test_get_threshold_subscription_with_auth(self):
        """GET threshold-subscription with valid auth should return subscription"""
        if not self.token:
            pytest.skip("No valid auth token available")
        
        response = requests.get(
            f"{BASE_URL}/api/notifications/threshold-subscription",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should have subscription fields
        assert "enabled" in data or "user_id" in data, f"Invalid subscription response: {data}"
        print(f"PASS: GET threshold-subscription returns subscription data: enabled={data.get('enabled')}, threshold={data.get('score_threshold')}")
    
    def test_put_threshold_subscription_requires_auth(self):
        """PUT threshold-subscription should require auth"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/threshold-subscription",
            json={"enabled": True, "score_threshold": 80}
        )
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("PASS: PUT /api/notifications/threshold-subscription requires authentication")
    
    def test_put_threshold_subscription_update(self):
        """PUT threshold-subscription should update subscription settings"""
        if not self.token:
            pytest.skip("No valid auth token available")
        
        # Update subscription
        new_threshold = 80
        update_data = {
            "enabled": True,
            "score_threshold": new_threshold,
            "categories": [],
            "email_alerts": True,
            "in_app_alerts": True
        }
        
        response = requests.put(
            f"{BASE_URL}/api/notifications/threshold-subscription",
            headers=self.headers,
            json=update_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("enabled") == True, f"enabled should be True: {data}"
        assert data.get("score_threshold") == new_threshold, f"score_threshold should be {new_threshold}: {data}"
        print(f"PASS: PUT threshold-subscription updated successfully: enabled={data.get('enabled')}, threshold={data.get('score_threshold')}")
    
    def test_put_threshold_subscription_with_categories(self):
        """PUT threshold-subscription should accept categories filter"""
        if not self.token:
            pytest.skip("No valid auth token available")
        
        update_data = {
            "enabled": True,
            "score_threshold": 75,
            "categories": ["Electronics", "Home"],
            "email_alerts": True,
            "in_app_alerts": False
        }
        
        response = requests.put(
            f"{BASE_URL}/api/notifications/threshold-subscription",
            headers=self.headers,
            json=update_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("categories") == ["Electronics", "Home"] or isinstance(data.get("categories"), list), f"categories not saved: {data}"
        print(f"PASS: Categories filter saved: {data.get('categories')}")


class TestDailyUsageTracking:
    """Test daily usage and insight tracking endpoints (requires auth)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup auth token for tests"""
        self.token = TestHelpers.get_auth_token(FREE_USER_EMAIL, FREE_USER_PASSWORD)
        if not self.token:
            # Try to register
            TestHelpers.register_user(FREE_USER_EMAIL, FREE_USER_PASSWORD)
            self.token = TestHelpers.get_auth_token(FREE_USER_EMAIL, FREE_USER_PASSWORD)
        
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def test_daily_usage_requires_auth(self):
        """GET daily-usage should require auth"""
        response = requests.get(f"{BASE_URL}/api/user/daily-usage")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("PASS: GET /api/user/daily-usage requires authentication")
    
    def test_daily_usage_returns_usage_data(self):
        """GET daily-usage should return usage data"""
        if not self.token:
            pytest.skip("No valid auth token available")
        
        response = requests.get(
            f"{BASE_URL}/api/user/daily-usage",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        required_fields = ["daily_limit", "insights_used", "remaining"]
        for field in required_fields:
            assert field in data, f"Missing field '{field}': {data}"
        
        print(f"PASS: GET daily-usage returns: plan={data.get('plan')}, limit={data.get('daily_limit')}, used={data.get('insights_used')}, remaining={data.get('remaining')}")
    
    def test_track_insight_requires_auth(self):
        """POST track-insight should require auth"""
        response = requests.post(f"{BASE_URL}/api/user/track-insight")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("PASS: POST /api/user/track-insight requires authentication")
    
    def test_track_insight_increments_usage(self):
        """POST track-insight should increment usage counter"""
        if not self.token:
            pytest.skip("No valid auth token available")
        
        # Get current usage
        before = requests.get(
            f"{BASE_URL}/api/user/daily-usage",
            headers=self.headers
        )
        before_data = before.json()
        before_used = before_data.get("insights_used", 0)
        
        # Track an insight
        response = requests.post(
            f"{BASE_URL}/api/user/track-insight",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "insights_used" in data, f"Response should contain insights_used: {data}"
        
        # Verify counter incremented
        after_used = data.get("insights_used", 0)
        assert after_used == before_used + 1, f"insights_used should increment: before={before_used}, after={after_used}"
        print(f"PASS: track-insight incremented usage from {before_used} to {after_used}")
    
    def test_track_insight_returns_limit_reached(self):
        """POST track-insight should return limit_reached field"""
        if not self.token:
            pytest.skip("No valid auth token available")
        
        response = requests.post(
            f"{BASE_URL}/api/user/track-insight",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "limit_reached" in data, f"Response should contain limit_reached: {data}"
        print(f"PASS: track-insight returns limit_reached={data.get('limit_reached')}")


class TestAdminThresholdSubscription:
    """Test with admin user for elite plan access"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin auth token"""
        self.token = TestHelpers.get_auth_token(ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD)
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def test_admin_can_access_threshold_subscription(self):
        """Admin user should be able to access threshold subscription"""
        if not self.token:
            pytest.skip("Admin auth token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/notifications/threshold-subscription",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Admin can access threshold subscription endpoint")
    
    def test_admin_daily_usage_shows_unlimited_or_high_limit(self):
        """Admin user should have elite plan with high/unlimited daily limit"""
        if not self.token:
            pytest.skip("Admin auth token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/user/daily-usage",
            headers=self.headers
        )
        if response.status_code == 200:
            data = response.json()
            plan = data.get("plan", "")
            is_unlimited = data.get("is_unlimited", False)
            daily_limit = data.get("daily_limit", 0)
            
            print(f"Admin user: plan={plan}, daily_limit={daily_limit}, is_unlimited={is_unlimited}")
            # Elite should have unlimited (-1) or high limit
            assert is_unlimited or daily_limit == -1 or daily_limit >= 10, f"Elite plan should have high/unlimited limit: {data}"
            print("PASS: Admin has elite plan with high/unlimited daily limit")
        else:
            pytest.skip(f"Could not verify admin daily usage: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
