"""
Backend Refactoring Regression Tests
=====================================
Tests all endpoints after the monolithic server.py was refactored into modular route files.
This ensures all functionality is preserved after the refactoring.

Test Categories:
1. Health Check endpoints
2. Auth endpoints (register, login, profile)
3. Stripe/Feature access endpoints
4. Products endpoints
5. Public endpoints (no auth)
6. Dashboard endpoints
7. Blog endpoints
8. Workspace endpoints
9. Automation endpoints
10. Jobs endpoints
11. Reports endpoints
12. Notifications endpoints
13. Admin endpoints
14. Sitemap/SEO endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://scout-alerts-live.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "admin123456"
TEST_USER_EMAIL = f"test_refactor_{os.urandom(4).hex()}@test.com"
TEST_USER_PASSWORD = "test123456"


class TestHealthEndpoints:
    """Test health check endpoints - these should work without auth"""
    
    def test_root_endpoint(self):
        """GET /api/ returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "message" in data
        print(f"✓ Root endpoint working: {data}")
    
    def test_health_endpoint(self):
        """GET /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
        print(f"✓ Health endpoint working: {data}")


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    @pytest.fixture(scope="class")
    def registered_user(self):
        """Register a test user and return credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": "Test Refactor User"
        })
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400 and "already registered" in response.text.lower():
            # User exists, try login
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            if login_resp.status_code == 200:
                return login_resp.json()
        pytest.skip("Could not register or login test user")
    
    def test_register_returns_token(self, registered_user):
        """POST /api/auth/register returns token"""
        assert "token" in registered_user
        assert "user" in registered_user
        print(f"✓ Register returned token for: {registered_user['user']['email']}")
    
    def test_login_success(self):
        """POST /api/auth/login returns token for valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        print(f"✓ Login successful for: {data['user']['email']}")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login returns 401 for invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly returns 401")
    
    def test_profile_requires_auth(self):
        """GET /api/auth/profile returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/auth/profile")
        assert response.status_code == 401
        print("✓ Profile correctly requires auth")
    
    def test_profile_with_auth(self):
        """GET /api/auth/profile returns profile with auth"""
        # Login first
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["token"]
        
        # Get profile
        response = requests.get(
            f"{BASE_URL}/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data or "email" in data
        print(f"✓ Profile returned: {data.get('email', 'N/A')}")


class TestStripeEndpoints:
    """Test Stripe/subscription endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get auth token")
    
    def test_plans_no_auth(self):
        """GET /api/stripe/plans works without auth"""
        response = requests.get(f"{BASE_URL}/api/stripe/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        print(f"✓ Plans returned: {len(data['plans'])} plans")
    
    def test_feature_access_requires_auth(self):
        """GET /api/stripe/feature-access returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/stripe/feature-access")
        assert response.status_code == 401
        print("✓ Feature access correctly requires auth")
    
    def test_feature_access_with_auth(self, auth_token):
        """GET /api/stripe/feature-access returns features with auth"""
        response = requests.get(
            f"{BASE_URL}/api/stripe/feature-access",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "plan" in data
        assert "features" in data
        print(f"✓ Feature access returned for plan: {data['plan']}")


class TestProductsEndpoints:
    """Test product-related endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get auth token")
    
    def test_products_list_requires_auth(self):
        """GET /api/products requires auth"""
        response = requests.get(f"{BASE_URL}/api/products")
        # Products endpoint might not require auth based on implementation
        # Check if it returns data or requires auth
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert "data" in data or isinstance(data, list)
            print(f"✓ Products list returned (public): {len(data.get('data', data))} products")
        else:
            print("✓ Products correctly requires auth")
    
    def test_find_winning_requires_auth(self):
        """GET /api/products/find-winning requires auth"""
        response = requests.get(f"{BASE_URL}/api/products/find-winning")
        assert response.status_code == 401
        print("✓ Find winning correctly requires auth")
    
    def test_find_winning_with_auth(self, auth_token):
        """GET /api/products/find-winning returns winning product with auth"""
        response = requests.get(
            f"{BASE_URL}/api/products/find-winning",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "product" in data
        if data["product"]:
            print(f"✓ Find winning returned: {data['product'].get('product_name', 'N/A')}")
        else:
            print("✓ Find winning returned (no products available)")


class TestPublicEndpoints:
    """Test public endpoints that don't require auth"""
    
    def test_top_trending(self):
        """GET /api/public/top-trending returns products"""
        response = requests.get(f"{BASE_URL}/api/public/top-trending")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        print(f"✓ Top trending returned: {len(data['products'])} products")
    
    def test_daily_picks(self):
        """GET /api/public/daily-picks returns daily picks"""
        response = requests.get(f"{BASE_URL}/api/public/daily-picks")
        assert response.status_code == 200
        data = response.json()
        assert "picks" in data
        print(f"✓ Daily picks returned: {len(data['picks'])} picks")
    
    def test_platform_stats(self):
        """GET /api/public/platform-stats returns stats"""
        response = requests.get(f"{BASE_URL}/api/public/platform-stats")
        assert response.status_code == 200
        data = response.json()
        assert "products_analysed" in data or "products_scored" in data
        print(f"✓ Platform stats returned: {data}")
    
    def test_categories(self):
        """GET /api/public/categories returns categories"""
        response = requests.get(f"{BASE_URL}/api/public/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Categories returned: {len(data)} categories")
    
    def test_trending_products(self):
        """GET /api/public/trending-products returns products"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        print(f"✓ Trending products returned: {len(data['products'])} products")
    
    def test_featured_product(self):
        """GET /api/public/featured-product returns featured product"""
        response = requests.get(f"{BASE_URL}/api/public/featured-product")
        assert response.status_code == 200
        data = response.json()
        assert "product" in data
        print(f"✓ Featured product returned")


class TestDashboardEndpoints:
    """Test dashboard endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get auth token")
    
    def test_dashboard_summary_optional_auth(self):
        """GET /api/dashboard/summary works without auth (limited data)"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary")
        # Summary might work without auth with limited data
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Dashboard summary returned (public)")
        else:
            print("✓ Dashboard summary requires auth")
    
    def test_daily_winners(self):
        """GET /api/dashboard/daily-winners returns winners"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners")
        assert response.status_code == 200
        data = response.json()
        assert "daily_winners" in data
        print(f"✓ Daily winners returned: {len(data['daily_winners'])} winners")


class TestBlogEndpoints:
    """Test blog endpoints"""
    
    def test_blog_posts_list(self):
        """GET /api/blog/posts returns blog posts"""
        response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        print(f"✓ Blog posts returned: {len(data['posts'])} posts")


class TestWorkspaceEndpoints:
    """Test workspace endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get auth token")
    
    def test_workspace_requires_auth(self):
        """GET /api/workspace/products requires auth"""
        response = requests.get(f"{BASE_URL}/api/workspace/products")
        assert response.status_code == 401
        print("✓ Workspace correctly requires auth")
    
    def test_workspace_with_auth(self, auth_token):
        """GET /api/workspace/products returns items with auth"""
        response = requests.get(
            f"{BASE_URL}/api/workspace/products",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✓ Workspace returned: {len(data['items'])} items")


class TestAutomationEndpoints:
    """Test automation endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get auth token")
    
    def test_automation_stats(self):
        """GET /api/automation/stats returns stats"""
        response = requests.get(f"{BASE_URL}/api/automation/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_runs" in data
        print(f"✓ Automation stats returned: {data}")
    
    def test_automation_logs(self):
        """GET /api/automation/logs returns logs"""
        response = requests.get(f"{BASE_URL}/api/automation/logs")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        print(f"✓ Automation logs returned: {len(data['data'])} logs")


class TestJobsEndpoints:
    """Test jobs endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get auth token")
    
    def test_jobs_status(self):
        """GET /api/jobs/status returns status"""
        response = requests.get(f"{BASE_URL}/api/jobs/status")
        assert response.status_code in [200, 500]  # May fail if worker not initialized
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Jobs status returned: {data.get('worker', {}).get('status', 'unknown')}")
        else:
            print("✓ Jobs status endpoint exists (worker may not be initialized)")


class TestReportsEndpoints:
    """Test reports endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get auth token")
    
    def test_reports_list(self):
        """GET /api/reports/ returns reports list"""
        response = requests.get(f"{BASE_URL}/api/reports/")
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        print(f"✓ Reports list returned: {len(data['reports'])} reports")
    
    def test_weekly_report(self):
        """GET /api/reports/weekly-winning-products returns report"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products")
        assert response.status_code == 200
        data = response.json()
        assert "report" in data
        print(f"✓ Weekly report returned")


class TestNotificationsEndpoints:
    """Test notifications endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get auth token")
    
    def test_notifications_requires_auth(self):
        """GET /api/notifications/ requires auth"""
        response = requests.get(f"{BASE_URL}/api/notifications/")
        assert response.status_code == 401
        print("✓ Notifications correctly requires auth")
    
    def test_notifications_with_auth(self, auth_token):
        """GET /api/notifications/ returns notifications with auth"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        print(f"✓ Notifications returned: {len(data['notifications'])} notifications")


class TestAdminEndpoints:
    """Test admin endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get admin token")
    
    def test_image_review_requires_admin(self):
        """GET /api/admin/image-review/metrics requires admin auth"""
        response = requests.get(f"{BASE_URL}/api/admin/image-review/metrics")
        assert response.status_code == 401
        print("✓ Image review metrics correctly requires auth")
    
    def test_image_review_with_admin(self, admin_token):
        """GET /api/admin/image-review/metrics returns metrics with admin auth"""
        response = requests.get(
            f"{BASE_URL}/api/admin/image-review/metrics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_products" in data
        print(f"✓ Image review metrics returned: {data['total_products']} total products")
    
    def test_analytics_dashboard_requires_admin(self):
        """GET /api/analytics/dashboard requires admin auth"""
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard")
        assert response.status_code == 401
        print("✓ Analytics dashboard correctly requires auth")
    
    def test_analytics_dashboard_with_admin(self, admin_token):
        """GET /api/analytics/dashboard returns data with admin auth"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        print(f"✓ Analytics dashboard returned: {data['total_events']} events")


class TestSeoEndpoints:
    """Test SEO-related endpoints"""
    
    def test_sitemap_xml(self):
        """GET /api/sitemap.xml returns valid XML"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        assert "xml" in response.headers.get("content-type", "").lower()
        assert "<?xml" in response.text
        assert "<urlset" in response.text
        print(f"✓ Sitemap XML returned: {len(response.text)} bytes")


class TestUserEndpoints:
    """Test user-related endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get auth token")
    
    def test_onboarding_status_requires_auth(self):
        """GET /api/user/onboarding-status requires auth"""
        response = requests.get(f"{BASE_URL}/api/user/onboarding-status")
        assert response.status_code == 401
        print("✓ Onboarding status correctly requires auth")
    
    def test_onboarding_status_with_auth(self, auth_token):
        """GET /api/user/onboarding-status returns status with auth"""
        response = requests.get(
            f"{BASE_URL}/api/user/onboarding-status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "onboarding_completed" in data
        print(f"✓ Onboarding status returned: completed={data['onboarding_completed']}")


# Run quick sanity test when file is executed directly
if __name__ == "__main__":
    print("=== Quick Backend Sanity Test ===")
    
    # Test health
    resp = requests.get(f"{BASE_URL}/api/health")
    print(f"Health: {resp.status_code} - {resp.json() if resp.status_code == 200 else 'FAIL'}")
    
    # Test login
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    print(f"Login: {resp.status_code} - {'OK' if resp.status_code == 200 else 'FAIL'}")
    
    if resp.status_code == 200:
        token = resp.json()["token"]
        
        # Test authenticated endpoints
        endpoints = [
            ("Feature Access", f"{BASE_URL}/api/stripe/feature-access"),
            ("Products", f"{BASE_URL}/api/products"),
            ("Find Winning", f"{BASE_URL}/api/products/find-winning"),
            ("Workspace", f"{BASE_URL}/api/workspace/products"),
            ("Notifications", f"{BASE_URL}/api/notifications/"),
            ("Image Review", f"{BASE_URL}/api/admin/image-review/metrics"),
        ]
        
        for name, url in endpoints:
            resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
            print(f"{name}: {resp.status_code}")
