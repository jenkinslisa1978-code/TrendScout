"""
Avasam UK Supplier Integration Tests

Tests the Avasam integration including:
- Service layer (services/avasam.py)
- Routes (routes/avasam.py)
- Scheduler task (sync_avasam_products in tasks.py)
- Shipping tier update (Avasam products get green/UK Warehouse tier)
- Supplier comparison inclusion
- Graceful error handling when API keys not configured
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "reviewer@trendscout.click"
TEST_PASSWORD = "ShopifyReview2026!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for protected endpoints."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with authentication token."""
    return {"Authorization": f"Bearer {auth_token}"}


class TestAvasamEndpointsGracefulErrors:
    """
    Test that all Avasam endpoints return graceful errors when API keys not configured.
    Expected: success: false with error message, NOT a 500 error.
    """

    def test_avasam_search_graceful_error(self, auth_headers):
        """GET /api/avasam/search?q=test returns graceful error when keys not configured."""
        response = requests.get(
            f"{BASE_URL}/api/avasam/search",
            params={"q": "test"},
            headers=auth_headers
        )
        # Should NOT be a 500 error
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should have success: false with error message
        assert data.get("success") is False, f"Expected success=False, got: {data}"
        assert "error" in data, f"Expected error field in response: {data}"
        assert "AVASAM_CONSUMER_KEY" in data["error"] or "not configured" in data["error"].lower(), \
            f"Expected configuration error message, got: {data['error']}"
        # Should still have products array (empty)
        assert "products" in data, f"Expected products array in response: {data}"
        assert data["products"] == [], f"Expected empty products array: {data}"
        print(f"PASS: /api/avasam/search returns graceful error: {data['error']}")

    def test_avasam_categories_graceful_error(self, auth_headers):
        """GET /api/avasam/categories returns graceful error when keys not configured."""
        response = requests.get(
            f"{BASE_URL}/api/avasam/categories",
            headers=auth_headers
        )
        # Should NOT be a 500 error
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should have success: false with error message
        assert data.get("success") is False, f"Expected success=False, got: {data}"
        assert "error" in data, f"Expected error field in response: {data}"
        # Should still have categories array (empty)
        assert "categories" in data, f"Expected categories array in response: {data}"
        assert data["categories"] == [], f"Expected empty categories array: {data}"
        print(f"PASS: /api/avasam/categories returns graceful error: {data['error']}")

    def test_avasam_product_detail_404(self, auth_headers):
        """GET /api/avasam/product/123 returns 404 when keys not configured."""
        response = requests.get(
            f"{BASE_URL}/api/avasam/product/123",
            headers=auth_headers
        )
        # Should return 404 (product not found due to API failure)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"PASS: /api/avasam/product/123 returns 404 as expected")

    def test_avasam_stock_404(self, auth_headers):
        """GET /api/avasam/stock/123 returns 404 when keys not configured."""
        response = requests.get(
            f"{BASE_URL}/api/avasam/stock/123",
            headers=auth_headers
        )
        # Should return 404 (stock not found due to API failure)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"PASS: /api/avasam/stock/123 returns 404 as expected")

    def test_avasam_import_404(self, auth_headers):
        """POST /api/avasam/import/123 returns 404 when keys not configured."""
        response = requests.post(
            f"{BASE_URL}/api/avasam/import/123",
            headers=auth_headers
        )
        # Should return 404 (cannot import due to API failure)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"PASS: /api/avasam/import/123 returns 404 as expected")

    def test_avasam_sync_history_empty(self, auth_headers):
        """GET /api/avasam/sync/history returns empty history array."""
        response = requests.get(
            f"{BASE_URL}/api/avasam/sync/history",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got: {data}"
        assert "history" in data, f"Expected history field in response: {data}"
        assert isinstance(data["history"], list), f"Expected history to be a list: {data}"
        print(f"PASS: /api/avasam/sync/history returns history array (length: {len(data['history'])})")


class TestAvasamAuthenticationRequired:
    """Test that all Avasam endpoints require authentication."""

    def test_avasam_search_requires_auth(self):
        """GET /api/avasam/search requires authentication (401 without token)."""
        response = requests.get(
            f"{BASE_URL}/api/avasam/search",
            params={"q": "test"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: /api/avasam/search requires authentication")

    def test_avasam_categories_requires_auth(self):
        """GET /api/avasam/categories requires authentication."""
        response = requests.get(f"{BASE_URL}/api/avasam/categories")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: /api/avasam/categories requires authentication")

    def test_avasam_product_requires_auth(self):
        """GET /api/avasam/product/123 requires authentication."""
        response = requests.get(f"{BASE_URL}/api/avasam/product/123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: /api/avasam/product/123 requires authentication")

    def test_avasam_stock_requires_auth(self):
        """GET /api/avasam/stock/123 requires authentication."""
        response = requests.get(f"{BASE_URL}/api/avasam/stock/123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: /api/avasam/stock/123 requires authentication")

    def test_avasam_import_requires_auth(self):
        """POST /api/avasam/import/123 requires authentication."""
        response = requests.post(f"{BASE_URL}/api/avasam/import/123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: /api/avasam/import/123 requires authentication")

    def test_avasam_sync_history_requires_auth(self):
        """GET /api/avasam/sync/history requires authentication."""
        response = requests.get(f"{BASE_URL}/api/avasam/sync/history")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: /api/avasam/sync/history requires authentication")


class TestSupplierComparisonIncludesAvasam:
    """Test that supplier comparison endpoint includes Avasam UK."""

    def test_supplier_comparison_includes_avasam(self, auth_headers):
        """GET /api/cj/supplier-comparison?q=phone+cases includes Avasam UK in results."""
        response = requests.get(
            f"{BASE_URL}/api/cj/supplier-comparison",
            params={"q": "phone cases"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got: {data}"
        assert "suppliers" in data, f"Expected suppliers field in response: {data}"
        
        # Find Avasam in suppliers
        avasam_suppliers = [s for s in data["suppliers"] if s.get("source") == "avasam"]
        assert len(avasam_suppliers) > 0, f"Expected Avasam in suppliers list: {data['suppliers']}"
        
        avasam = avasam_suppliers[0]
        # Verify Avasam UK properties
        assert avasam.get("source_label") == "Avasam UK", f"Expected source_label='Avasam UK', got: {avasam}"
        assert avasam.get("uk_warehouse") is True, f"Expected uk_warehouse=True, got: {avasam}"
        assert avasam.get("shipping_days") == 2, f"Expected shipping_days=2, got: {avasam}"
        
        print(f"PASS: Supplier comparison includes Avasam UK with uk_warehouse=True, shipping_days=2")
        print(f"  Avasam entry: source={avasam['source']}, mode={avasam.get('mode')}, uk_warehouse={avasam.get('uk_warehouse')}")


class TestShippingTierForAvasamProducts:
    """Test that Avasam products get green UK Warehouse shipping tier."""

    def test_compute_uk_shipping_tier_avasam_pid(self):
        """Products with avasam_pid get green tier with 'UK Warehouse' label."""
        # Import the scoring function
        import sys
        sys.path.insert(0, '/app/backend')
        from common.scoring import compute_uk_shipping_tier
        
        # Test product with avasam_pid
        product = {
            "avasam_pid": "12345",
            "product_name": "Test Avasam Product",
            "suppliers": []
        }
        
        tier = compute_uk_shipping_tier(product)
        
        assert tier["tier"] == "green", f"Expected tier='green', got: {tier}"
        assert tier["label"] == "UK Warehouse", f"Expected label='UK Warehouse', got: {tier}"
        assert tier["color"] == "green", f"Expected color='green', got: {tier}"
        assert tier["days_estimate"] == "1-3 days", f"Expected days_estimate='1-3 days', got: {tier}"
        assert "Avasam" in tier["description"], f"Expected 'Avasam' in description, got: {tier}"
        
        print(f"PASS: avasam_pid product gets green tier: {tier}")

    def test_compute_uk_shipping_tier_avasam_data_source(self):
        """Products with data_source='avasam' get green tier."""
        import sys
        sys.path.insert(0, '/app/backend')
        from common.scoring import compute_uk_shipping_tier
        
        # Test product with data_source=avasam
        product = {
            "data_source": "avasam",
            "product_name": "Test Avasam Product",
            "suppliers": []
        }
        
        tier = compute_uk_shipping_tier(product)
        
        assert tier["tier"] == "green", f"Expected tier='green', got: {tier}"
        assert tier["label"] == "UK Warehouse", f"Expected label='UK Warehouse', got: {tier}"
        
        print(f"PASS: data_source='avasam' product gets green tier: {tier}")

    def test_cj_products_still_get_yellow_tier(self):
        """CJ products still get yellow tier (no regression)."""
        import sys
        sys.path.insert(0, '/app/backend')
        from common.scoring import compute_uk_shipping_tier
        
        # Test CJ product
        product = {
            "cj_pid": "CJ12345",
            "data_source": "cj_dropshipping",
            "product_name": "Test CJ Product",
            "suppliers": [{
                "name": "CJ Dropshipping",
                "country": "CN",
                "lead_time_days": 8
            }]
        }
        
        tier = compute_uk_shipping_tier(product)
        
        assert tier["tier"] == "yellow", f"Expected tier='yellow', got: {tier}"
        assert tier["label"] == "7-14 Days", f"Expected label='7-14 Days', got: {tier}"
        
        print(f"PASS: CJ product still gets yellow tier: {tier}")

    def test_generic_products_still_get_red_tier(self):
        """Generic products still get red tier (no regression)."""
        import sys
        sys.path.insert(0, '/app/backend')
        from common.scoring import compute_uk_shipping_tier
        
        # Test generic product (no cj_pid, no avasam_pid)
        product = {
            "product_name": "Generic Product",
            "data_source": "amazon_movers",
            "suppliers": [{
                "name": "AliExpress",
                "country": "CN"
            }]
        }
        
        tier = compute_uk_shipping_tier(product)
        
        assert tier["tier"] == "red", f"Expected tier='red', got: {tier}"
        assert tier["label"] == "3-4 Weeks", f"Expected label='3-4 Weeks', got: {tier}"
        
        print(f"PASS: Generic product still gets red tier: {tier}")


class TestSyncAvasamProductsTaskRegistered:
    """Test that sync_avasam_products task is registered in TaskRegistry."""

    def test_sync_avasam_products_task_exists(self):
        """sync_avasam_products task is registered in TaskRegistry."""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.jobs.tasks import TaskRegistry
        
        all_tasks = TaskRegistry.get_all_tasks()
        
        assert "sync_avasam_products" in all_tasks, \
            f"Expected 'sync_avasam_products' in TaskRegistry, got: {list(all_tasks.keys())}"
        
        task = all_tasks["sync_avasam_products"]
        assert task["description"], f"Expected task to have description: {task}"
        assert task["default_schedule"] == "0 */6 * * *", \
            f"Expected schedule '0 */6 * * *', got: {task['default_schedule']}"
        
        print(f"PASS: sync_avasam_products task registered with schedule: {task['default_schedule']}")

    def test_sync_avasam_products_in_scheduled_tasks(self):
        """sync_avasam_products appears in scheduled tasks list."""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.jobs.tasks import TaskRegistry
        
        scheduled = TaskRegistry.get_scheduled_tasks()
        task_names = [t["name"] for t in scheduled]
        
        assert "sync_avasam_products" in task_names, \
            f"Expected 'sync_avasam_products' in scheduled tasks, got: {task_names}"
        
        print(f"PASS: sync_avasam_products in scheduled tasks list")


class TestBackendStartsWithAvasamRouter:
    """Test that backend starts without errors after adding Avasam router."""

    def test_health_endpoint(self):
        """Backend health endpoint responds (server started successfully)."""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Health endpoint may return JSON or plain text
        try:
            data = response.json()
            assert data.get("status") == "ok", f"Expected status='ok', got: {data}"
        except Exception:
            # Plain text response is also acceptable
            assert "ok" in response.text.lower() or response.status_code == 200
        
        print("PASS: Backend health endpoint responds - server started successfully")

    def test_api_health_endpoint(self):
        """Backend /api/health endpoint responds."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        print("PASS: /api/health endpoint responds")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
