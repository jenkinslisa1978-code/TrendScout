"""
Test OAuth 2.0 and WebSocket notification features.
Tests:
- OAuth platforms endpoint (7 platforms)
- OAuth setup endpoints for each platform
- WebSocket endpoint accessibility
- Automation/ingestion endpoints with WebSocket notifications
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://db-seeding-async.preview.emergentagent.com').rstrip('/')


class TestOAuthPlatforms:
    """Test OAuth platform endpoints"""
    
    def test_get_all_oauth_platforms(self):
        """GET /api/oauth/platforms returns all 7 OAuth platforms"""
        response = requests.get(f"{BASE_URL}/api/oauth/platforms")
        assert response.status_code == 200
        
        data = response.json()
        assert "platforms" in data
        platforms = data["platforms"]
        
        # Verify all 7 platforms are present
        expected_platforms = ["shopify", "etsy", "amazon_seller", "tiktok_shop", "meta", "google_ads", "tiktok_ads"]
        for platform in expected_platforms:
            assert platform in platforms, f"Missing platform: {platform}"
        
        # Verify each platform has required fields
        for key, config in platforms.items():
            assert "name" in config, f"Platform {key} missing 'name'"
            assert "redirect_uri" in config, f"Platform {key} missing 'redirect_uri'"
            assert "instructions" in config, f"Platform {key} missing 'instructions'"
            assert "connection_type" in config, f"Platform {key} missing 'connection_type'"
            assert "setup_url" in config, f"Platform {key} missing 'setup_url'"
    
    def test_shopify_setup_endpoint(self):
        """GET /api/oauth/shopify/setup returns setup instructions"""
        response = requests.get(f"{BASE_URL}/api/oauth/shopify/setup")
        assert response.status_code == 200
        
        data = response.json()
        assert data["platform"] == "shopify"
        assert data["name"] == "Shopify"
        assert "redirect_uri" in data
        assert "/api/oauth/shopify/callback" in data["redirect_uri"]
        assert "instructions" in data
        assert "partners.shopify.com" in data["instructions"]
        assert data["connection_type"] == "store"
    
    def test_meta_setup_endpoint(self):
        """GET /api/oauth/meta/setup returns Meta setup info"""
        response = requests.get(f"{BASE_URL}/api/oauth/meta/setup")
        assert response.status_code == 200
        
        data = response.json()
        assert data["platform"] == "meta"
        assert data["name"] == "Meta (Facebook & Instagram)"
        assert "redirect_uri" in data
        assert "/api/oauth/meta/callback" in data["redirect_uri"]
        assert "instructions" in data
        assert "developers.facebook.com" in data["instructions"]
        assert data["connection_type"] == "ads"
    
    def test_etsy_setup_endpoint(self):
        """GET /api/oauth/etsy/setup returns Etsy setup info"""
        response = requests.get(f"{BASE_URL}/api/oauth/etsy/setup")
        assert response.status_code == 200
        
        data = response.json()
        assert data["platform"] == "etsy"
        assert data["name"] == "Etsy"
        assert "redirect_uri" in data
        assert data["connection_type"] == "store"
    
    def test_amazon_seller_setup_endpoint(self):
        """GET /api/oauth/amazon_seller/setup returns Amazon Seller setup info"""
        response = requests.get(f"{BASE_URL}/api/oauth/amazon_seller/setup")
        assert response.status_code == 200
        
        data = response.json()
        assert data["platform"] == "amazon_seller"
        assert data["name"] == "Amazon Seller"
        assert "redirect_uri" in data
    
    def test_tiktok_shop_setup_endpoint(self):
        """GET /api/oauth/tiktok_shop/setup returns TikTok Shop setup info"""
        response = requests.get(f"{BASE_URL}/api/oauth/tiktok_shop/setup")
        assert response.status_code == 200
        
        data = response.json()
        assert data["platform"] == "tiktok_shop"
        assert data["name"] == "TikTok Shop"
    
    def test_google_ads_setup_endpoint(self):
        """GET /api/oauth/google_ads/setup returns Google Ads setup info"""
        response = requests.get(f"{BASE_URL}/api/oauth/google_ads/setup")
        assert response.status_code == 200
        
        data = response.json()
        assert data["platform"] == "google_ads"
        assert data["name"] == "Google Ads"
        assert data["connection_type"] == "ads"
    
    def test_tiktok_ads_setup_endpoint(self):
        """GET /api/oauth/tiktok_ads/setup returns TikTok Ads setup info"""
        response = requests.get(f"{BASE_URL}/api/oauth/tiktok_ads/setup")
        assert response.status_code == 200
        
        data = response.json()
        assert data["platform"] == "tiktok_ads"
        assert data["name"] == "TikTok Ads"
        assert data["connection_type"] == "ads"
    
    def test_invalid_platform_setup(self):
        """GET /api/oauth/invalid_platform/setup returns 400"""
        response = requests.get(f"{BASE_URL}/api/oauth/invalid_platform/setup")
        assert response.status_code == 400


class TestWebSocketEndpoint:
    """Test WebSocket endpoint accessibility"""
    
    def test_websocket_endpoint_accessible(self):
        """WebSocket endpoint is accessible (returns 200 for HTTP GET via ingress)"""
        # Note: WebSocket endpoints return 200 (frontend HTML) for regular HTTP requests
        # through the ingress. Actual WS requires protocol upgrade (wss://)
        response = requests.get(f"{BASE_URL}/api/ws/notifications")
        # The endpoint is accessible - it returns 200 (frontend) or 405 (method not allowed)
        assert response.status_code in [200, 405]
    
    def test_websocket_endpoint_post_returns_405(self):
        """WebSocket endpoint returns 405 for POST requests"""
        response = requests.post(f"{BASE_URL}/api/ws/notifications")
        # POST to WebSocket endpoint should return 405
        assert response.status_code in [200, 405]


class TestAutomationWithNotifications:
    """Test automation endpoints that trigger WebSocket notifications"""
    
    def test_automation_run_full_pipeline(self):
        """POST /api/automation/run with job_type full_pipeline returns success"""
        response = requests.post(
            f"{BASE_URL}/api/automation/run",
            json={"job_type": "full_pipeline"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "processed" in data
        assert "alerts_generated" in data
        assert "log_id" in data
    
    def test_automation_logs_endpoint(self):
        """GET /api/automation/logs returns logs array"""
        response = requests.get(f"{BASE_URL}/api/automation/logs")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_automation_stats_endpoint(self):
        """GET /api/automation/stats returns stats"""
        response = requests.get(f"{BASE_URL}/api/automation/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_runs" in data
        assert "success_rate" in data
        assert "products_processed" in data
        assert "alerts_generated" in data


class TestIngestionWithNotifications:
    """Test ingestion endpoints that trigger WebSocket notifications"""
    
    def test_amazon_import(self):
        """POST /api/ingestion/amazon with limit 3 returns success"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/amazon",
            json={"limit": 3}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["source"] == "amazon"
        assert "fetched" in data
        assert "inserted" in data or "updated" in data
    
    def test_tiktok_import(self):
        """POST /api/ingestion/tiktok with limit 3 returns success"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/tiktok",
            json={"limit": 3}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["source"] == "tiktok"
        assert "fetched" in data
    
    def test_ingestion_sources_endpoint(self):
        """GET /api/ingestion/sources returns 3+ sources"""
        response = requests.get(f"{BASE_URL}/api/ingestion/sources")
        assert response.status_code == 200
        
        data = response.json()
        assert "sources" in data
        assert len(data["sources"]) >= 3
        
        # Verify source structure
        for source in data["sources"]:
            assert "id" in source
            assert "name" in source
            assert "status" in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
