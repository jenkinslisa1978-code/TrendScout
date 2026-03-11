"""
Phase 4: One-Click Store Launch Tests
Tests for POST /api/stores/launch and export endpoints (Shopify CSV, WooCommerce)
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_EMAIL = "scrapetest@example.com"
TEST_PASSWORD = "Test1234!"

class TestStoreLaunch:
    """Test suite for Phase 4: One-Click Store Launch feature"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert res.status_code == 200, f"Login failed: {res.text}"
        data = res.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Auth headers for requests"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def test_product(self, headers):
        """Get a product ID for testing"""
        res = requests.get(f"{BASE_URL}/api/products?limit=1", headers=headers)
        assert res.status_code == 200, f"Failed to fetch product: {res.text}"
        data = res.json()
        assert "data" in data and len(data["data"]) > 0, "No products found for testing"
        return data["data"][0]
    
    # =====================
    # Backend Tests: POST /api/stores/launch
    # =====================
    
    def test_launch_store_creates_store(self, headers, test_product):
        """Test 1: POST /api/stores/launch creates a store with all required data"""
        res = requests.post(f"{BASE_URL}/api/stores/launch", headers=headers, json={
            "product_id": test_product["id"]
        })
        
        assert res.status_code == 200, f"Store launch failed: {res.text}"
        data = res.json()
        
        # Verify success
        assert data.get("success") is True, "Launch should return success=True"
        
        # Verify store created
        assert "store" in data, "Response should include store object"
        store = data["store"]
        assert "id" in store, "Store should have an ID"
        assert "name" in store, "Store should have a name"
        assert "shipping_rules" in store, "Store should have shipping_rules"
        assert "supplier_info" in store, "Store should have supplier_info"
        
        print(f"✓ Store created successfully: {store['name']} (ID: {store['id']})")
        return store
    
    def test_launch_response_includes_generation_data(self, headers, test_product):
        """Test 2: Launch response includes generation data with variants"""
        res = requests.post(f"{BASE_URL}/api/stores/launch", headers=headers, json={
            "product_id": test_product["id"]
        })
        
        assert res.status_code == 200, f"Store launch failed: {res.text}"
        data = res.json()
        
        # Verify generation data
        assert "generation" in data, "Response should include generation object"
        gen = data["generation"]
        
        # Verify product variants in generation
        assert "product" in gen, "Generation should include product"
        product_gen = gen["product"]
        assert "variants" in product_gen, "Generated product should include variants"
        variants = product_gen["variants"]
        assert isinstance(variants, list), "Variants should be a list"
        assert len(variants) > 0, "Should have at least one variant"
        
        print(f"✓ Generation includes product variants: {variants}")
    
    def test_launch_response_includes_shipping_rules(self, headers, test_product):
        """Test 2b: Launch response includes shipping rules"""
        res = requests.post(f"{BASE_URL}/api/stores/launch", headers=headers, json={
            "product_id": test_product["id"]
        })
        
        assert res.status_code == 200
        data = res.json()
        store = data["store"]
        
        # Verify shipping rules structure
        shipping = store.get("shipping_rules", {})
        assert "standard" in shipping, "Shipping should have standard option"
        assert "express" in shipping, "Shipping should have express option"
        
        standard = shipping["standard"]
        assert "name" in standard, "Standard shipping should have name"
        assert "price" in standard, "Standard shipping should have price"
        assert "estimated_days" in standard, "Standard shipping should have estimated_days"
        
        print(f"✓ Shipping rules: standard={standard['price']}, express={shipping['express']['price']}")
    
    def test_launch_response_includes_supplier_info(self, headers, test_product):
        """Test 2c: Launch response includes supplier info"""
        res = requests.post(f"{BASE_URL}/api/stores/launch", headers=headers, json={
            "product_id": test_product["id"]
        })
        
        assert res.status_code == 200
        data = res.json()
        store = data["store"]
        
        supplier_info = store.get("supplier_info", {})
        # Supplier may be null if no supplier was found, but the field should exist
        assert "supplier_info" in store, "Store should have supplier_info field"
        
        print(f"✓ Supplier info present: {supplier_info}")
    
    def test_store_product_includes_supplier_data(self, headers, test_product):
        """Test 9: Store product document includes supplier fields"""
        res = requests.post(f"{BASE_URL}/api/stores/launch", headers=headers, json={
            "product_id": test_product["id"]
        })
        
        assert res.status_code == 200
        data = res.json()
        
        # Verify product document
        assert "product" in data, "Response should include product document"
        product = data["product"]
        
        # Check supplier fields in store product
        assert "supplier_id" in product, "Store product should have supplier_id"
        assert "supplier_source" in product, "Store product should have supplier_source"
        assert "supplier_cost" in product, "Store product should have supplier_cost"
        assert "variants" in product, "Store product should have variants"
        
        print(f"✓ Store product has supplier fields: source={product.get('supplier_source')}, cost={product.get('supplier_cost')}")
    
    # =====================
    # Backend Tests: Export endpoints
    # =====================
    
    def test_export_shopify_csv(self, headers, test_product):
        """Test 3: GET /api/stores/{store_id}/export?format=shopify_csv returns CSV"""
        # First launch a store
        launch_res = requests.post(f"{BASE_URL}/api/stores/launch", headers=headers, json={
            "product_id": test_product["id"]
        })
        assert launch_res.status_code == 200
        store_id = launch_res.json()["store"]["id"]
        
        # Export as CSV
        res = requests.get(f"{BASE_URL}/api/stores/{store_id}/export?format=shopify_csv", headers=headers)
        
        assert res.status_code == 200, f"CSV export failed: {res.text}"
        assert "text/csv" in res.headers.get("Content-Type", ""), "Should return CSV content type"
        assert "Content-Disposition" in res.headers, "Should have Content-Disposition header"
        
        # Verify CSV content has Shopify headers
        csv_content = res.text
        assert "Handle" in csv_content, "CSV should have Handle header"
        assert "Title" in csv_content, "CSV should have Title header"
        assert "Body (HTML)" in csv_content, "CSV should have Body (HTML) header"
        assert "Vendor" in csv_content, "CSV should have Vendor header"
        
        print(f"✓ Shopify CSV export works, headers present")
    
    def test_export_woocommerce_json(self, headers, test_product):
        """Test 4: GET /api/stores/{store_id}/export?format=woocommerce returns WooCommerce JSON"""
        # First launch a store
        launch_res = requests.post(f"{BASE_URL}/api/stores/launch", headers=headers, json={
            "product_id": test_product["id"]
        })
        assert launch_res.status_code == 200
        store_id = launch_res.json()["store"]["id"]
        
        # Export as WooCommerce
        res = requests.get(f"{BASE_URL}/api/stores/{store_id}/export?format=woocommerce", headers=headers)
        
        assert res.status_code == 200, f"WooCommerce export failed: {res.text}"
        data = res.json()
        
        # Verify WooCommerce format
        assert "export_format" in data, "Should have export_format field"
        assert data["export_format"] == "woocommerce_rest_api_v3", f"Export format should be woocommerce_rest_api_v3, got {data['export_format']}"
        assert "products" in data, "Should have products array"
        
        if len(data["products"]) > 0:
            product = data["products"][0]
            assert "type" in product, "Product should have type field"
            assert product["type"] in ["simple", "variable"], f"Product type should be simple or variable, got {product['type']}"
        
        print(f"✓ WooCommerce export works, format={data['export_format']}")
    
    def test_export_shopify_json(self, headers, test_product):
        """Test 3b: GET /api/stores/{store_id}/export?format=shopify returns Shopify JSON"""
        # First launch a store
        launch_res = requests.post(f"{BASE_URL}/api/stores/launch", headers=headers, json={
            "product_id": test_product["id"]
        })
        assert launch_res.status_code == 200
        store_id = launch_res.json()["store"]["id"]
        
        # Export as Shopify JSON
        res = requests.get(f"{BASE_URL}/api/stores/{store_id}/export?format=shopify", headers=headers)
        
        assert res.status_code == 200, f"Shopify JSON export failed: {res.text}"
        data = res.json()
        
        assert "export_format" in data, "Should have export_format field"
        assert "shopify" in data["export_format"].lower(), f"Export format should contain shopify, got {data['export_format']}"
        assert "products" in data, "Should have products array"
        
        print(f"✓ Shopify JSON export works, format={data['export_format']}")


class TestStoreLaunchValidation:
    """Validation tests for store launch"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert res.status_code == 200, f"Login failed: {res.text}"
        return res.json().get("access_token") or res.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_launch_requires_auth(self):
        """Test: Launch endpoint requires authentication"""
        res = requests.post(f"{BASE_URL}/api/stores/launch", json={"product_id": "test"})
        assert res.status_code in [401, 403], "Should reject unauthenticated requests"
        print("✓ Launch requires authentication")
    
    def test_launch_invalid_product(self, headers):
        """Test: Launch with invalid product_id returns 404"""
        res = requests.post(f"{BASE_URL}/api/stores/launch", headers=headers, json={
            "product_id": "non-existent-product-id"
        })
        assert res.status_code == 404, f"Should return 404 for invalid product, got {res.status_code}"
        print("✓ Launch with invalid product returns 404")


class TestStoreDetailAPI:
    """Tests for store detail endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return res.json().get("access_token") or res.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    @pytest.fixture(scope="class")
    def created_store(self, headers):
        """Create a store for testing"""
        # Get a product
        res = requests.get(f"{BASE_URL}/api/products?limit=1", headers=headers)
        product = res.json()["data"][0]
        
        # Launch store
        res = requests.post(f"{BASE_URL}/api/stores/launch", headers=headers, json={
            "product_id": product["id"]
        })
        return res.json()["store"]
    
    def test_get_store_detail(self, headers, created_store):
        """Test: GET /api/stores/{store_id} returns store with shipping and supplier"""
        res = requests.get(f"{BASE_URL}/api/stores/{created_store['id']}", headers=headers)
        
        assert res.status_code == 200, f"Failed to get store detail: {res.text}"
        response = res.json()
        
        # Response is wrapped in "data"
        data = response.get("data", response)
        
        # Verify store has shipping rules
        assert "shipping_rules" in data, "Store should have shipping_rules"
        
        # Verify store has supplier info
        assert "supplier_info" in data, "Store should have supplier_info"
        
        # Verify store has products
        assert "products" in data, "Store should have products"
        
        print(f"✓ Store detail includes shipping_rules and supplier_info")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
