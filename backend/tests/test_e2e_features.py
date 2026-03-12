"""
End-to-End Tests for TrendScout E-Commerce Intelligence Platform

Tests for:
1. Public SEO Pages (no auth required)
2. Zendrop Supplier Integration in Data Enrichment Pipeline
3. Smart Budget Optimizer V2 (presets, auto-recommend, settings)
4. Integration Health Endpoint with Zendrop entry
"""

import pytest
import requests
import os
import random
import string

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test user credentials
TEST_EMAIL = "jenkinslisa1978@gmail.com"
TEST_PASSWORD = "Test123!"


class TestPublicSEOEndpoints:
    """Test public endpoints - no auth required"""
    
    def test_trending_products_returns_200(self):
        """GET /api/public/trending-products should return 200 without auth"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "products" in data, "Response should contain 'products' array"
        assert "total" in data, "Response should contain 'total' count"
        assert "detected_this_week" in data, "Response should contain 'detected_this_week' count"
        
        # Validate products array structure
        if len(data["products"]) > 0:
            product = data["products"][0]
            required_fields = ["id", "slug", "product_name", "launch_score", "trend_stage", "margin_percent"]
            for field in required_fields:
                assert field in product, f"Product should have '{field}' field"
            print(f"✓ Trending products endpoint returned {len(data['products'])} products")
        
        return data
    
    def test_trending_products_has_radar_badges(self):
        """Products should include radar_detected status for badge display"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products")
        assert response.status_code == 200
        
        data = response.json()
        if len(data["products"]) > 0:
            # Check if any product has radar_detected field
            has_radar_field = any("radar_detected" in p for p in data["products"])
            assert has_radar_field, "Products should include 'radar_detected' field for badges"
            print("✓ Products include radar_detected field for badges")
    
    def test_product_detail_by_slug(self):
        """GET /api/public/product/{slug} should return product detail without auth"""
        # First get a valid slug from trending products
        trending = requests.get(f"{BASE_URL}/api/public/trending-products")
        assert trending.status_code == 200
        products = trending.json().get("products", [])
        
        if len(products) == 0:
            pytest.skip("No products available for testing")
        
        slug = products[0]["slug"]
        response = requests.get(f"{BASE_URL}/api/public/product/{slug}")
        assert response.status_code == 200, f"Expected 200 for slug '{slug}', got {response.status_code}"
        
        data = response.json()
        assert "id" in data, "Product detail should have 'id'"
        assert "product_name" in data, "Product detail should have 'product_name'"
        assert "launch_score" in data, "Product detail should have 'launch_score'"
        assert "margin_percent" in data, "Product detail should have 'margin_percent'"
        assert "trend_stage" in data, "Product detail should have 'trend_stage'"
        print(f"✓ Product detail returned for slug '{slug}'")
    
    def test_product_detail_has_related_products(self):
        """Product detail should include related products for cross-linking"""
        trending = requests.get(f"{BASE_URL}/api/public/trending-products")
        products = trending.json().get("products", [])
        
        if len(products) == 0:
            pytest.skip("No products available")
        
        slug = products[0]["slug"]
        response = requests.get(f"{BASE_URL}/api/public/product/{slug}")
        data = response.json()
        
        assert "related_products" in data, "Product detail should include 'related_products'"
        print(f"✓ Product detail includes {len(data.get('related_products', []))} related products")
    
    def test_product_detail_404_for_invalid_slug(self):
        """GET /api/public/product/{invalid-slug} should return 404"""
        response = requests.get(f"{BASE_URL}/api/public/product/nonexistent-product-slug-xyz-123")
        assert response.status_code == 404, f"Expected 404 for invalid slug, got {response.status_code}"
        print("✓ Invalid slug returns 404 as expected")


class TestAuthentication:
    """Test authentication for protected endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get JWT token for authenticated requests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        
        data = response.json()
        token = data.get("session", {}).get("access_token") or data.get("access_token") or data.get("token")
        if not token:
            pytest.skip(f"No token in response: {data}")
        return token
    
    def test_login_success(self):
        """POST /api/auth/login should return token for valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        # Check for token in various possible response structures
        has_token = (
            data.get("session", {}).get("access_token") or 
            data.get("access_token") or 
            data.get("token")
        )
        assert has_token, f"Response should contain access token: {data}"
        print("✓ Login successful, token received")
        return has_token


class TestOptimizerV2Endpoints:
    """Test Smart Budget Optimizer V2 endpoints"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for protected requests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        
        data = response.json()
        token = data.get("session", {}).get("access_token") or data.get("access_token") or data.get("token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_presets(self, auth_headers):
        """GET /api/optimization/presets should return presets"""
        response = requests.get(
            f"{BASE_URL}/api/optimization/presets",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "presets" in data, "Response should contain 'presets'"
        
        # Presets can be dict or list
        presets = data["presets"]
        if isinstance(presets, dict):
            assert len(presets) > 0, "Should have at least one preset"
            # Validate preset structure from dict
            preset_keys = list(presets.keys())
            assert "balanced" in preset_keys, "Should include 'balanced' preset"
            print(f"✓ Got {len(presets)} optimizer presets: {preset_keys}")
        else:
            assert isinstance(presets, list), "'presets' should be a list or dict"
            assert len(presets) > 0, "Should have at least one preset"
            preset = presets[0]
            assert "id" in preset or "name" in preset, "Preset should have 'id' or 'name'"
            print(f"✓ Got {len(presets)} optimizer presets")
    
    def test_set_preset(self, auth_headers):
        """POST /api/optimization/set-preset should update user preset"""
        # Set preset to 'balanced'
        response = requests.post(
            f"{BASE_URL}/api/optimization/set-preset",
            headers=auth_headers,
            json={"preset": "balanced"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success", f"Expected status 'success', got {data}"
        assert data.get("preset") == "balanced", f"Expected preset 'balanced', got {data.get('preset')}"
        print("✓ Preset set successfully to 'balanced'")
    
    def test_set_invalid_preset(self, auth_headers):
        """POST /api/optimization/set-preset with invalid preset should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/optimization/set-preset",
            headers=auth_headers,
            json={"preset": "invalid_preset_name"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid preset, got {response.status_code}"
        print("✓ Invalid preset correctly rejected with 400")
    
    def test_toggle_auto_recommend(self, auth_headers):
        """POST /api/optimization/toggle-auto-recommend should toggle auto mode"""
        # Toggle to enabled
        response = requests.post(
            f"{BASE_URL}/api/optimization/toggle-auto-recommend",
            headers=auth_headers,
            json={"enabled": True}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success", f"Expected status 'success', got {data}"
        assert data.get("auto_recommend_enabled") == True, "auto_recommend_enabled should be True"
        print("✓ Auto-recommend enabled successfully")
        
        # Toggle back to disabled
        response = requests.post(
            f"{BASE_URL}/api/optimization/toggle-auto-recommend",
            headers=auth_headers,
            json={"enabled": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("auto_recommend_enabled") == False
        print("✓ Auto-recommend disabled successfully")
    
    def test_get_settings(self, auth_headers):
        """GET /api/optimization/settings should return preset and auto_recommend_enabled"""
        response = requests.get(
            f"{BASE_URL}/api/optimization/settings",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "preset" in data, "Response should contain 'preset'"
        assert "auto_recommend_enabled" in data, "Response should contain 'auto_recommend_enabled'"
        print(f"✓ Got optimizer settings: preset={data['preset']}, auto_recommend={data['auto_recommend_enabled']}")
    
    def test_settings_persistence(self, auth_headers):
        """Settings should persist across API calls"""
        # Set a specific preset
        requests.post(
            f"{BASE_URL}/api/optimization/set-preset",
            headers=auth_headers,
            json={"preset": "aggressive"}
        )
        
        # Get settings and verify
        response = requests.get(
            f"{BASE_URL}/api/optimization/settings",
            headers=auth_headers
        )
        data = response.json()
        assert data.get("preset") == "aggressive", f"Preset should be 'aggressive', got {data.get('preset')}"
        print("✓ Settings persistence verified")


class TestDataIntegrationEndpoints:
    """Test Data Integration endpoints with Zendrop"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for protected requests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        
        data = response.json()
        token = data.get("session", {}).get("access_token") or data.get("access_token") or data.get("token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_enrich_product_includes_zendrop(self, auth_headers):
        """POST /api/data-integration/enrich/{product_id} should include Zendrop in sources_status"""
        # First get a product ID
        trending = requests.get(f"{BASE_URL}/api/public/trending-products")
        products = trending.json().get("products", [])
        
        if len(products) == 0:
            pytest.skip("No products available for enrichment test")
        
        product_id = products[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/data-integration/enrich/{product_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "sources_status" in data, "Response should contain 'sources_status'"
        
        sources = data["sources_status"]
        assert "zendrop" in sources, "sources_status should include 'zendrop'"
        
        zendrop_result = sources["zendrop"]
        assert zendrop_result.get("success") == True, f"Zendrop should have success=True, got {zendrop_result}"
        assert "confidence" in zendrop_result, "Zendrop result should have 'confidence'"
        
        # In estimation mode, confidence should be 'estimated'
        print(f"✓ Product enrichment includes Zendrop with confidence={zendrop_result.get('confidence')}")
    
    def test_enrich_product_has_all_sources(self, auth_headers):
        """Enrichment should include all 5 data sources"""
        trending = requests.get(f"{BASE_URL}/api/public/trending-products")
        products = trending.json().get("products", [])
        
        if len(products) == 0:
            pytest.skip("No products available")
        
        product_id = products[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/data-integration/enrich/{product_id}",
            headers=auth_headers
        )
        data = response.json()
        
        expected_sources = ["aliexpress", "cj_dropshipping", "zendrop", "tiktok", "meta_ads"]
        sources = data.get("sources_status", {})
        
        for src in expected_sources:
            assert src in sources, f"Missing source: {src}"
            assert sources[src].get("success") == True, f"Source {src} should succeed"
        
        print(f"✓ All {len(expected_sources)} data sources present in enrichment response")
    
    def test_integration_health_includes_zendrop(self, auth_headers):
        """GET /api/data-integration/integration-health should include zendrop entry"""
        response = requests.get(
            f"{BASE_URL}/api/data-integration/integration-health",
            headers=auth_headers
        )
        # This endpoint requires admin access, might return 403
        if response.status_code == 403:
            print("✓ Integration health requires admin access (expected)")
            return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "zendrop" in data, "Integration health should include 'zendrop'"
        
        zendrop_health = data["zendrop"]
        assert "status" in zendrop_health, "Zendrop health should have 'status'"
        assert "mode" in zendrop_health, "Zendrop health should have 'mode'"
        
        # Since ZENDROP_API_KEY is not set, should be in estimation mode
        expected_mode = "estimation"
        assert zendrop_health.get("mode") == expected_mode, f"Expected mode '{expected_mode}', got {zendrop_health.get('mode')}"
        print(f"✓ Integration health shows Zendrop status={zendrop_health.get('status')}, mode={zendrop_health.get('mode')}")
    
    def test_source_health_endpoint(self, auth_headers):
        """GET /api/data-integration/source-health should return source pull logs"""
        response = requests.get(
            f"{BASE_URL}/api/data-integration/source-health",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "sources" in data, "Response should contain 'sources' array"
        print(f"✓ Source health returned {len(data.get('sources', []))} source entries")


class TestDashboardEndpoints:
    """Test Dashboard API endpoints"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for protected requests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        
        data = response.json()
        token = data.get("session", {}).get("access_token") or data.get("access_token") or data.get("token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_dashboard_summary(self, auth_headers):
        """GET /api/dashboard/summary should return dashboard summary"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/summary",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Dashboard summary endpoint accessible")
    
    def test_dashboard_daily_winners(self, auth_headers):
        """GET /api/dashboard/daily-winners should return top products"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/daily-winners",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Dashboard daily winners endpoint accessible")
    
    def test_user_onboarding_status(self, auth_headers):
        """GET /api/user/onboarding-status should return onboarding state"""
        response = requests.get(
            f"{BASE_URL}/api/user/onboarding-status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "onboarding_completed" in data, "Response should contain 'onboarding_completed'"
        print(f"✓ Onboarding status: completed={data.get('onboarding_completed')}")


class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("✓ API health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
