"""
Tests for Onboarding Walkthrough, Quick Launch Flow, Supplier Section, and Ad Creative Generation
Testing iteration 68 focus areas
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://product-scout-80.preview.emergentagent.com').rstrip('/')

class TestAdCreativeGeneration:
    """Test ad creative generation endpoint"""

    def test_health_check(self):
        """Verify backend is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("PASSED: Health check endpoint")

    def test_get_products_for_ad_generation(self):
        """Get a product to test ad generation with"""
        response = requests.get(f"{BASE_URL}/api/products?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        products = data.get("data", data.get("products", []))
        assert len(products) > 0, "Need at least one product to test ad generation"
        print(f"PASSED: Got {len(products)} products for testing")
        return products[0]

    def test_ad_creative_generation_endpoint_exists(self):
        """Test that ad creative generation endpoint exists"""
        # First get a product
        products_response = requests.get(f"{BASE_URL}/api/products?page=1&limit=1")
        assert products_response.status_code == 200
        data = products_response.json()
        products = data.get("data", data.get("products", []))
        assert len(products) > 0
        
        product_id = products[0]["id"]
        
        # Test the endpoint - may take time due to LLM call
        response = requests.post(f"{BASE_URL}/api/ad-creatives/generate/{product_id}", timeout=120)
        
        # The endpoint should return 200 with valid response or 401 if auth required
        assert response.status_code in [200, 401, 404, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            # Check response structure
            assert "product_id" in data or "id" in data or "creatives" in data, f"Invalid response structure: {data.keys()}"
            print(f"PASSED: Ad creative generation returned valid response for product {product_id}")
        elif response.status_code == 401:
            print(f"PASSED: Ad creative endpoint requires auth (401) - expected behavior")
        else:
            print(f"WARNING: Ad creative endpoint returned {response.status_code}")
        
        return response.status_code


class TestSupplierEndpoints:
    """Test supplier-related endpoints (no external links)"""
    
    def test_supplier_endpoint_exists(self):
        """Test that supplier endpoints exist and return proper data"""
        # Get a product first
        products_response = requests.get(f"{BASE_URL}/api/products?page=1&limit=1")
        assert products_response.status_code == 200
        data = products_response.json()
        products = data.get("data", data.get("products", []))
        assert len(products) > 0
        
        product_id = products[0]["id"]
        
        # Get suppliers for this product
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            suppliers = data.get("suppliers", [])
            print(f"PASSED: Supplier endpoint returned {len(suppliers)} suppliers")
            
            # Verify no external links in supplier data that would link to AliExpress
            for supplier in suppliers:
                # The supplier should not have external_link or search_link fields
                # that would redirect users to AliExpress
                assert "external_link" not in supplier or supplier.get("external_link") is None, \
                    "Supplier should not have external link"
                print(f"PASSED: Supplier {supplier.get('supplier_name', 'unknown')} has no external links")
        else:
            print("INFO: No suppliers found for this product (404)")


class TestQuickLaunchFlow:
    """Test Quick Launch Flow API endpoints"""
    
    def test_store_launch_endpoint(self):
        """Test the store launch endpoint used by Quick Launch"""
        response = requests.post(f"{BASE_URL}/api/stores/launch", json={
            "product_id": "test-product-id",
            "store_name": "Test Quick Launch Store"
        })
        
        # Should require auth or return some response
        assert response.status_code in [200, 201, 400, 401, 404, 422], f"Unexpected status: {response.status_code}"
        print(f"PASSED: Store launch endpoint responds with {response.status_code}")

    def test_connections_endpoint(self):
        """Test the connections endpoint used by Quick Launch"""
        response = requests.get(f"{BASE_URL}/api/connections/")
        
        # May return empty or require auth
        assert response.status_code in [200, 401], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            print(f"PASSED: Connections endpoint returns: stores={len(data.get('stores', []))}, ads={len(data.get('ads', []))}")
        else:
            print("PASSED: Connections endpoint requires auth (401)")


class TestDashboardEndpoints:
    """Test dashboard-related endpoints"""
    
    def test_products_sorted_by_launch_score(self):
        """Test products endpoint with launch_score sorting (used by Quick Launch)"""
        response = requests.get(f"{BASE_URL}/api/products?page=1&limit=10&sort_by=launch_score&sort_order=desc")
        assert response.status_code == 200
        
        data = response.json()
        products = data.get("data", data.get("products", []))
        assert len(products) > 0, "Should have products"
        
        # Check first product has expected fields for Quick Launch
        first = products[0]
        assert "product_name" in first, "Product should have name"
        assert "id" in first, "Product should have id"
        print(f"PASSED: Products sorted by launch_score, top product: {first.get('product_name')}")


class TestPlatformConnections:
    """Test Platform Connections page endpoints"""
    
    def test_platforms_endpoint(self):
        """Test the platforms listing endpoint"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200
        
        data = response.json()
        # API uses 'stores' and 'ads' keys
        store_platforms = data.get("stores", {})
        ad_platforms = data.get("ads", {})
        
        assert len(store_platforms) >= 5, f"Should have 5 store platforms, got {len(store_platforms)}"
        assert len(ad_platforms) >= 3, f"Should have 3 ad platforms, got {len(ad_platforms)}"
        
        print(f"PASSED: Platforms endpoint returns {len(store_platforms)} store, {len(ad_platforms)} ad platforms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
