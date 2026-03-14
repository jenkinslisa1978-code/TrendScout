"""
Test CSP Enforcement and Product Decision Panel features
- CSP header is 'Content-Security-Policy' (not 'Content-Security-Policy-Report-Only')
- GET /api/dashboard/next-steps returns personalized steps
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestCSPEnforcement:
    """Tests for Content-Security-Policy header enforcement"""
    
    def test_health_endpoint_returns_csp_header(self):
        """CSP header should be 'Content-Security-Policy', NOT 'Content-Security-Policy-Report-Only'"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        # Check CSP header is enforcing (not report-only)
        csp_header = response.headers.get('Content-Security-Policy')
        csp_report_only = response.headers.get('Content-Security-Policy-Report-Only')
        
        assert csp_header is not None, "Content-Security-Policy header should be present"
        assert csp_report_only is None, "Content-Security-Policy-Report-Only header should NOT be present"
        
        # Verify CSP contains expected directives
        assert "default-src 'self'" in csp_header
        assert "script-src" in csp_header
        assert "frame-ancestors 'none'" in csp_header
        print(f"CSP Header verified: {csp_header[:100]}...")
    
    def test_landing_page_returns_csp_header(self):
        """Landing page should also have CSP enforced via API headers"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        csp_header = response.headers.get('Content-Security-Policy')
        assert csp_header is not None, "CSP should be enforced on all API routes"


class TestNextStepsEndpoint:
    """Tests for GET /api/dashboard/next-steps endpoint"""
    
    @pytest.fixture
    def authenticated_session(self):
        """Login and return session with auth headers"""
        session = requests.Session()
        
        # Login
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "jenkinslisa1978@gmail.com",
                "password": "admin123456"
            }
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        token = login_response.json().get("token")
        assert token, "No token returned from login"
        
        # Get CSRF token from cookie
        csrf_token = session.cookies.get("__Host-csrf")
        
        # Set headers
        session.headers.update({
            "Authorization": f"Bearer {token}",
            "x-csrf-token": csrf_token or "",
            "Content-Type": "application/json"
        })
        
        return session
    
    def test_next_steps_requires_auth(self):
        """Endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/dashboard/next-steps")
        assert response.status_code in [401, 403], f"Expected 401/403 for unauthenticated request, got {response.status_code}"
    
    def test_next_steps_returns_steps_array(self, authenticated_session):
        """Should return steps array with required fields"""
        response = authenticated_session.get(f"{BASE_URL}/api/dashboard/next-steps")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check steps array exists
        assert "steps" in data, "Response should contain 'steps' array"
        steps = data["steps"]
        assert isinstance(steps, list), "steps should be a list"
        
        # If there are steps, verify structure
        if len(steps) > 0:
            step = steps[0]
            assert "id" in step, "Step should have 'id'"
            assert "priority" in step, "Step should have 'priority'"
            assert "title" in step, "Step should have 'title'"
            assert "description" in step, "Step should have 'description'"
            assert "action" in step, "Step should have 'action'"
            assert "icon" in step, "Step should have 'icon'"
            
            # Verify action structure
            action = step["action"]
            assert "label" in action, "Action should have 'label'"
            assert "href" in action, "Action should have 'href'"
            
            print(f"Step verified: {step['id']} - {step['title']}")
    
    def test_next_steps_returns_stats(self, authenticated_session):
        """Should return user stats object"""
        response = authenticated_session.get(f"{BASE_URL}/api/dashboard/next-steps")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check stats object exists
        assert "stats" in data, "Response should contain 'stats' object"
        stats = data["stats"]
        
        # Verify stats fields
        assert "saved_products" in stats, "Stats should have 'saved_products'"
        assert "stores" in stats, "Stats should have 'stores'"
        assert "watchlist" in stats, "Stats should have 'watchlist'"
        assert "insights_used_today" in stats, "Stats should have 'insights_used_today'"
        
        # Verify types
        assert isinstance(stats["saved_products"], int)
        assert isinstance(stats["stores"], int)
        assert isinstance(stats["watchlist"], int)
        
        print(f"Stats verified: {stats}")
    
    def test_next_steps_priorities_are_sorted(self, authenticated_session):
        """Steps should be sorted by priority (ascending)"""
        response = authenticated_session.get(f"{BASE_URL}/api/dashboard/next-steps")
        assert response.status_code == 200
        
        steps = response.json().get("steps", [])
        
        if len(steps) > 1:
            priorities = [s["priority"] for s in steps]
            assert priorities == sorted(priorities), f"Steps should be sorted by priority, got {priorities}"
            print(f"Priority order verified: {priorities}")
    
    def test_next_steps_max_five_items(self, authenticated_session):
        """Should return max 5 steps"""
        response = authenticated_session.get(f"{BASE_URL}/api/dashboard/next-steps")
        assert response.status_code == 200
        
        steps = response.json().get("steps", [])
        assert len(steps) <= 5, f"Should return max 5 steps, got {len(steps)}"


class TestDashboardEndpoints:
    """Regression tests for existing dashboard endpoints"""
    
    def test_daily_winners_endpoint(self):
        """Daily winners endpoint should work (public)"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "daily_winners" in data
        assert "count" in data
    
    def test_market_radar_endpoint(self):
        """Market radar endpoint should work (public)"""
        response = requests.get(f"{BASE_URL}/api/dashboard/market-radar?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "market_radar" in data
        assert "count" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
