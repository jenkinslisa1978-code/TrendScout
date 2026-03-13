"""
Test suite for Phase C - Viral & Upgrade Features:
- GET /api/public/daily-picks - Daily curated products (public, no auth)
- GET /api/user/daily-usage - Daily usage tracking (requires auth)
- POST /api/user/track-insight - Increment insight usage (requires auth)
- GET /api/stripe/feature-access - Feature access with daily limits (requires auth)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDailyPicksPublic:
    """Tests for public /api/public/daily-picks endpoint"""
    
    def test_daily_picks_returns_200(self):
        """Daily picks endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Daily picks endpoint returns 200")
    
    def test_daily_picks_returns_required_fields(self):
        """Daily picks should return picks array with required fields"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200
        data = response.json()
        
        assert "picks" in data, "Response should contain 'picks' field"
        assert "date" in data, "Response should contain 'date' field"
        assert isinstance(data["picks"], list), "'picks' should be a list"
        
        print(f"✓ Daily picks returned {len(data['picks'])} products for date {data['date']}")
    
    def test_daily_picks_product_structure(self):
        """Each product in daily picks should have required fields"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200
        data = response.json()
        picks = data.get("picks", [])
        
        if len(picks) == 0:
            pytest.skip("No daily picks returned - cannot validate structure")
        
        # Check first product has required fields
        required_fields = ["id", "slug", "product_name", "launch_score", "margin_percent"]
        product = picks[0]
        
        for field in required_fields:
            assert field in product, f"Product missing required field: {field}"
        
        print(f"✓ Daily picks products have required fields: {required_fields}")
        print(f"  Sample product: {product.get('product_name')} - Score: {product.get('launch_score')}, Margin: {product.get('margin_percent')}%")
    
    def test_daily_picks_returns_max_5_products(self):
        """Daily picks should return at most 5 products"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200
        data = response.json()
        picks = data.get("picks", [])
        
        assert len(picks) <= 5, f"Expected max 5 products, got {len(picks)}"
        print(f"✓ Daily picks returns {len(picks)} products (max 5)")


class TestAuthHelpers:
    """Helper class for authentication"""
    
    @staticmethod
    def register_user(email, password):
        """Register a new user and return auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        # If user exists, try login
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        return None
    
    @staticmethod
    def get_auth_header(token):
        """Return auth header dict"""
        return {"Authorization": f"Bearer {token}"}


class TestDailyUsage:
    """Tests for /api/user/daily-usage endpoint (requires auth)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: get auth token for test user"""
        self.email = "testuser_phase_c@test.com"
        self.password = "test123"
        self.token = TestAuthHelpers.register_user(self.email, self.password)
    
    def test_daily_usage_requires_auth(self):
        """Daily usage endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/user/daily-usage")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Daily usage endpoint requires authentication")
    
    def test_daily_usage_returns_data_with_auth(self):
        """Daily usage should return usage data for authenticated user"""
        if not self.token:
            pytest.skip("Could not get auth token")
        
        response = requests.get(
            f"{BASE_URL}/api/user/daily-usage",
            headers=TestAuthHelpers.get_auth_header(self.token)
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        required_fields = ["daily_limit", "insights_used", "remaining"]
        for field in required_fields:
            assert field in data, f"Response missing required field: {field}"
        
        print(f"✓ Daily usage returned: limit={data['daily_limit']}, used={data['insights_used']}, remaining={data['remaining']}")
    
    def test_daily_usage_has_plan_field(self):
        """Daily usage should include user's plan"""
        if not self.token:
            pytest.skip("Could not get auth token")
        
        response = requests.get(
            f"{BASE_URL}/api/user/daily-usage",
            headers=TestAuthHelpers.get_auth_header(self.token)
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "plan" in data, "Response should include user's plan"
        print(f"✓ User plan: {data['plan']}")


class TestTrackInsight:
    """Tests for POST /api/user/track-insight endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: get auth token for test user"""
        self.email = "testuser_phase_c@test.com"
        self.password = "test123"
        self.token = TestAuthHelpers.register_user(self.email, self.password)
    
    def test_track_insight_requires_auth(self):
        """Track insight endpoint should require authentication"""
        response = requests.post(f"{BASE_URL}/api/user/track-insight")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Track insight endpoint requires authentication")
    
    def test_track_insight_increments_usage(self):
        """Track insight should increment insights_used counter"""
        if not self.token:
            pytest.skip("Could not get auth token")
        
        headers = TestAuthHelpers.get_auth_header(self.token)
        
        # Get current usage
        before_response = requests.get(
            f"{BASE_URL}/api/user/daily-usage",
            headers=headers
        )
        before_used = before_response.json().get("insights_used", 0) if before_response.status_code == 200 else 0
        
        # Track an insight
        response = requests.post(
            f"{BASE_URL}/api/user/track-insight",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "insights_used" in data, "Response should include insights_used"
        assert data["insights_used"] == before_used + 1, f"Expected insights_used to increment from {before_used} to {before_used + 1}"
        
        print(f"✓ Track insight incremented usage from {before_used} to {data['insights_used']}")
    
    def test_track_insight_returns_limit_reached(self):
        """Track insight should indicate when limit is reached"""
        if not self.token:
            pytest.skip("Could not get auth token")
        
        response = requests.post(
            f"{BASE_URL}/api/user/track-insight",
            headers=TestAuthHelpers.get_auth_header(self.token)
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "limit_reached" in data, "Response should include limit_reached field"
        print(f"✓ Track insight returns limit_reached: {data['limit_reached']}")


class TestFeatureAccess:
    """Tests for GET /api/stripe/feature-access endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: get auth token for test user"""
        self.email = "testuser_phase_c@test.com"
        self.password = "test123"
        self.token = TestAuthHelpers.register_user(self.email, self.password)
    
    def test_feature_access_requires_auth(self):
        """Feature access endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/stripe/feature-access")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Feature access endpoint requires authentication")
    
    def test_feature_access_returns_daily_limits(self):
        """Feature access should return max_analyses_daily and insights_used_today"""
        if not self.token:
            pytest.skip("Could not get auth token")
        
        response = requests.get(
            f"{BASE_URL}/api/stripe/feature-access",
            headers=TestAuthHelpers.get_auth_header(self.token)
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "features" in data, "Response should include features object"
        
        features = data["features"]
        assert "max_analyses_daily" in features, "features should include max_analyses_daily"
        assert "insights_used_today" in features, "features should include insights_used_today"
        
        print(f"✓ Feature access returns daily limits: max={features['max_analyses_daily']}, used={features['insights_used_today']}")
    
    def test_feature_access_returns_plan(self):
        """Feature access should return user's plan"""
        if not self.token:
            pytest.skip("Could not get auth token")
        
        response = requests.get(
            f"{BASE_URL}/api/stripe/feature-access",
            headers=TestAuthHelpers.get_auth_header(self.token)
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "plan" in data, "Response should include plan"
        print(f"✓ Feature access returns plan: {data['plan']}")


class TestAdminUserFeatureAccess:
    """Tests for admin user with elite access"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: get auth token for admin user"""
        self.email = "jenkinslisa1978@gmail.com"
        self.password = "Test123!"
        self.token = TestAuthHelpers.register_user(self.email, self.password)
    
    def test_admin_has_unlimited_access(self):
        """Admin users should have unlimited daily analyses"""
        if not self.token:
            pytest.skip("Could not get auth token for admin user")
        
        response = requests.get(
            f"{BASE_URL}/api/stripe/feature-access",
            headers=TestAuthHelpers.get_auth_header(self.token)
        )
        
        if response.status_code != 200:
            pytest.skip(f"Could not get feature access: {response.status_code}")
        
        data = response.json()
        
        # Admin should have elite plan or is_admin flag
        is_admin = data.get("is_admin", False)
        plan = data.get("plan", "free")
        
        print(f"✓ Admin user - is_admin: {is_admin}, plan: {plan}")
        
        if is_admin or plan == "elite":
            features = data.get("features", {})
            daily_limit = features.get("max_analyses_daily", 0)
            # Elite/admin should have high or unlimited (-1) daily limit
            assert daily_limit == -1 or daily_limit >= 50, f"Expected high or unlimited daily limit for admin, got {daily_limit}"
            print(f"  Daily limit: {daily_limit} (-1 means unlimited)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
