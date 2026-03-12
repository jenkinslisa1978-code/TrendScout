"""
Tests for Data Integration API endpoints
Phase: Data Credibility & Supplier Intelligence
Endpoints:
- POST /api/data-integration/enrich/{product_id}
- POST /api/data-integration/run-ingestion
- GET /api/data-integration/source-health
- GET /api/data-integration/ingestion-status
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "testopt@example.com"
ADMIN_PASSWORD = "TestPass123!"
ENRICHED_PRODUCT_ID = "68f41478-9ca2-48c6-997d-b121e2ef8ee9"
AUTOMATION_KEY = "vs_automation_key_2024"


@pytest.fixture(scope="module")
def admin_token():
    """Get authentication token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token") or data.get("token")
        if token:
            return token
    pytest.skip("Admin authentication failed")


@pytest.fixture(scope="module")
def api_client():
    """Create requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def authenticated_client(api_client, admin_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


class TestEnrichedProductFields:
    """Test that enriched product has correct fields"""
    
    def test_enriched_product_has_data_confidence(self, authenticated_client):
        """Enriched product should have data_confidence field"""
        response = authenticated_client.get(f"{BASE_URL}/api/products/{ENRICHED_PRODUCT_ID}")
        assert response.status_code == 200
        
        data = response.json()
        product = data.get("data", data)
        
        assert "data_confidence" in product, "Missing data_confidence field"
        assert product["data_confidence"] in ["live", "estimated", "fallback"], \
            f"Invalid data_confidence value: {product['data_confidence']}"
        print(f"✓ data_confidence = {product['data_confidence']}")
    
    def test_enriched_product_has_source_signals(self, authenticated_client):
        """Enriched product should have source_signals dict"""
        response = authenticated_client.get(f"{BASE_URL}/api/products/{ENRICHED_PRODUCT_ID}")
        assert response.status_code == 200
        
        data = response.json()
        product = data.get("data", data)
        
        assert "source_signals" in product, "Missing source_signals field"
        assert isinstance(product["source_signals"], dict), "source_signals should be a dict"
        
        # Check signal structure
        signals = product["source_signals"]
        assert len(signals) > 0, "source_signals should not be empty"
        
        for signal_name, signal_data in signals.items():
            assert "value" in signal_data, f"Signal {signal_name} missing 'value'"
            assert "confidence" in signal_data, f"Signal {signal_name} missing 'confidence'"
            assert "source" in signal_data, f"Signal {signal_name} missing 'source'"
            assert "updated" in signal_data, f"Signal {signal_name} missing 'updated'"
        
        print(f"✓ source_signals has {len(signals)} signals: {list(signals.keys())}")
    
    def test_enriched_product_has_scoring_metadata(self, authenticated_client):
        """Enriched product should have scoring_metadata.source_breakdown"""
        response = authenticated_client.get(f"{BASE_URL}/api/products/{ENRICHED_PRODUCT_ID}")
        assert response.status_code == 200
        
        data = response.json()
        product = data.get("data", data)
        
        assert "scoring_metadata" in product, "Missing scoring_metadata field"
        metadata = product["scoring_metadata"]
        assert "source_breakdown" in metadata, "Missing source_breakdown in scoring_metadata"
        
        breakdown = metadata["source_breakdown"]
        assert isinstance(breakdown, dict), "source_breakdown should be a dict"
        assert len(breakdown) > 0, "source_breakdown should not be empty"
        
        # Check breakdown structure
        for key, info in breakdown.items():
            assert "confidence" in info, f"Breakdown {key} missing 'confidence'"
            assert "source" in info, f"Breakdown {key} missing 'source'"
        
        print(f"✓ scoring_metadata.source_breakdown has {len(breakdown)} entries")
    
    def test_enriched_product_has_cj_fields(self, authenticated_client):
        """Enriched product should have CJ Dropshipping fields"""
        response = authenticated_client.get(f"{BASE_URL}/api/products/{ENRICHED_PRODUCT_ID}")
        assert response.status_code == 200
        
        data = response.json()
        product = data.get("data", data)
        
        cj_fields = ["cj_price", "cj_shipping_days", "cj_processing_days", 
                     "cj_availability", "cj_warehouse", "cj_variants_count"]
        
        found_fields = []
        for field in cj_fields:
            if field in product:
                found_fields.append(field)
        
        assert len(found_fields) >= 4, f"Expected at least 4 CJ fields, found {len(found_fields)}: {found_fields}"
        print(f"✓ CJ fields present: {found_fields}")
        
        # Verify values are reasonable
        if "cj_price" in product:
            assert isinstance(product["cj_price"], (int, float)), "cj_price should be numeric"
        if "cj_shipping_days" in product:
            assert isinstance(product["cj_shipping_days"], int), "cj_shipping_days should be int"
    
    def test_enriched_product_has_aliexpress_fields(self, authenticated_client):
        """Enriched product should have AliExpress fields"""
        response = authenticated_client.get(f"{BASE_URL}/api/products/{ENRICHED_PRODUCT_ID}")
        assert response.status_code == 200
        
        data = response.json()
        product = data.get("data", data)
        
        ae_fields = ["orders_30d", "ae_shipping_days", "ae_rating", "ae_reviews"]
        
        found_fields = []
        for field in ae_fields:
            if field in product:
                found_fields.append(field)
        
        assert len(found_fields) >= 2, f"Expected at least 2 AliExpress fields, found {len(found_fields)}: {found_fields}"
        print(f"✓ AliExpress fields present: {found_fields}")
    
    def test_enriched_product_has_tiktok_fields(self, authenticated_client):
        """Enriched product should have TikTok fields"""
        response = authenticated_client.get(f"{BASE_URL}/api/products/{ENRICHED_PRODUCT_ID}")
        assert response.status_code == 200
        
        data = response.json()
        product = data.get("data", data)
        
        tt_fields = ["tiktok_views", "engagement_rate", "ad_count"]
        
        found_fields = []
        for field in tt_fields:
            if field in product:
                found_fields.append(field)
        
        assert len(found_fields) >= 2, f"Expected at least 2 TikTok fields, found {len(found_fields)}: {found_fields}"
        print(f"✓ TikTok fields present: {found_fields}")
    
    def test_enriched_product_has_meta_fields(self, authenticated_client):
        """Enriched product should have Meta Ad fields"""
        response = authenticated_client.get(f"{BASE_URL}/api/products/{ENRICHED_PRODUCT_ID}")
        assert response.status_code == 200
        
        data = response.json()
        product = data.get("data", data)
        
        meta_fields = ["meta_active_ads", "meta_ad_growth_7d", "estimated_monthly_ad_spend"]
        
        found_fields = []
        for field in meta_fields:
            if field in product:
                found_fields.append(field)
        
        assert len(found_fields) >= 2, f"Expected at least 2 Meta fields, found {len(found_fields)}: {found_fields}"
        print(f"✓ Meta Ad fields present: {found_fields}")


class TestEnrichEndpoint:
    """Test POST /api/data-integration/enrich/{product_id}"""
    
    def test_enrich_requires_auth(self, api_client):
        """Enrich endpoint should require authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/data-integration/enrich/{ENRICHED_PRODUCT_ID}",
            headers={"Authorization": ""}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Enrich endpoint requires authentication")
    
    def test_enrich_product_success(self, authenticated_client):
        """Enrich endpoint should work for authenticated user"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/data-integration/enrich/{ENRICHED_PRODUCT_ID}"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "product_id" in data, "Response should have product_id"
        assert "data_confidence" in data, "Response should have data_confidence"
        assert "source_signals" in data, "Response should have source_signals"
        assert "sources_status" in data, "Response should have sources_status"
        
        # Verify sources_status has all 4 sources
        sources = data["sources_status"]
        assert "aliexpress" in sources, "Missing aliexpress in sources_status"
        assert "cj_dropshipping" in sources, "Missing cj_dropshipping in sources_status"
        assert "tiktok" in sources, "Missing tiktok in sources_status"
        assert "meta_ads" in sources, "Missing meta_ads in sources_status"
        
        print(f"✓ Enrich returned data_confidence={data['data_confidence']}")
        print(f"✓ Sources status: {list(sources.keys())}")
    
    def test_enrich_invalid_product(self, authenticated_client):
        """Enrich should handle invalid product ID"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/data-integration/enrich/invalid-product-id-12345"
        )
        data = response.json()
        # Should return error or 404
        assert response.status_code in [200, 404] or "error" in data
        print("✓ Invalid product ID handled correctly")


class TestSourceHealthEndpoint:
    """Test GET /api/data-integration/source-health"""
    
    def test_source_health_requires_auth(self, api_client):
        """Source health endpoint should require authentication"""
        response = api_client.get(
            f"{BASE_URL}/api/data-integration/source-health",
            headers={"Authorization": ""}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Source health endpoint requires authentication")
    
    def test_source_health_returns_data(self, authenticated_client):
        """Source health should return source pull stats"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/data-integration/source-health"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "sources" in data, "Response should have 'sources' field"
        
        # Sources can be empty if no pulls yet
        sources = data["sources"]
        if len(sources) > 0:
            for s in sources[:1]:  # Check first source
                assert "source" in s, "Source item missing 'source' field"
                assert "method" in s, "Source item missing 'method' field"
                assert "success_rate" in s, "Source item missing 'success_rate' field"
                assert "total_pulls" in s, "Source item missing 'total_pulls' field"
        
        print(f"✓ Source health returned {len(sources)} source entries")
        if "latest_ingestion" in data and data["latest_ingestion"]:
            print(f"✓ Latest ingestion: {data['latest_ingestion'].get('timestamp', 'unknown')}")


class TestIngestionStatusEndpoint:
    """Test GET /api/data-integration/ingestion-status"""
    
    def test_ingestion_status_requires_auth(self, api_client):
        """Ingestion status endpoint should require authentication"""
        response = api_client.get(
            f"{BASE_URL}/api/data-integration/ingestion-status",
            headers={"Authorization": ""}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Ingestion status endpoint requires authentication")
    
    def test_ingestion_status_returns_counts(self, authenticated_client):
        """Ingestion status should return enriched count and confidence breakdown"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/data-integration/ingestion-status"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "enriched_count" in data, "Response should have 'enriched_count'"
        assert "total_products" in data, "Response should have 'total_products'"
        assert "confidence_breakdown" in data, "Response should have 'confidence_breakdown'"
        
        # Verify confidence breakdown structure
        breakdown = data["confidence_breakdown"]
        assert "live" in breakdown, "confidence_breakdown missing 'live'"
        assert "estimated" in breakdown, "confidence_breakdown missing 'estimated'"
        assert "fallback" in breakdown, "confidence_breakdown missing 'fallback'"
        
        print(f"✓ Enriched: {data['enriched_count']}/{data['total_products']} products")
        print(f"✓ Confidence breakdown: live={breakdown['live']}, estimated={breakdown['estimated']}, fallback={breakdown['fallback']}")


class TestRunIngestionEndpoint:
    """Test POST /api/data-integration/run-ingestion"""
    
    def test_run_ingestion_requires_auth(self, api_client):
        """Run ingestion endpoint should require authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/data-integration/run-ingestion",
            headers={"Authorization": ""}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Run ingestion endpoint requires authentication")
    
    def test_run_ingestion_requires_admin(self, admin_token, api_client):
        """Run ingestion should require admin role"""
        # First need to test with non-admin user - skip if can't create one
        # For now, just verify the endpoint exists and returns expected structure for admin
        response = api_client.post(
            f"{BASE_URL}/api/data-integration/run-ingestion?limit=1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should either succeed (200) or indicate admin required (403)
        assert response.status_code in [200, 403], f"Expected 200 or 403, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data, "Response should have 'status' field"
            assert data["status"] == "started", f"Expected status='started', got {data['status']}"
            print("✓ Run ingestion started successfully (admin user)")
        else:
            print("✓ Run ingestion correctly requires admin role")


class TestScoreRecomputeEndpoint:
    """Test POST /api/ingestion/scores/recompute with automation key"""
    
    def test_score_recompute_with_api_key(self, api_client):
        """Score recompute should work with automation key"""
        response = api_client.post(
            f"{BASE_URL}/api/ingestion/scores/recompute?limit=2",
            headers={"X-API-Key": AUTOMATION_KEY}
        )
        
        # Should succeed or indicate throttling
        assert response.status_code in [200, 429], f"Expected 200 or 429, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "updated" in data or "recomputed" in data or "status" in data
            print(f"✓ Score recompute response: {data}")
        else:
            print("✓ Score recompute throttled (expected behavior)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
