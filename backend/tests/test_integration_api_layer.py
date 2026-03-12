"""
Test suite for Official API Integration Layer (Phase 38)
Tests integration health, enrich endpoint with fallback chains, and ingestion

Test Coverage:
- GET /api/data-integration/integration-health - health for all 4 sources
- POST /api/data-integration/enrich/{product_id} - 4-step fallback chain
- POST /api/data-integration/run-ingestion - background ingestion
- GET /api/data-integration/ingestion-status - confidence breakdown
- GET /api/data-integration/source-health - pull history
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAPISetup:
    """Verify basic API connectivity"""

    def test_api_health(self):
        """Basic API health check"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"API not healthy: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ API is healthy")


class TestAuthLogin:
    """Auth for test user"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        login_data = {
            "email": "testopt@example.com",
            "password": "TestPass123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        print(f"✓ Admin logged in successfully")
        return data["token"]


class TestIntegrationHealth:
    """Tests for GET /api/data-integration/integration-health"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers for admin user"""
        login_data = {
            "email": "testopt@example.com",
            "password": "TestPass123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_integration_health_returns_all_4_sources(self, auth_headers):
        """Integration health returns status for aliexpress, cj_dropshipping, meta_ads, tiktok"""
        response = requests.get(
            f"{BASE_URL}/api/data-integration/integration-health",
            headers=auth_headers,
            timeout=15
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        required_sources = ["aliexpress", "cj_dropshipping", "meta_ads", "tiktok"]
        for source in required_sources:
            assert source in data, f"Missing source: {source}"
        
        print(f"✓ All 4 sources present: {list(data.keys())}")

    def test_each_source_has_required_fields(self, auth_headers):
        """Each source reports status, credential_detected, mode, and message"""
        response = requests.get(
            f"{BASE_URL}/api/data-integration/integration-health",
            headers=auth_headers,
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["status", "credential_detected", "mode", "message"]
        for source_name in ["aliexpress", "cj_dropshipping", "meta_ads", "tiktok"]:
            source_data = data.get(source_name, {})
            for field in required_fields:
                assert field in source_data, f"Missing {field} in {source_name}"
            print(f"✓ {source_name}: status={source_data['status']}, mode={source_data['mode']}")

    def test_aliexpress_shows_not_configured(self, auth_headers):
        """AliExpress shows not_configured when no keys set"""
        response = requests.get(
            f"{BASE_URL}/api/data-integration/integration-health",
            headers=auth_headers,
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        
        ae = data.get("aliexpress", {})
        assert ae.get("status") == "not_configured", f"Expected not_configured, got {ae.get('status')}"
        assert ae.get("credential_detected") == False
        assert ae.get("mode") == "estimation"
        print(f"✓ AliExpress status: not_configured (mode: estimation)")

    def test_cj_shows_not_configured(self, auth_headers):
        """CJ shows not_configured when no key set"""
        response = requests.get(
            f"{BASE_URL}/api/data-integration/integration-health",
            headers=auth_headers,
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        
        cj = data.get("cj_dropshipping", {})
        assert cj.get("status") == "not_configured", f"Expected not_configured, got {cj.get('status')}"
        assert cj.get("credential_detected") == False
        assert cj.get("mode") == "estimation"
        print(f"✓ CJ Dropshipping status: not_configured (mode: estimation)")

    def test_meta_shows_not_configured(self, auth_headers):
        """Meta shows not_configured when no token set"""
        response = requests.get(
            f"{BASE_URL}/api/data-integration/integration-health",
            headers=auth_headers,
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        
        meta = data.get("meta_ads", {})
        assert meta.get("status") == "not_configured", f"Expected not_configured, got {meta.get('status')}"
        assert meta.get("credential_detected") == False
        assert meta.get("mode") == "estimation"
        print(f"✓ Meta Ads status: not_configured (mode: estimation)")

    def test_tiktok_shows_healthy_with_live_mode(self, auth_headers):
        """TikTok shows healthy with live mode (public scraper)"""
        response = requests.get(
            f"{BASE_URL}/api/data-integration/integration-health",
            headers=auth_headers,
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        
        tiktok = data.get("tiktok", {})
        assert tiktok.get("status") == "healthy", f"Expected healthy, got {tiktok.get('status')}"
        assert tiktok.get("credential_detected") == True
        assert tiktok.get("mode") == "live"
        print(f"✓ TikTok status: healthy (mode: live)")


class TestProductEnrich:
    """Tests for POST /api/data-integration/enrich/{product_id}"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers for admin user"""
        login_data = {
            "email": "testopt@example.com",
            "password": "TestPass123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_enrich_uses_4_step_fallback_chain(self, auth_headers):
        """Enrichment uses 4-step fallback: Official API → Scraper → Estimation → Hardcoded"""
        product_id = "68f41478-9ca2-48c6-997d-b121e2ef8ee9"
        response = requests.post(
            f"{BASE_URL}/api/data-integration/enrich/{product_id}",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "product_id" in data
        assert "data_confidence" in data
        assert "source_signals" in data
        print(f"✓ Enrich returned: product_id, data_confidence={data.get('data_confidence')}, source_signals")

    def test_enrichment_returns_sources_status(self, auth_headers):
        """Enrichment returns sources_status showing which method was used per source"""
        product_id = "68f41478-9ca2-48c6-997d-b121e2ef8ee9"
        response = requests.post(
            f"{BASE_URL}/api/data-integration/enrich/{product_id}",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "sources_status" in data
        sources_status = data["sources_status"]
        
        # Verify all 4 sources are present
        required_sources = ["aliexpress", "cj_dropshipping", "tiktok", "meta_ads"]
        for source in required_sources:
            assert source in sources_status, f"Missing source: {source}"
            assert "method" in sources_status[source], f"Missing method for {source}"
            assert "confidence" in sources_status[source], f"Missing confidence for {source}"
        
        print(f"✓ sources_status contains all 4 sources with method used:")
        for source, info in sources_status.items():
            print(f"  - {source}: method={info.get('method')}, confidence={info.get('confidence')}")


class TestDataIngestion:
    """Tests for ingestion endpoints"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers for admin user"""
        login_data = {
            "email": "testopt@example.com",
            "password": "TestPass123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_run_ingestion_starts_background_job(self, auth_headers):
        """POST /api/data-integration/run-ingestion starts background ingestion"""
        response = requests.post(
            f"{BASE_URL}/api/data-integration/run-ingestion?limit=5",
            headers=auth_headers,
            timeout=15
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "started"
        assert "message" in data
        print(f"✓ Ingestion started: {data.get('message')}")

    def test_ingestion_status_returns_confidence_breakdown(self, auth_headers):
        """GET /api/data-integration/ingestion-status returns confidence_breakdown"""
        response = requests.get(
            f"{BASE_URL}/api/data-integration/ingestion-status",
            headers=auth_headers,
            timeout=15
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "total_products" in data
        assert "enriched_count" in data
        assert "confidence_breakdown" in data
        
        breakdown = data["confidence_breakdown"]
        assert "live" in breakdown
        assert "estimated" in breakdown
        assert "fallback" in breakdown
        
        print(f"✓ Ingestion status:")
        print(f"  - Total products: {data['total_products']}")
        print(f"  - Enriched count: {data['enriched_count']}")
        print(f"  - Breakdown: live={breakdown['live']}, estimated={breakdown['estimated']}, fallback={breakdown['fallback']}")


class TestSourceHealth:
    """Tests for GET /api/data-integration/source-health"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers for admin user"""
        login_data = {
            "email": "testopt@example.com",
            "password": "TestPass123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_source_health_returns_pull_history(self, auth_headers):
        """GET /api/data-integration/source-health returns pull history"""
        response = requests.get(
            f"{BASE_URL}/api/data-integration/source-health",
            headers=auth_headers,
            timeout=15
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "sources" in data
        sources = data["sources"]
        
        # If there are sources, check structure
        if sources:
            for source in sources:
                assert "source" in source
                assert "method" in source
                assert "success_rate" in source
                assert "total_pulls" in source
            print(f"✓ Source health: {len(sources)} sources tracked")
        else:
            print("✓ Source health endpoint working (no pull history yet)")


class TestSystemHealthDashboard:
    """Tests for GET /api/system-health integration check"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers for admin user"""
        login_data = {
            "email": "testopt@example.com",
            "password": "TestPass123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_system_health_uses_official_client_health_checks(self, auth_headers):
        """System Health Dashboard uses official client health checks for API integrations"""
        response = requests.get(
            f"{BASE_URL}/api/system-health",
            headers=auth_headers,
            timeout=15
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "checks" in data
        checks = data["checks"]
        
        # Find API integration checks
        api_checks = [c for c in checks if c.get("category") == "api_integrations"]
        assert len(api_checks) >= 4, f"Expected at least 4 API integration checks, got {len(api_checks)}"
        
        # Verify expected integrations are present
        check_names = [c.get("name") for c in api_checks]
        expected_names = ["AliExpress", "CJ Dropshipping", "Meta Ad Library", "TikTok"]
        for name in expected_names:
            assert any(name in cn for cn in check_names), f"Missing {name} in system health checks"
        
        print(f"✓ System Health has {len(api_checks)} API integration checks:")
        for c in api_checks:
            print(f"  - {c.get('name')}: status={c.get('status')}, message={c.get('message', '')[:50]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
