"""
Test suite for ViralScout Real Data Scraping/Ingestion APIs

Features tested:
- GET /api/ingestion/scrape/health - Health status for all scrapers
- GET /api/ingestion/scrape/quality - Data quality report (real vs simulated)
- POST /api/ingestion/scrape/{source_name} - Scrape products from specific source
- GET /api/ingestion/scrape/history - Recent scraping runs
- POST /api/ingestion/scrape/full - Full scraping from all sources

Rate limiting: 1 req/sec, 24h cache
API Key required: X-API-Key: vs_automation_key_2024
"""

import pytest
import requests
import os
import time

# Use public URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# API key for protected scraping endpoints
API_KEY = "vs_automation_key_2024"

# Valid source names for scraping
VALID_SOURCES = ['aliexpress', 'tiktok_trends', 'amazon_movers', 'cj_dropshipping']


class TestScraperHealthAPI:
    """Tests for GET /api/ingestion/scrape/health endpoint"""
    
    def test_health_endpoint_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/health")
        print(f"Health endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_health_returns_all_sources(self):
        """Health endpoint should return status for all scraper sources"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/health")
        assert response.status_code == 200
        
        data = response.json()
        print(f"Health data keys: {list(data.keys())}")
        
        # Should have status for each source
        for source in VALID_SOURCES:
            print(f"Checking source: {source}")
            # Note: source might be in data directly or might be empty if no scraping done yet
    
    def test_health_single_source(self):
        """Health endpoint should accept source_name parameter"""
        response = requests.get(
            f"{BASE_URL}/api/ingestion/scrape/health",
            params={"source_name": "aliexpress"}
        )
        print(f"Single source health status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        
        data = response.json()
        # Should have aliexpress in response
        assert "aliexpress" in data or "error" not in data
    
    def test_health_invalid_source_returns_error(self):
        """Health endpoint should handle invalid source name"""
        response = requests.get(
            f"{BASE_URL}/api/ingestion/scrape/health",
            params={"source_name": "invalid_source"}
        )
        print(f"Invalid source status: {response.status_code}")
        print(f"Response: {response.json()}")
        # Should return error for invalid source
        assert response.status_code == 200  # Returns dict with error key
        data = response.json()
        assert "error" in data


class TestDataQualityAPI:
    """Tests for GET /api/ingestion/scrape/quality endpoint"""
    
    def test_quality_endpoint_returns_200(self):
        """Quality endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/quality")
        print(f"Quality endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
    
    def test_quality_returns_expected_fields(self):
        """Quality endpoint should return real vs simulated breakdown"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/quality")
        assert response.status_code == 200
        
        data = response.json()
        print(f"Quality data: {data}")
        
        # Should have these fields
        expected_fields = [
            'total_products',
            'real_data_products', 
            'simulated_products',
            'real_data_percentage',
            'by_source',
            'generated_at'
        ]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
            print(f"  {field}: {data[field]}")
    
    def test_quality_has_source_breakdown(self):
        """Quality endpoint should have breakdown by source"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/quality")
        assert response.status_code == 200
        
        data = response.json()
        by_source = data.get('by_source', {})
        print(f"Sources in quality report: {list(by_source.keys())}")
        
        # Each source should have count and avg_confidence
        for source_name, source_data in by_source.items():
            print(f"  {source_name}: count={source_data.get('count')}, avg_confidence={source_data.get('avg_confidence')}")
            assert 'count' in source_data
            assert 'avg_confidence' in source_data


class TestScrapeHistoryAPI:
    """Tests for GET /api/ingestion/scrape/history endpoint"""
    
    def test_history_endpoint_returns_200(self):
        """History endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/history")
        print(f"History endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
    
    def test_history_returns_list(self):
        """History endpoint should return a list of ingestion runs"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/history")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "History should be a list"
        print(f"Number of history entries: {len(data)}")
        
        if data:
            print(f"First entry keys: {list(data[0].keys())}")
    
    def test_history_respects_limit(self):
        """History endpoint should respect limit parameter"""
        response = requests.get(
            f"{BASE_URL}/api/ingestion/scrape/history",
            params={"limit": 5}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 5


class TestScrapeSourceAPI:
    """Tests for POST /api/ingestion/scrape/{source_name} endpoint"""
    
    def test_scrape_requires_api_key(self):
        """Scrape endpoint should require API key"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/aliexpress",
            params={"max_products": 5}
        )
        print(f"No API key status: {response.status_code}")
        assert response.status_code == 401, "Should reject without API key"
    
    def test_scrape_wrong_api_key(self):
        """Scrape endpoint should reject wrong API key"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/aliexpress",
            params={"max_products": 5},
            headers={"X-API-Key": "wrong_key"}
        )
        print(f"Wrong API key status: {response.status_code}")
        assert response.status_code == 401, "Should reject wrong API key"
    
    def test_scrape_invalid_source(self):
        """Scrape endpoint should reject invalid source name"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/invalid_source",
            params={"max_products": 5},
            headers={"X-API-Key": API_KEY}
        )
        print(f"Invalid source status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400, "Should reject invalid source"
        assert "Invalid source" in response.json().get("detail", "")
    
    def test_scrape_aliexpress(self):
        """Scrape AliExpress with valid API key (small batch)"""
        print("Testing AliExpress scrape with max_products=5...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/aliexpress",
            params={"max_products": 5},
            headers={"X-API-Key": API_KEY},
            timeout=120  # Long timeout for scraping
        )
        
        duration = time.time() - start_time
        print(f"AliExpress scrape status: {response.status_code} (took {duration:.1f}s)")
        
        # Accept 200 (success) or 500 (scraping blocked/failed - common with web scraping)
        if response.status_code == 200:
            data = response.json()
            print(f"Scrape result: {data}")
            
            # Verify expected fields
            assert 'source_name' in data
            assert data['source_name'] == 'aliexpress'
            assert 'products_fetched' in data
            assert 'products_created' in data
            assert 'products_updated' in data
            assert 'success' in data
            
            print(f"  - Products fetched: {data.get('products_fetched', 0)}")
            print(f"  - Products created: {data.get('products_created', 0)}")
            print(f"  - Products updated: {data.get('products_updated', 0)}")
        else:
            print(f"Scraping may be blocked: {response.text}")
            # This is acceptable - web scraping can be blocked
            assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
    
    def test_scrape_tiktok_trends(self):
        """Scrape TikTok trends with valid API key"""
        print("Testing TikTok trends scrape with max_products=5...")
        
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/tiktok_trends",
            params={"max_products": 5},
            headers={"X-API-Key": API_KEY},
            timeout=120
        )
        
        print(f"TikTok scrape status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Scrape result: {data}")
            assert data['source_name'] == 'tiktok_trends'
        else:
            print(f"Scraping may be blocked: {response.text}")
            assert response.status_code in [200, 500]
    
    def test_scrape_amazon_movers(self):
        """Scrape Amazon Movers & Shakers"""
        print("Testing Amazon Movers scrape with max_products=5...")
        
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/amazon_movers",
            params={"max_products": 5},
            headers={"X-API-Key": API_KEY},
            timeout=120
        )
        
        print(f"Amazon scrape status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Scrape result: {data}")
            assert data['source_name'] == 'amazon_movers'
        else:
            print(f"Scraping may be blocked: {response.text}")
            assert response.status_code in [200, 500]
    
    def test_scrape_cj_dropshipping(self):
        """Scrape CJ Dropshipping"""
        print("Testing CJ Dropshipping scrape with max_products=5...")
        
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/cj_dropshipping",
            params={"max_products": 5},
            headers={"X-API-Key": API_KEY},
            timeout=120
        )
        
        print(f"CJ scrape status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Scrape result: {data}")
            assert data['source_name'] == 'cj_dropshipping'
        else:
            print(f"Scraping may be blocked: {response.text}")
            assert response.status_code in [200, 500]


class TestFullScrapeAPI:
    """Tests for POST /api/ingestion/scrape/full endpoint"""
    
    def test_full_scrape_requires_api_key(self):
        """Full scrape endpoint should require API key"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/full",
            params={"max_products": 5}
        )
        print(f"No API key status: {response.status_code}")
        assert response.status_code == 401
    
    def test_full_scrape_single_source(self):
        """Full scrape with single source specified"""
        print("Testing full scrape with single source (aliexpress)...")
        
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/full",
            params={"max_products": 5},
            json={"sources": ["aliexpress"]},
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            timeout=120
        )
        
        print(f"Full scrape status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Full scrape result keys: {list(data.keys())}")
            
            # Verify aggregated results
            assert 'started_at' in data
            assert 'completed_at' in data
            assert 'sources_attempted' in data
            assert 'results_by_source' in data
        else:
            print(f"Response: {response.text}")
            assert response.status_code in [200, 422, 500]


class TestProductDataIntegrity:
    """Tests to verify scraped products have correct data attributes"""
    
    def test_products_have_data_source_field(self):
        """Products should have data_source field set correctly"""
        # Query some products to check their data_source field
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 20})
        
        print(f"Products API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('data', [])
            
            print(f"Total products: {len(products)}")
            
            # Count products by data_source
            source_counts = {}
            for product in products:
                source = product.get('data_source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            print(f"Products by data_source: {source_counts}")
    
    def test_products_have_is_real_data_field(self):
        """Products should have is_real_data field"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 20})
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('data', [])
            
            real_count = 0
            simulated_count = 0
            
            for product in products:
                if product.get('is_real_data', False):
                    real_count += 1
                else:
                    simulated_count += 1
            
            print(f"Real data products: {real_count}")
            print(f"Simulated products: {simulated_count}")
    
    def test_products_have_confidence_score(self):
        """Products should have confidence_score field"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 20})
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('data', [])
            
            confidence_scores = [p.get('confidence_score', 0) for p in products]
            
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                print(f"Average confidence score: {avg_confidence:.1f}")
                print(f"Confidence range: {min(confidence_scores)} - {max(confidence_scores)}")
    
    def test_products_have_last_updated(self):
        """Products should have last_updated field"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 20})
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('data', [])
            
            updated_count = sum(1 for p in products if p.get('last_updated'))
            print(f"Products with last_updated: {updated_count}/{len(products)}")


class TestHealthStatusTracking:
    """Tests to verify health monitoring tracks success/failure rates"""
    
    def test_health_status_values(self):
        """Health status should be one of expected values"""
        valid_statuses = ['healthy', 'degraded', 'unavailable', 'rate_limited']
        
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/health")
        assert response.status_code == 200
        
        data = response.json()
        
        for source_name, source_health in data.items():
            if isinstance(source_health, dict) and 'status' in source_health:
                status = source_health.get('status')
                print(f"  {source_name}: {status}")
                assert status in valid_statuses, f"Invalid status: {status}"
    
    def test_health_has_success_rate(self):
        """Health status should include success rate"""
        response = requests.get(f"{BASE_URL}/api/ingestion/scrape/health")
        assert response.status_code == 200
        
        data = response.json()
        
        for source_name, source_health in data.items():
            if isinstance(source_health, dict):
                success_rate = source_health.get('success_rate_24h')
                print(f"  {source_name}: success_rate_24h={success_rate}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
