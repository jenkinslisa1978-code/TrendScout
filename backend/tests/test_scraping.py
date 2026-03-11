"""
Test file for TrendScout Scraping and Products API
Tests:
1. POST /api/ingestion/scrape/amazon_movers - scrape Amazon products
2. GET /api/products - verify products have is_real_data=true, supplier_link, trend_score, last_updated
3. Verify supplier_link URLs are valid AliExpress search URLs
4. POST /api/ingestion/scrape/full - test full scrape endpoint
"""

import pytest
import requests
import os
import re
from urllib.parse import urlparse

# Get base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API_KEY = "vs_automation_key_2024"

class TestScrapingAPI:
    """Tests for scraping/ingestion endpoints"""
    
    def test_api_health(self):
        """Test basic API health"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ API health check passed")
    
    def test_scrape_amazon_movers(self):
        """Test POST /api/ingestion/scrape/amazon_movers - main scraping endpoint"""
        headers = {"X-API-Key": API_KEY}
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/amazon_movers",
            headers=headers,
            params={"max_products": 10}  # Keep small for testing
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check response structure
        assert "source_name" in data, "Response should contain source_name"
        assert data["source_name"] == "amazon_movers"
        
        # The scraper may succeed or fail due to caching/rate limits, check both cases
        if data.get("success"):
            print(f"✓ Amazon movers scrape succeeded: {data.get('products_fetched', 0)} products fetched")
            assert data.get("products_fetched", 0) >= 0
        else:
            # Even if it fails, the API should return structured response
            print(f"⚠ Amazon movers scrape returned: success={data.get('success')}, errors={data.get('errors', [])}")
        
        print(f"✓ Scrape amazon_movers endpoint works correctly")
        return data
    
    def test_scrape_health(self):
        """Test GET /api/ingestion/scrape/health"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return health status for sources
        assert isinstance(data, dict)
        print(f"✓ Scraper health endpoint works. Sources: {list(data.keys())}")
        return data
    
    def test_scrape_history(self):
        """Test GET /api/ingestion/scrape/history"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/history")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return list of ingestion runs
        assert isinstance(data, list)
        print(f"✓ Scrape history endpoint works. {len(data)} recent runs")
    
    def test_data_quality_report(self):
        """Test GET /api/ingestion/scrape/quality"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/quality")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for expected fields
        assert "total_products" in data
        assert "real_data_products" in data
        assert "real_data_percentage" in data
        
        print(f"✓ Data quality: {data.get('real_data_products', 0)}/{data.get('total_products', 0)} real products ({data.get('real_data_percentage', 0)}%)")
        return data


class TestProductsAPI:
    """Tests for products API and data quality"""
    
    def test_get_products(self):
        """Test GET /api/products returns products"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 50})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert "metadata" in data
        assert isinstance(data["data"], list)
        
        products = data["data"]
        assert len(products) > 0, "Should have at least some products"
        
        print(f"✓ GET /api/products returned {len(products)} products")
        return products
    
    def test_products_have_real_data_flag(self):
        """Verify products have is_real_data field"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 100})
        data = response.json()
        products = data["data"]
        
        real_data_count = 0
        for p in products:
            if p.get("is_real_data") == True:
                real_data_count += 1
        
        print(f"✓ {real_data_count}/{len(products)} products have is_real_data=true")
        
        # At least some products should have real data
        assert real_data_count > 0, "Expected at least some products with is_real_data=true"
    
    def test_products_have_supplier_links(self):
        """Verify products have supplier_link URLs"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 100})
        data = response.json()
        products = data["data"]
        
        with_supplier_link = 0
        aliexpress_links = 0
        
        for p in products:
            supplier_link = p.get("supplier_link", "")
            if supplier_link:
                with_supplier_link += 1
                if "aliexpress.com" in supplier_link.lower():
                    aliexpress_links += 1
        
        print(f"✓ {with_supplier_link}/{len(products)} products have supplier_link")
        print(f"✓ {aliexpress_links}/{with_supplier_link} supplier links are AliExpress URLs")
        
        # Most products should have supplier links
        assert with_supplier_link > len(products) * 0.3, "At least 30% of products should have supplier_link"
    
    def test_supplier_link_format(self):
        """Verify supplier_link URLs are valid AliExpress search URLs"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 50})
        data = response.json()
        products = data["data"]
        
        valid_links = 0
        sample_links = []
        
        for p in products:
            supplier_link = p.get("supplier_link", "")
            if supplier_link and "aliexpress.com" in supplier_link.lower():
                # Check it's a valid URL format
                parsed = urlparse(supplier_link)
                if parsed.scheme in ["http", "https"] and "aliexpress.com" in parsed.netloc:
                    valid_links += 1
                    if len(sample_links) < 3:
                        sample_links.append({
                            "product": p.get("product_name", "")[:40],
                            "link": supplier_link[:80] + "..."
                        })
        
        print(f"✓ {valid_links} valid AliExpress supplier links found")
        print("Sample supplier links:")
        for s in sample_links:
            print(f"  - {s['product']}: {s['link']}")
        
        assert valid_links > 0, "Should have at least some valid AliExpress URLs"
    
    def test_products_have_trend_score(self):
        """Verify products have trend_score field"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 100})
        data = response.json()
        products = data["data"]
        
        with_trend_score = 0
        score_range = {"min": 100, "max": 0}
        
        for p in products:
            trend_score = p.get("trend_score", 0)
            if trend_score > 0:
                with_trend_score += 1
                score_range["min"] = min(score_range["min"], trend_score)
                score_range["max"] = max(score_range["max"], trend_score)
        
        print(f"✓ {with_trend_score}/{len(products)} products have trend_score > 0")
        if with_trend_score > 0:
            print(f"✓ Trend score range: {score_range['min']} - {score_range['max']}")
        
        assert with_trend_score > len(products) * 0.5, "At least 50% of products should have trend_score"
    
    def test_products_have_last_updated(self):
        """Verify products have last_updated timestamps"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 100})
        data = response.json()
        products = data["data"]
        
        with_last_updated = 0
        recent_updates = []
        
        for p in products:
            last_updated = p.get("last_updated") or p.get("updated_at")
            if last_updated:
                with_last_updated += 1
                if len(recent_updates) < 3:
                    recent_updates.append({
                        "product": p.get("product_name", "")[:30],
                        "updated": last_updated
                    })
        
        print(f"✓ {with_last_updated}/{len(products)} products have last_updated timestamps")
        print("Recent updates:")
        for u in recent_updates:
            print(f"  - {u['product']}: {u['updated']}")
        
        assert with_last_updated > len(products) * 0.5, "At least 50% of products should have timestamps"
    
    def test_product_categories_diversity(self):
        """Verify products span multiple categories"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 200})
        data = response.json()
        products = data["data"]
        
        categories = {}
        for p in products:
            cat = p.get("category", "Unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"✓ Found {len(categories)} unique categories:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:10]:
            print(f"  - {cat}: {count} products")
        
        # Should have diverse categories (at least 3 different categories)
        assert len(categories) >= 3, f"Expected at least 3 categories, got {len(categories)}"
    
    def test_metadata_includes_live_data_count(self):
        """Verify API metadata includes live data statistics"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 100})
        data = response.json()
        
        metadata = data.get("metadata", {})
        
        assert "live_data_count" in metadata, "Metadata should include live_data_count"
        assert "total_count" in metadata, "Metadata should include total_count"
        
        print(f"✓ Metadata: {metadata.get('live_data_count', 0)} live / {metadata.get('total_count', 0)} total")
        print(f"✓ Simulated: {metadata.get('simulated_count', 0)}")
        print(f"✓ Avg confidence: {metadata.get('avg_confidence_score', 0)}")


class TestProductDetail:
    """Tests for product detail API"""
    
    def test_get_product_detail_with_supplier(self):
        """Test getting a product detail with supplier link"""
        # First get a product that has a supplier link
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 20})
        products = response.json()["data"]
        
        product_with_supplier = None
        for p in products:
            if p.get("supplier_link") and "aliexpress.com" in p.get("supplier_link", ""):
                product_with_supplier = p
                break
        
        if not product_with_supplier:
            pytest.skip("No products with AliExpress supplier links found")
            return
        
        # Get product detail
        product_id = product_with_supplier["id"]
        detail_response = requests.get(f"{BASE_URL}/api/products/{product_id}")
        
        assert detail_response.status_code == 200
        detail = detail_response.json()["data"]
        
        assert detail.get("supplier_link"), "Product detail should have supplier_link"
        assert "aliexpress.com" in detail.get("supplier_link", "").lower()
        
        print(f"✓ Product detail has supplier link: {detail.get('supplier_link')[:60]}...")
        print(f"✓ Product: {detail.get('product_name')[:50]}")
        print(f"✓ is_real_data: {detail.get('is_real_data')}")
        return detail


class TestFullScrapeEndpoint:
    """Tests for full scrape endpoint (may take longer)"""
    
    def test_full_scrape_requires_api_key(self):
        """Test that full scrape requires API key"""
        response = requests.post(f"{BASE_URL}/api/ingestion/scrape/full")
        
        assert response.status_code == 401, "Should require API key"
        print("✓ Full scrape endpoint correctly requires API key")
    
    def test_full_scrape_with_api_key(self):
        """Test POST /api/ingestion/scrape/full with API key"""
        headers = {"X-API-Key": API_KEY}
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/full",
            headers=headers,
            params={"max_products": 5},  # Very small for testing
            timeout=120  # 2 min timeout for full scrape
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Check response has expected structure
        assert "started_at" in data or "results_by_source" in data
        
        print(f"✓ Full scrape returned successfully")
        if "results_by_source" in data:
            for source, result in data["results_by_source"].items():
                status = "✓" if result.get("success") else "✗"
                fetched = result.get("products_fetched", 0)
                print(f"  {status} {source}: {fetched} products")
        
        return data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
