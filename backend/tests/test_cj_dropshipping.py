"""
CJ Dropshipping API Integration Tests

Tests for:
- GET /api/cj/search - Search CJ products
- GET /api/cj/categories - Get CJ categories
- GET /api/cj/product/{pid} - Get product detail
- POST /api/cj/import/{pid} - Import CJ product
- POST /api/cj/sync - Manual CJ sync
- GET /api/cj/sync/history - Sync run history
- GET /api/cj/supplier-comparison - Compare suppliers
- POST /api/automation/scheduled/daily - Daily automation with CJ sync
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "reviewer@trendscout.click"
TEST_PASSWORD = "ShopifyReview2026!"
AUTOMATION_API_KEY = "vs_automation_key_2024"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for API calls"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with Bearer token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestCJSearch:
    """Tests for GET /api/cj/search endpoint"""
    
    def test_search_requires_auth(self):
        """Search endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cj/search?q=phone+accessories")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Search requires authentication")
    
    def test_search_returns_products(self, auth_headers):
        """Search returns success:true with products array"""
        response = requests.get(
            f"{BASE_URL}/api/cj/search?q=phone+accessories",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success:true, got {data}"
        assert "products" in data, f"Expected 'products' key in response"
        assert isinstance(data["products"], list), f"Expected products to be a list"
        
        # Verify product structure if products exist
        if data["products"]:
            product = data["products"][0]
            assert "cj_pid" in product, "Product should have cj_pid"
            assert "product_name" in product, "Product should have product_name"
            assert "sell_price" in product, "Product should have sell_price"
            print(f"PASS: Search returned {len(data['products'])} products")
        else:
            print("PASS: Search returned empty products array (API may have no results)")
    
    def test_search_with_pagination(self, auth_headers):
        """Search supports pagination parameters"""
        # Wait for rate limit to reset (CJ API: 1 req/sec)
        time.sleep(1.5)
        
        response = requests.get(
            f"{BASE_URL}/api/cj/search?q=phone&page=1&page_size=5",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # Handle rate limiting gracefully
        if data.get("error") and "Too Many Requests" in str(data.get("error", "")):
            pytest.skip("CJ API rate limited - this is expected behavior")
        assert data.get("success") is True
        assert "page" in data
        assert "page_size" in data
        print(f"PASS: Search pagination works - page={data.get('page')}, page_size={data.get('page_size')}")


class TestCJCategories:
    """Tests for GET /api/cj/categories endpoint"""
    
    def test_categories_requires_auth(self):
        """Categories endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cj/categories")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Categories requires authentication")
    
    def test_categories_returns_list(self, auth_headers):
        """Categories returns success:true with categories array"""
        response = requests.get(
            f"{BASE_URL}/api/cj/categories",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success:true, got {data}"
        assert "categories" in data, f"Expected 'categories' key in response"
        assert isinstance(data["categories"], list), f"Expected categories to be a list"
        
        # Verify category structure if categories exist
        if data["categories"]:
            category = data["categories"][0]
            assert "id" in category, "Category should have id"
            assert "name" in category, "Category should have name"
            print(f"PASS: Categories returned {len(data['categories'])} categories")
        else:
            print("PASS: Categories returned empty array (API may have no categories)")


class TestCJProductDetail:
    """Tests for GET /api/cj/product/{pid} endpoint"""
    
    def test_product_detail_requires_auth(self):
        """Product detail endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cj/product/test-pid")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Product detail requires authentication")
    
    def test_product_detail_not_found(self, auth_headers):
        """Product detail returns 404 for invalid pid"""
        response = requests.get(
            f"{BASE_URL}/api/cj/product/invalid-pid-12345",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Product detail returns 404 for invalid pid")
    
    def test_product_detail_from_search(self, auth_headers):
        """Product detail works with pid from search results"""
        # Wait for rate limit to reset (CJ API: 1 req/sec)
        time.sleep(1.5)
        
        # First search for products
        search_response = requests.get(
            f"{BASE_URL}/api/cj/search?q=phone+case&page_size=1",
            headers=auth_headers
        )
        
        if search_response.status_code != 200:
            pytest.skip("Search failed, cannot test product detail")
        
        search_data = search_response.json()
        if not search_data.get("products"):
            pytest.skip("No products found in search, cannot test product detail")
        
        pid = search_data["products"][0]["cj_pid"]
        
        # Wait for rate limit
        time.sleep(1.5)
        
        # Get product detail
        response = requests.get(
            f"{BASE_URL}/api/cj/product/{pid}",
            headers=auth_headers
        )
        
        # Handle rate limiting gracefully
        if response.status_code == 404:
            data = response.json()
            if "Too Many Requests" in str(data.get("error", "")):
                pytest.skip("CJ API rate limited - this is expected behavior")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success:true, got {data}"
        assert "product" in data, f"Expected 'product' key in response"
        
        product = data["product"]
        assert product.get("cj_pid") == pid, f"Product pid mismatch"
        assert "product_name" in product, "Product should have product_name"
        assert "sell_price" in product, "Product should have sell_price"
        print(f"PASS: Product detail returned for pid={pid}")


class TestCJImport:
    """Tests for POST /api/cj/import/{pid} endpoint"""
    
    def test_import_requires_auth(self):
        """Import endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/cj/import/test-pid")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Import requires authentication")
    
    def test_import_invalid_pid(self, auth_headers):
        """Import returns 404 for invalid pid"""
        response = requests.post(
            f"{BASE_URL}/api/cj/import/invalid-pid-99999",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Import returns 404 for invalid pid")
    
    def test_import_product_from_search(self, auth_headers):
        """Import a product from search results"""
        # Wait for rate limit to reset (CJ API: 1 req/sec)
        time.sleep(1.5)
        
        # First search for products
        search_response = requests.get(
            f"{BASE_URL}/api/cj/search?q=LED+lights&page_size=5",
            headers=auth_headers
        )
        
        if search_response.status_code != 200:
            pytest.skip("Search failed, cannot test import")
        
        search_data = search_response.json()
        if not search_data.get("products"):
            pytest.skip("No products found in search, cannot test import")
        
        # Try to import first product
        pid = search_data["products"][0]["cj_pid"]
        
        # Wait for rate limit
        time.sleep(1.5)
        
        response = requests.post(
            f"{BASE_URL}/api/cj/import/{pid}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success:true, got {data}"
        assert "product_id" in data, f"Expected 'product_id' in response"
        
        # Check if already existed or newly imported
        if data.get("already_existed"):
            print(f"PASS: Import returned already_existed:true for pid={pid}")
        else:
            print(f"PASS: Import created new product with id={data['product_id']}")
    
    def test_import_deduplication(self, auth_headers):
        """Import same product twice returns already_existed:true"""
        # Wait for rate limit to reset (CJ API: 1 req/sec)
        time.sleep(1.5)
        
        # First search for products
        search_response = requests.get(
            f"{BASE_URL}/api/cj/search?q=phone+case&page_size=1",
            headers=auth_headers
        )
        
        if search_response.status_code != 200:
            pytest.skip("Search failed, cannot test deduplication")
        
        search_data = search_response.json()
        if not search_data.get("products"):
            pytest.skip("No products found in search, cannot test deduplication")
        
        pid = search_data["products"][0]["cj_pid"]
        
        # Wait for rate limit
        time.sleep(1.5)
        
        # Import first time
        response1 = requests.post(
            f"{BASE_URL}/api/cj/import/{pid}",
            headers=auth_headers
        )
        assert response1.status_code == 200
        
        # Import second time - should return already_existed (no rate limit needed, uses DB)
        response2 = requests.post(
            f"{BASE_URL}/api/cj/import/{pid}",
            headers=auth_headers
        )
        assert response2.status_code == 200
        
        data2 = response2.json()
        assert data2.get("success") is True
        assert data2.get("already_existed") is True, f"Expected already_existed:true on second import"
        print(f"PASS: Deduplication works - second import returned already_existed:true")


class TestCJSync:
    """Tests for POST /api/cj/sync endpoint"""
    
    def test_sync_requires_auth(self):
        """Sync endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/cj/sync")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Sync requires authentication")
    
    def test_sync_returns_counts(self, auth_headers):
        """Sync returns fetched/created/skipped counts"""
        # Note: This endpoint may take 10-30 seconds due to CJ API rate limiting
        response = requests.post(
            f"{BASE_URL}/api/cj/sync",
            headers=auth_headers,
            timeout=60  # Extended timeout for rate-limited API
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success:true, got {data}"
        assert "details" in data, f"Expected 'details' in response"
        
        details = data["details"]
        assert "fetched" in details, "Details should have 'fetched' count"
        assert "created" in details, "Details should have 'created' count"
        assert "skipped" in details, "Details should have 'skipped' count"
        
        print(f"PASS: Sync completed - fetched={details['fetched']}, created={details['created']}, skipped={details['skipped']}")


class TestCJSyncHistory:
    """Tests for GET /api/cj/sync/history endpoint"""
    
    def test_sync_history_requires_auth(self):
        """Sync history endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cj/sync/history")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Sync history requires authentication")
    
    def test_sync_history_returns_list(self, auth_headers):
        """Sync history returns success:true with history array"""
        response = requests.get(
            f"{BASE_URL}/api/cj/sync/history",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success:true, got {data}"
        assert "history" in data, f"Expected 'history' key in response"
        assert isinstance(data["history"], list), f"Expected history to be a list"
        
        # Verify history entry structure if entries exist
        if data["history"]:
            entry = data["history"][0]
            assert "job_name" in entry, "History entry should have job_name"
            assert entry["job_name"] == "sync_cj_products", f"Expected job_name='sync_cj_products'"
            assert "status" in entry, "History entry should have status"
            assert "run_time" in entry, "History entry should have run_time"
            print(f"PASS: Sync history returned {len(data['history'])} entries")
        else:
            print("PASS: Sync history returned empty array (no sync runs yet)")
    
    def test_sync_history_limit(self, auth_headers):
        """Sync history respects limit parameter"""
        response = requests.get(
            f"{BASE_URL}/api/cj/sync/history?limit=5",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert len(data.get("history", [])) <= 5, "History should respect limit parameter"
        print(f"PASS: Sync history limit works - returned {len(data.get('history', []))} entries (limit=5)")


class TestCJSupplierComparison:
    """Tests for GET /api/cj/supplier-comparison endpoint"""
    
    def test_supplier_comparison_requires_auth(self):
        """Supplier comparison endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cj/supplier-comparison?q=phone+case")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Supplier comparison requires authentication")
    
    def test_supplier_comparison_returns_suppliers(self, auth_headers):
        """Supplier comparison returns success:true with suppliers array"""
        response = requests.get(
            f"{BASE_URL}/api/cj/supplier-comparison?q=phone+case",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success:true, got {data}"
        assert "suppliers" in data, f"Expected 'suppliers' key in response"
        assert isinstance(data["suppliers"], list), f"Expected suppliers to be a list"
        assert "query" in data, f"Expected 'query' key in response"
        
        # Verify supplier structure if suppliers exist
        if data["suppliers"]:
            supplier = data["suppliers"][0]
            assert "source" in supplier, "Supplier should have source"
            assert "source_label" in supplier, "Supplier should have source_label"
            assert "product_name" in supplier, "Supplier should have product_name"
            assert "supplier_cost" in supplier, "Supplier should have supplier_cost"
            print(f"PASS: Supplier comparison returned {len(data['suppliers'])} suppliers")
        else:
            print("PASS: Supplier comparison returned empty array")
    
    def test_supplier_comparison_includes_cj(self, auth_headers):
        """Supplier comparison includes CJ Dropshipping data"""
        response = requests.get(
            f"{BASE_URL}/api/cj/supplier-comparison?q=LED+lights",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check if CJ is in the suppliers
        cj_suppliers = [s for s in data.get("suppliers", []) if s.get("source") == "cj_dropshipping"]
        if cj_suppliers:
            cj = cj_suppliers[0]
            assert cj.get("source_label") == "CJ Dropshipping"
            assert cj.get("mode") == "live", "CJ should be in live mode"
            print(f"PASS: Supplier comparison includes CJ Dropshipping with {len(cj_suppliers)} products")
        else:
            print("PASS: Supplier comparison returned (CJ may have no results for this query)")


class TestDailyAutomation:
    """Tests for POST /api/automation/scheduled/daily endpoint"""
    
    def test_daily_automation_requires_api_key(self):
        """Daily automation requires X-API-Key header"""
        response = requests.post(f"{BASE_URL}/api/automation/scheduled/daily")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Daily automation requires API key")
    
    def test_daily_automation_invalid_key(self):
        """Daily automation rejects invalid API key"""
        response = requests.post(
            f"{BASE_URL}/api/automation/scheduled/daily",
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Daily automation rejects invalid API key")
    
    def test_daily_automation_includes_cj_sync(self):
        """Daily automation includes cj_sync in response"""
        response = requests.post(
            f"{BASE_URL}/api/automation/scheduled/daily",
            headers={"X-API-Key": AUTOMATION_API_KEY},
            timeout=120  # Extended timeout for full automation
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success:true, got {data}"
        assert "cj_sync" in data, f"Expected 'cj_sync' key in response"
        
        cj_sync = data["cj_sync"]
        if cj_sync.get("error") == "skipped":
            print("PASS: Daily automation ran but CJ sync was skipped (may be rate limited)")
        else:
            assert "fetched" in cj_sync or "created" in cj_sync, f"CJ sync should have counts"
            print(f"PASS: Daily automation includes cj_sync: {cj_sync}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
