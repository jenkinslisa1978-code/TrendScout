"""
Dashboard Intelligence API Tests

Tests for:
- GET /api/dashboard/daily-winners - Daily winning products
- GET /api/dashboard/market-radar - Market clusters with opportunity scores
- GET /api/dashboard/watchlist (auth required) - User's watchlist
- GET /api/dashboard/alerts (auth required) - User's alerts
- POST /api/dashboard/watchlist (auth required) - Add to watchlist
- DELETE /api/dashboard/watchlist/{product_id} (auth required) - Remove from watchlist
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
DEMO_TOKEN = "Bearer demo_demo-user-id"

# Test product IDs that may exist in the database
test_product_id = None


class TestHealthCheck:
    """Basic health check to ensure API is accessible"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Health check passed")


class TestDailyWinners:
    """Tests for GET /api/dashboard/daily-winners"""
    
    def test_daily_winners_returns_200(self):
        """Test that daily winners endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners")
        assert response.status_code == 200
        print(f"✓ Daily winners endpoint returned 200")
    
    def test_daily_winners_structure(self):
        """Test daily winners response structure"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check response structure
        assert "daily_winners" in data
        assert "count" in data
        assert "generated_at" in data
        assert isinstance(data["daily_winners"], list)
        
        print(f"✓ Daily winners structure valid - {data['count']} winners returned")
        
        # If there are winners, check item structure
        if len(data["daily_winners"]) > 0:
            winner = data["daily_winners"][0]
            required_fields = [
                "product_id", "product_name", "category", "trend_stage",
                "success_probability", "validation_result", "competition_level"
            ]
            for field in required_fields:
                assert field in winner, f"Missing field: {field}"
            
            # Store product_id for later tests
            global test_product_id
            test_product_id = winner["product_id"]
            
            print(f"✓ Winner item structure valid - first winner: {winner['product_name']}")
    
    def test_daily_winners_limit_param(self):
        """Test that limit parameter works"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["daily_winners"]) <= 3
        print(f"✓ Limit parameter works - returned {len(data['daily_winners'])} winners")


class TestMarketRadar:
    """Tests for GET /api/dashboard/market-radar"""
    
    def test_market_radar_returns_200(self):
        """Test that market radar endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dashboard/market-radar")
        assert response.status_code == 200
        print(f"✓ Market radar endpoint returned 200")
    
    def test_market_radar_structure(self):
        """Test market radar response structure"""
        response = requests.get(f"{BASE_URL}/api/dashboard/market-radar?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check response structure
        assert "market_radar" in data
        assert "count" in data
        assert "generated_at" in data
        assert isinstance(data["market_radar"], list)
        
        print(f"✓ Market radar structure valid - {data['count']} clusters returned")
        
        # If there are clusters, check item structure
        if len(data["market_radar"]) > 0:
            cluster = data["market_radar"][0]
            required_fields = [
                "cluster_name", "trend_stage", "avg_success_probability",
                "product_count", "competition_level", "opportunity_score"
            ]
            for field in required_fields:
                assert field in cluster, f"Missing field: {field}"
            
            print(f"✓ Cluster item structure valid - first cluster: {cluster['cluster_name']}")
    
    def test_market_radar_limit_param(self):
        """Test that limit parameter works"""
        response = requests.get(f"{BASE_URL}/api/dashboard/market-radar?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["market_radar"]) <= 3
        print(f"✓ Limit parameter works - returned {len(data['market_radar'])} clusters")


class TestWatchlistAuthenticated:
    """Tests for watchlist endpoints (auth required)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": DEMO_TOKEN
        }
    
    def test_get_watchlist_without_auth_returns_401(self):
        """Test that watchlist requires authentication"""
        response = requests.get(f"{BASE_URL}/api/dashboard/watchlist")
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403]
        print(f"✓ Watchlist requires auth - returned {response.status_code}")
    
    def test_get_watchlist_with_auth_returns_200(self):
        """Test that watchlist returns 200 with valid auth"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/watchlist",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "watchlist" in data
        assert "count" in data
        assert isinstance(data["watchlist"], list)
        
        print(f"✓ Watchlist with auth - {data['count']} items")
    
    def test_add_to_watchlist(self):
        """Test adding a product to watchlist"""
        global test_product_id
        
        if not test_product_id:
            # Get a product first
            products_response = requests.get(f"{BASE_URL}/api/products?limit=1")
            if products_response.status_code == 200:
                products_data = products_response.json()
                if products_data.get("data") and len(products_data["data"]) > 0:
                    test_product_id = products_data["data"][0].get("id")
        
        if not test_product_id:
            pytest.skip("No products available to test watchlist")
        
        # First remove if exists (cleanup)
        requests.delete(
            f"{BASE_URL}/api/dashboard/watchlist/{test_product_id}",
            headers=self.headers
        )
        
        # Add to watchlist
        response = requests.post(
            f"{BASE_URL}/api/dashboard/watchlist",
            headers=self.headers,
            json={"product_id": test_product_id}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ Added product to watchlist - {data.get('message', '')}")
    
    def test_add_duplicate_to_watchlist_returns_400(self):
        """Test that adding duplicate returns 400"""
        global test_product_id
        
        if not test_product_id:
            pytest.skip("No product ID for duplicate test")
        
        # Try to add same product again
        response = requests.post(
            f"{BASE_URL}/api/dashboard/watchlist",
            headers=self.headers,
            json={"product_id": test_product_id}
        )
        
        # Should return 400 for duplicate
        assert response.status_code == 400
        print(f"✓ Duplicate watchlist add returns 400")
    
    def test_check_watchlist_status(self):
        """Test checking if product is in watchlist"""
        global test_product_id
        
        if not test_product_id:
            pytest.skip("No product ID for status check")
        
        response = requests.get(
            f"{BASE_URL}/api/dashboard/watchlist/check/{test_product_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "in_watchlist" in data
        assert data["in_watchlist"] == True  # We just added it
        
        print(f"✓ Check watchlist status - in_watchlist: {data['in_watchlist']}")
    
    def test_remove_from_watchlist(self):
        """Test removing a product from watchlist"""
        global test_product_id
        
        if not test_product_id:
            pytest.skip("No product ID for remove test")
        
        response = requests.delete(
            f"{BASE_URL}/api/dashboard/watchlist/{test_product_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        print(f"✓ Removed product from watchlist")
    
    def test_remove_nonexistent_returns_404(self):
        """Test removing non-existent item returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/dashboard/watchlist/nonexistent-product-id-123",
            headers=self.headers
        )
        
        assert response.status_code == 404
        print(f"✓ Remove non-existent item returns 404")


class TestAlertsAuthenticated:
    """Tests for alerts endpoints (auth required)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": DEMO_TOKEN
        }
    
    def test_get_alerts_without_auth_returns_401(self):
        """Test that alerts requires authentication"""
        response = requests.get(f"{BASE_URL}/api/dashboard/alerts")
        assert response.status_code in [401, 403]
        print(f"✓ Alerts requires auth - returned {response.status_code}")
    
    def test_get_alerts_with_auth_returns_200(self):
        """Test that alerts returns 200 with valid auth"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/alerts",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        assert "count" in data
        assert "unread_count" in data
        assert isinstance(data["alerts"], list)
        
        print(f"✓ Alerts with auth - {data['count']} alerts, {data['unread_count']} unread")
    
    def test_get_alerts_with_limit(self):
        """Test alerts limit parameter"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/alerts?limit=5",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["alerts"]) <= 5
        
        print(f"✓ Alerts limit works - {len(data['alerts'])} alerts returned")
    
    def test_get_unread_alerts_only(self):
        """Test unread_only parameter"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/alerts?unread_only=true",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # All returned should be unread
        for alert in data["alerts"]:
            if "is_read" in alert:
                assert alert["is_read"] == False
        
        print(f"✓ Unread only filter works")


class TestDashboardSummary:
    """Tests for GET /api/dashboard/summary"""
    
    def test_summary_public_returns_200(self):
        """Test that summary works without auth (returns partial data)"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary")
        # Should return 200 even without auth
        assert response.status_code == 200
        
        data = response.json()
        assert "daily_winners" in data
        assert "market_radar" in data
        
        print(f"✓ Summary (public) returned 200")
    
    def test_summary_with_auth(self):
        """Test summary with authentication includes watchlist/alerts"""
        headers = {
            "Authorization": DEMO_TOKEN
        }
        
        response = requests.get(
            f"{BASE_URL}/api/dashboard/summary",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "daily_winners" in data
        assert "market_radar" in data
        assert "watchlist_preview" in data
        assert "unread_alerts" in data
        
        print(f"✓ Summary (authenticated) includes watchlist and alerts")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
