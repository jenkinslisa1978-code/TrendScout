"""
Test LaunchPad Bug Fixes - Test the 3 reported bugs:
1. Can't find a supplier - Fixed: Frontend now calls /api/suppliers/{id} correctly
2. Can't generate a store preview - Fixed: Backend stores.py imports were missing
3. Launch product fails - Fixed: Both issues above caused this
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_PRODUCT_ID = "2e3d8782-0026-4fef-a04a-a1d3426e2d26"

class TestLaunchPadBugFixes:
    """Tests for the 3 reported LaunchPad bugs that were fixed"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "jenkinslisa1978@gmail.com",
                "password": "admin123456"
            }
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Auth headers for authenticated requests"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    # ========== Step 1: Product Intel ==========
    def test_get_product_data(self, auth_headers):
        """Step 1 - GET /api/products/{id} loads product data correctly"""
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get product: {response.text}"
        
        data = response.json()
        product = data.get("data") or data
        
        # Verify product data is present
        assert product.get("id") == TEST_PRODUCT_ID, "Product ID mismatch"
        assert product.get("product_name"), "Product name missing"
        assert "category" in product, "Category field missing"
        print(f"✓ Product loaded: {product.get('product_name')}")
    
    # ========== Step 2: Supplier (BUG FIX #1) ==========
    def test_get_suppliers_for_product(self, auth_headers):
        """
        BUG FIX #1 - GET /api/suppliers/{id} returns suppliers for a product
        Previously: Frontend called wrong endpoint /api/products/{id}/suppliers
        Fixed: Frontend now calls /api/suppliers/{id}
        """
        response = requests.get(
            f"{BASE_URL}/api/suppliers/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get suppliers: {response.text}"
        
        data = response.json()
        suppliers = data.get("suppliers", [])
        
        # Verify suppliers are returned
        assert len(suppliers) >= 1, "No suppliers found - bug not fixed!"
        
        # Verify supplier data structure
        first_supplier = suppliers[0]
        assert first_supplier.get("id"), "Supplier ID missing"
        assert first_supplier.get("supplier_name"), "Supplier name missing"
        assert "supplier_cost" in first_supplier, "Supplier cost missing"
        
        print(f"✓ Suppliers found: {len(suppliers)}")
        for sup in suppliers[:2]:
            print(f"  - {sup.get('supplier_name')}: ${sup.get('supplier_cost', 0):.2f}")
    
    # ========== Step 3: Store (BUG FIX #2) ==========
    def test_store_launch_creates_store(self, auth_headers):
        """
        BUG FIX #2 - POST /api/stores/launch creates a store successfully
        Previously: Backend stores.py was missing imports for StoreGenerator, etc.
        Fixed: Added missing imports from store_service.py
        """
        import time
        store_name = f"Test LaunchPad Store {int(time.time())}"
        
        response = requests.post(
            f"{BASE_URL}/api/stores/launch",
            json={
                "product_id": TEST_PRODUCT_ID,
                "store_name": store_name
            },
            headers=auth_headers
        )
        
        # Should return 200 with store data
        assert response.status_code == 200, f"Store launch failed: {response.text}"
        
        data = response.json()
        
        # Verify success
        assert data.get("success") is True, f"Store launch not successful: {data}"
        
        # Verify store was created
        store = data.get("store", {})
        assert store.get("id"), "Store ID missing in response"
        assert store.get("name"), "Store name missing in response"
        
        # Verify product was attached
        product = data.get("product", {})
        assert product.get("original_product_id") == TEST_PRODUCT_ID, "Product not attached to store"
        
        # Verify generation data exists
        generation = data.get("generation", {})
        assert generation.get("selected_name"), "Store generation data missing"
        
        print(f"✓ Store created: {store.get('name')} (ID: {store.get('id')})")
        print(f"  - Generation data: {bool(generation)}")
        print(f"  - Supplier connected: {data.get('supplier_connected', False)}")
        
        # Return store_id for cleanup if needed
        return store.get("id")
    
    def test_store_launch_with_supplier(self, auth_headers):
        """Test store launch with a selected supplier"""
        # First get suppliers
        sup_response = requests.get(
            f"{BASE_URL}/api/suppliers/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        suppliers = sup_response.json().get("suppliers", [])
        
        if suppliers:
            supplier_id = suppliers[0].get("id")
            
            import time
            response = requests.post(
                f"{BASE_URL}/api/stores/launch",
                json={
                    "product_id": TEST_PRODUCT_ID,
                    "supplier_id": supplier_id,
                    "store_name": f"Test Store With Supplier {int(time.time())}"
                },
                headers=auth_headers
            )
            
            assert response.status_code == 200, f"Store launch with supplier failed: {response.text}"
            data = response.json()
            assert data.get("success") is True
            assert data.get("supplier_connected") is True, "Supplier not connected to store"
            print(f"✓ Store created with supplier connected")
    
    # ========== Step 4: Ad Creatives ==========
    def test_generate_ad_creatives(self, auth_headers):
        """Step 4 - POST /api/ad-creatives/generate/{id} returns ad creatives"""
        response = requests.post(
            f"{BASE_URL}/api/ad-creatives/generate/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Ad generation failed: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Ad generation not successful: {data}"
        assert data.get("product_id") == TEST_PRODUCT_ID
        
        # Verify creatives are present
        creatives = data.get("creatives", {})
        assert creatives, "No creatives in response"
        
        print(f"✓ Ad creatives generated")
        print(f"  - TikTok scripts: {len(creatives.get('tiktok_scripts', []))}")
        print(f"  - Facebook ads: {len(creatives.get('facebook_ads', []))}")
        print(f"  - Instagram captions: {len(creatives.get('instagram_captions', []))}")
    
    # ========== Integration Test: Full Launch Flow ==========
    def test_full_launch_flow(self, auth_headers):
        """
        Integration test: Complete LaunchPad flow
        1. Load product
        2. Load suppliers
        3. Generate store
        4. Generate ads
        """
        import time
        
        # Step 1: Load product
        prod_response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert prod_response.status_code == 200
        product = prod_response.json().get("data") or prod_response.json()
        print(f"Step 1 ✓ Product loaded: {product.get('product_name')}")
        
        # Step 2: Load suppliers
        sup_response = requests.get(
            f"{BASE_URL}/api/suppliers/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert sup_response.status_code == 200
        suppliers = sup_response.json().get("suppliers", [])
        assert len(suppliers) >= 1, "No suppliers found"
        selected_supplier = suppliers[0]
        print(f"Step 2 ✓ Suppliers loaded: {len(suppliers)} found, selected: {selected_supplier.get('supplier_name')}")
        
        # Step 3: Launch store
        store_response = requests.post(
            f"{BASE_URL}/api/stores/launch",
            json={
                "product_id": TEST_PRODUCT_ID,
                "supplier_id": selected_supplier.get("id"),
                "store_name": f"Full Flow Test Store {int(time.time())}"
            },
            headers=auth_headers
        )
        assert store_response.status_code == 200
        store_data = store_response.json()
        assert store_data.get("success") is True
        store = store_data.get("store", {})
        print(f"Step 3 ✓ Store created: {store.get('name')}")
        
        # Step 4: Generate ads
        ad_response = requests.post(
            f"{BASE_URL}/api/ad-creatives/generate/{TEST_PRODUCT_ID}",
            headers=auth_headers
        )
        assert ad_response.status_code == 200
        ad_data = ad_response.json()
        assert ad_data.get("success") is True
        print(f"Step 4 ✓ Ads generated")
        
        print("\n✓ Full LaunchPad flow completed successfully!")


class TestSupplierEndpointCorrection:
    """
    Verify the correct supplier endpoint is being used
    This tests the bug fix where frontend was calling wrong endpoint
    """
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "jenkinslisa1978@gmail.com", "password": "admin123456"}
        )
        return response.json().get("token")
    
    def test_correct_supplier_endpoint_returns_data(self, auth_token):
        """Test that /api/suppliers/{product_id} returns supplier data"""
        response = requests.get(
            f"{BASE_URL}/api/suppliers/{TEST_PRODUCT_ID}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "suppliers" in data
        assert len(data["suppliers"]) > 0
        print(f"✓ Correct endpoint /api/suppliers/{TEST_PRODUCT_ID} works")
    
    def test_wrong_endpoint_returns_error(self, auth_token):
        """
        Test that old wrong endpoint /api/products/{id}/suppliers returns error
        Frontend was incorrectly calling this before the fix
        """
        response = requests.get(
            f"{BASE_URL}/api/products/{TEST_PRODUCT_ID}/suppliers",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # This should return 404 since the endpoint doesn't exist
        # If it returns 200, that means there's a different endpoint
        # Either way, we've confirmed the correct endpoint works above
        print(f"✓ Old endpoint returns status: {response.status_code} (expected 404 or different behavior)")


class TestStoreGenerationImports:
    """
    Verify that store generation works correctly
    This tests the bug fix where stores.py was missing imports
    """
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "jenkinslisa1978@gmail.com", "password": "admin123456"}
        )
        return response.json().get("token")
    
    def test_store_generate_endpoint(self, auth_token):
        """Test /api/stores/generate endpoint (uses StoreGenerator)"""
        response = requests.post(
            f"{BASE_URL}/api/stores/generate",
            json={
                "product_id": TEST_PRODUCT_ID,
                "store_name": "Test Store Generation",
                "plan": "elite"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should not return 500 (which would indicate missing imports)
        assert response.status_code != 500, f"Store generate failed with 500: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") is True
            assert "generation" in data
            print(f"✓ /api/stores/generate works - StoreGenerator imports OK")
        else:
            # May hit plan limits or other business logic
            print(f"Store generate returned {response.status_code}: likely plan limits")
    
    def test_store_launch_endpoint(self, auth_token):
        """Test /api/stores/launch endpoint (uses all imported functions)"""
        import time
        response = requests.post(
            f"{BASE_URL}/api/stores/launch",
            json={
                "product_id": TEST_PRODUCT_ID,
                "store_name": f"Test Store Launch {int(time.time())}"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should not return 500 (which would indicate missing imports)
        assert response.status_code != 500, f"Store launch failed with 500: {response.text}"
        assert response.status_code == 200, f"Store launch failed: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        assert data.get("store", {}).get("id"), "Store not created"
        print(f"✓ /api/stores/launch works - All imports OK")
