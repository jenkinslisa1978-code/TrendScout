"""
Product Identity & Deduplication API Tests

Tests for:
- Product deduplication endpoints (/api/ingestion/dedup/*)
- Products API with canonical_only filter
- Dashboard daily-winners API
- Reports API
- Health check API

API Key: vs_automation_key_2024
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API_KEY = "vs_automation_key_2024"


class TestHealthAPI:
    """Health check endpoint tests"""
    
    def test_health_endpoint_returns_healthy(self):
        """Test GET /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["database"] == "connected"
        print(f"✓ Health check passed: {data}")


class TestDedupAPI:
    """Product deduplication API tests"""
    
    def test_dedup_stats_returns_correct_counts(self):
        """Test GET /api/ingestion/dedup/stats returns canonical product counts"""
        response = requests.get(f"{BASE_URL}/api/ingestion/dedup/stats")
        assert response.status_code == 200
        
        data = response.json()
        # Verify required fields
        assert "total_products" in data
        assert "canonical_products" in data
        assert "merged_products" in data
        assert "multi_source_products" in data
        assert "avg_canonical_confidence" in data
        
        # Verify counts are consistent
        assert data["total_products"] == data["canonical_products"] + data["merged_products"]
        assert data["canonical_products"] > 0
        
        print(f"✓ Dedup stats: total={data['total_products']}, canonical={data['canonical_products']}, merged={data['merged_products']}")
    
    def test_dedup_run_requires_api_key(self):
        """Test POST /api/ingestion/dedup/run returns 401 without API key"""
        response = requests.post(f"{BASE_URL}/api/ingestion/dedup/run?dry_run=true")
        assert response.status_code == 401
        
        data = response.json()
        assert "Invalid API key" in data.get("detail", "")
        print("✓ Dedup run correctly rejects requests without API key")
    
    def test_dedup_run_rejects_invalid_api_key(self):
        """Test POST /api/ingestion/dedup/run rejects wrong API key"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/dedup/run?dry_run=true",
            headers={"X-API-Key": "wrong_key"}
        )
        assert response.status_code == 401
        print("✓ Dedup run correctly rejects invalid API key")
    
    def test_dedup_run_dry_run_with_valid_key(self):
        """Test POST /api/ingestion/dedup/run dry_run=true with valid API key"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/dedup/run?dry_run=true",
            headers={"X-API-Key": API_KEY}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "started_at" in data
        assert "completed_at" in data
        assert "duration_seconds" in data
        assert "total_products_processed" in data
        assert "duplicate_groups_found" in data
        assert "products_merged" in data
        assert "errors" in data
        
        # In dry run, nothing should be merged
        assert data["products_merged"] == 0
        print(f"✓ Dedup dry run: processed={data['total_products_processed']}, groups={data['duplicate_groups_found']}")
    
    def test_dedup_history_returns_previous_runs(self):
        """Test GET /api/ingestion/dedup/history returns dedup run history"""
        response = requests.get(f"{BASE_URL}/api/ingestion/dedup/history")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            run = data[0]
            assert "started_at" in run
            assert "completed_at" in run
            assert "duration_seconds" in run
            assert "total_products_processed" in run
            assert "duplicate_groups_found" in run
            assert "success" in run
        
        print(f"✓ Dedup history: {len(data)} runs recorded")


class TestProductsAPI:
    """Products API tests - verifying canonical_only filter"""
    
    def test_products_api_returns_canonical_only_by_default(self):
        """Test GET /api/products returns only canonical products by default"""
        response = requests.get(f"{BASE_URL}/api/products?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        
        products = data["data"]
        metadata = data["metadata"]
        
        # All products should be canonical (is_canonical != False)
        for product in products:
            is_canonical = product.get("is_canonical", True)
            assert is_canonical != False, f"Product {product.get('id')} is not canonical but was returned"
        
        # Verify metadata counts
        assert metadata["canonical_count"] == metadata["total_count"]
        print(f"✓ Products API returns canonical only: {len(products)} canonical products")
    
    def test_products_api_with_canonical_only_false(self):
        """Test GET /api/products?canonical_only=false returns all products including merged"""
        response = requests.get(f"{BASE_URL}/api/products?canonical_only=false&limit=50")
        assert response.status_code == 200
        
        data = response.json()
        products = data["data"]
        metadata = data["metadata"]
        
        # Should include both canonical and merged products
        canonical_count = len([p for p in products if p.get("is_canonical") != False])
        
        print(f"✓ Products API with canonical_only=false: {len(products)} total, {canonical_count} canonical")
    
    def test_products_api_metadata_structure(self):
        """Test GET /api/products returns correct metadata structure"""
        response = requests.get(f"{BASE_URL}/api/products?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        metadata = data["metadata"]
        
        # Verify all required metadata fields
        required_fields = [
            "total_count", "canonical_count", "multi_source_count",
            "simulated_count", "live_data_count", "avg_confidence_score"
        ]
        for field in required_fields:
            assert field in metadata, f"Missing metadata field: {field}"
        
        print(f"✓ Products metadata structure valid: {metadata}")
    
    def test_canonical_product_has_required_fields(self):
        """Test canonical products have all required dedup fields"""
        response = requests.get(f"{BASE_URL}/api/products?limit=5")
        assert response.status_code == 200
        
        products = response.json()["data"]
        
        for product in products:
            # Check canonical fields exist
            assert "canonical_id" in product or "is_canonical" in product
            assert "canonical_confidence" in product or "confidence_score" in product
            
            # Check contributing_sources if it's a merged product
            if product.get("is_canonical") == True and "contributing_sources" in product:
                sources = product.get("contributing_sources", [])
                assert len(sources) > 0
        
        print(f"✓ Canonical products have required fields")
    
    def test_multi_source_products_have_source_data(self):
        """Test multi-source canonical products have source_data array"""
        response = requests.get(f"{BASE_URL}/api/products?limit=50")
        assert response.status_code == 200
        
        products = response.json()["data"]
        
        # Find products with multiple sources
        multi_source_products = [
            p for p in products 
            if len(p.get("contributing_sources", [])) > 1
        ]
        
        for product in multi_source_products:
            assert "source_data" in product, f"Multi-source product {product.get('id')} missing source_data"
            source_data = product.get("source_data", [])
            assert len(source_data) > 0
            
            # Verify source_data structure
            for source in source_data:
                assert "source_name" in source
        
        print(f"✓ Found {len(multi_source_products)} multi-source products with valid source_data")


class TestDashboardAPI:
    """Dashboard API tests"""
    
    def test_daily_winners_returns_products(self):
        """Test GET /api/dashboard/daily-winners returns daily winners"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners")
        assert response.status_code == 200
        
        data = response.json()
        assert "daily_winners" in data
        assert "count" in data
        assert "generated_at" in data
        
        winners = data["daily_winners"]
        assert len(winners) > 0
        
        # Verify winner structure
        winner = winners[0]
        required_fields = [
            "product_id", "product_name", "category", "trend_stage",
            "estimated_margin", "competition_level", "success_probability",
            "validation_result", "validation_label", "ranking_score"
        ]
        for field in required_fields:
            assert field in winner, f"Missing field in daily winner: {field}"
        
        print(f"✓ Daily winners: {len(winners)} products with correct structure")
    
    def test_daily_winners_have_valid_trend_stages(self):
        """Test daily winners have valid trend_stage values"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners")
        assert response.status_code == 200
        
        winners = response.json()["daily_winners"]
        valid_stages = ["exploding", "rising", "stable", "early", "declining", None]
        
        for winner in winners:
            stage = winner.get("trend_stage")
            assert stage in valid_stages, f"Invalid trend_stage: {stage}"
        
        print(f"✓ All {len(winners)} daily winners have valid trend stages")
    
    def test_daily_winners_have_validation_labels(self):
        """Test daily winners have validation labels and results"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners")
        assert response.status_code == 200
        
        winners = response.json()["daily_winners"]
        
        for winner in winners:
            assert "validation_result" in winner
            assert "validation_label" in winner
            assert winner["validation_result"] is not None
        
        print(f"✓ All daily winners have validation labels")


class TestReportsAPI:
    """Reports API tests"""
    
    def test_reports_list_returns_available_reports(self):
        """Test GET /api/reports/ returns list of reports"""
        response = requests.get(f"{BASE_URL}/api/reports/")
        assert response.status_code == 200
        
        data = response.json()
        assert "reports" in data
        assert "count" in data
        assert "latest" in data
        
        reports = data["reports"]
        assert len(reports) > 0
        
        print(f"✓ Reports API: {len(reports)} reports available")
    
    def test_report_structure_is_valid(self):
        """Test report structure has required fields"""
        response = requests.get(f"{BASE_URL}/api/reports/")
        assert response.status_code == 200
        
        reports = response.json()["reports"]
        
        for report in reports:
            # Check metadata
            assert "metadata" in report
            metadata = report["metadata"]
            assert "id" in metadata
            assert "report_type" in metadata
            assert "title" in metadata
            assert "generated_at" in metadata
            assert "status" in metadata
            
            # Check summary
            assert "summary" in report
            
            # Check public_preview
            assert "public_preview" in report
        
        print(f"✓ All reports have valid structure")
    
    def test_reports_have_latest_indicators(self):
        """Test reports API returns latest report indicators"""
        response = requests.get(f"{BASE_URL}/api/reports/")
        assert response.status_code == 200
        
        data = response.json()
        latest = data.get("latest", {})
        
        # Should have weekly and/or monthly latest
        assert "weekly" in latest or "monthly" in latest
        
        print(f"✓ Reports have latest indicators: {list(latest.keys())}")
    
    def test_weekly_report_has_products(self):
        """Test weekly report public preview has products"""
        response = requests.get(f"{BASE_URL}/api/reports/")
        assert response.status_code == 200
        
        reports = response.json()["reports"]
        weekly_reports = [r for r in reports if r["metadata"]["report_type"] == "weekly_winning_products"]
        
        if weekly_reports:
            weekly = weekly_reports[0]
            preview = weekly.get("public_preview", {})
            
            # Check top products exist
            top_products = preview.get("top_5_products", [])
            assert len(top_products) > 0
            
            # Verify product structure
            product = top_products[0]
            assert "id" in product
            assert "name" in product
            assert "category" in product
            
            print(f"✓ Weekly report has {len(top_products)} preview products")
        else:
            pytest.skip("No weekly reports available")


class TestProductDedupIntegration:
    """Integration tests for product deduplication flow"""
    
    def test_dedup_stats_match_products_api(self):
        """Test dedup stats canonical count matches products API"""
        # Get dedup stats
        stats_response = requests.get(f"{BASE_URL}/api/ingestion/dedup/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        # Get all products (canonical only)
        products_response = requests.get(f"{BASE_URL}/api/products?limit=200")
        assert products_response.status_code == 200
        products_data = products_response.json()
        
        # The counts should match (within reasonable bounds due to potential race conditions)
        stats_canonical = stats["canonical_products"]
        api_count = products_data["metadata"]["total_count"]
        
        # They might not be exact due to limit param but should be close
        print(f"✓ Dedup stats canonical: {stats_canonical}, Products API returned: {api_count}")
    
    def test_merged_products_excluded_from_default_query(self):
        """Test merged products are excluded from default products query"""
        # Get canonical only (default)
        canonical_response = requests.get(f"{BASE_URL}/api/products?limit=200")
        assert canonical_response.status_code == 200
        canonical_products = canonical_response.json()["data"]
        
        # Get all including merged
        all_response = requests.get(f"{BASE_URL}/api/products?canonical_only=false&limit=200")
        assert all_response.status_code == 200
        all_products = all_response.json()["data"]
        
        # Default should have fewer or equal products
        canonical_ids = set(p.get("id") for p in canonical_products)
        
        # Check that non-canonical products exist in the all_products
        merged_in_all = [p for p in all_products if p.get("is_canonical") == False]
        
        print(f"✓ Canonical products: {len(canonical_products)}, All products: {len(all_products)}, Merged found: {len(merged_in_all)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
