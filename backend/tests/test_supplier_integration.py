"""
Supplier Integration API Tests

Tests the supplier discovery, listing, and selection features for Phase 3.
Covers:
- GET /api/suppliers/{product_id} - Get/auto-discover suppliers
- POST /api/suppliers/{product_id}/find - Force refresh suppliers
- POST /api/suppliers/{product_id}/select/{supplier_id} - Select a supplier
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSupplierIntegration:
    """Tests for supplier integration endpoints"""
    
    @pytest.fixture(scope="class")
    def product_id(self):
        """Get a product ID for testing"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 1})
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data and len(data['data']) > 0
        return data['data'][0]['id']
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for authenticated tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "scrapetest@example.com",
            "password": "Test1234!"
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    # =====================
    # TEST: GET /api/suppliers/{product_id}
    # =====================
    
    def test_get_suppliers_auto_discovers(self, product_id):
        """Test GET /api/suppliers/{product_id} auto-discovers suppliers for products with none"""
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Response data: {data}")
        
        # Should have suppliers_found and suppliers list
        assert 'suppliers_found' in data
        assert 'suppliers' in data
        assert isinstance(data['suppliers'], list)
    
    def test_get_suppliers_returns_two_sources(self, product_id):
        """Test that GET returns both AliExpress and CJ Dropshipping suppliers"""
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response.status_code == 200
        
        data = response.json()
        suppliers = data.get('suppliers', [])
        
        # Should have at least 2 suppliers (AliExpress + CJ)
        assert len(suppliers) >= 2, f"Expected at least 2 suppliers, got {len(suppliers)}"
        
        # Check sources
        sources = [s.get('source') for s in suppliers]
        assert 'aliexpress' in sources, f"AliExpress source not found. Sources: {sources}"
        assert 'cj_dropshipping' in sources, f"CJ Dropshipping source not found. Sources: {sources}"
    
    def test_supplier_listing_has_required_fields(self, product_id):
        """Test each supplier listing has all required fields"""
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response.status_code == 200
        
        data = response.json()
        suppliers = data.get('suppliers', [])
        
        required_fields = [
            'id', 'source', 'supplier_name', 'supplier_cost',
            'estimated_shipping_cost', 'shipping_origin',
            'shipping_days_min', 'shipping_days_max', 'confidence', 'supplier_url'
        ]
        
        for supplier in suppliers:
            for field in required_fields:
                assert field in supplier, f"Missing field '{field}' in supplier: {supplier}"
            
            # Verify data types
            assert isinstance(supplier['id'], str)
            assert supplier['source'] in ['aliexpress', 'cj_dropshipping']
            assert isinstance(supplier['supplier_name'], str)
            assert isinstance(supplier['supplier_cost'], (int, float))
            assert isinstance(supplier['estimated_shipping_cost'], (int, float))
            assert isinstance(supplier['shipping_origin'], str)
            assert isinstance(supplier['shipping_days_min'], int)
            assert isinstance(supplier['shipping_days_max'], int)
            assert supplier['confidence'] in ['estimated', 'verified', 'scraped', 'matched']
            assert isinstance(supplier['supplier_url'], str)
            
            print(f"Supplier: {supplier['source']} - {supplier['supplier_name']}")
            print(f"  Cost: ${supplier['supplier_cost']}, Shipping: ${supplier['estimated_shipping_cost']}")
            print(f"  Origin: {supplier['shipping_origin']}, Delivery: {supplier['shipping_days_min']}-{supplier['shipping_days_max']} days")
            print(f"  Confidence: {supplier['confidence']}")
    
    def test_aliexpress_supplier_data(self, product_id):
        """Test AliExpress supplier has correct data"""
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response.status_code == 200
        
        data = response.json()
        suppliers = data.get('suppliers', [])
        
        aliexpress = next((s for s in suppliers if s['source'] == 'aliexpress'), None)
        assert aliexpress is not None, "AliExpress supplier not found"
        
        # AliExpress specific validations
        assert aliexpress['supplier_name'] == 'AliExpress Marketplace'
        assert 'aliexpress' in aliexpress['supplier_url'].lower()
        assert aliexpress['shipping_origin'] == 'China'
        assert aliexpress['shipping_days_min'] == 7
        assert aliexpress['shipping_days_max'] == 20
    
    def test_cj_dropshipping_supplier_data(self, product_id):
        """Test CJ Dropshipping supplier has correct data"""
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response.status_code == 200
        
        data = response.json()
        suppliers = data.get('suppliers', [])
        
        cj = next((s for s in suppliers if s['source'] == 'cj_dropshipping'), None)
        assert cj is not None, "CJ Dropshipping supplier not found"
        
        # CJ specific validations
        assert cj['supplier_name'] == 'CJ Dropshipping'
        assert 'cjdropshipping' in cj['supplier_url'].lower()
        assert 'China' in cj['shipping_origin'] or 'US' in cj['shipping_origin']
        assert cj['shipping_days_min'] == 5
        assert cj['shipping_days_max'] == 15
    
    def test_invalid_product_id_returns_error(self):
        """Test that invalid product ID returns error"""
        response = requests.get(f"{BASE_URL}/api/suppliers/invalid-product-id-12345")
        assert response.status_code == 200  # Returns 200 with error message
        
        data = response.json()
        assert 'error' in data or data.get('suppliers_found', 0) == 0
    
    # =====================
    # TEST: POST /api/suppliers/{product_id}/find
    # =====================
    
    def test_find_suppliers_refreshes_data(self, product_id):
        """Test POST /api/suppliers/{product_id}/find refreshes supplier listings"""
        response = requests.post(f"{BASE_URL}/api/suppliers/{product_id}/find")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Should return refreshed suppliers
        assert 'suppliers_found' in data
        assert 'suppliers' in data
        assert len(data['suppliers']) >= 2
        
        # Should not be cached
        assert data.get('cached', False) is False, "Expected fresh data, not cached"
    
    def test_find_suppliers_returns_fresh_ids(self, product_id):
        """Test that find generates new supplier IDs (deletes old ones)"""
        # Get current suppliers
        response1 = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response1.status_code == 200
        old_ids = [s['id'] for s in response1.json().get('suppliers', [])]
        
        # Force refresh
        response2 = requests.post(f"{BASE_URL}/api/suppliers/{product_id}/find")
        assert response2.status_code == 200
        new_ids = [s['id'] for s in response2.json().get('suppliers', [])]
        
        # IDs should be different (new records created)
        # Note: Only check if there were old suppliers with IDs
        if old_ids:
            assert not any(nid in old_ids for nid in new_ids), \
                "Expected new supplier IDs after refresh"
    
    # =====================
    # TEST: POST /api/suppliers/{product_id}/select/{supplier_id}
    # =====================
    
    def test_select_supplier_works(self, product_id, auth_token):
        """Test POST /api/suppliers/{product_id}/select/{supplier_id} selects a supplier"""
        # First get suppliers
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response.status_code == 200
        suppliers = response.json().get('suppliers', [])
        assert len(suppliers) >= 1, "No suppliers to select"
        
        supplier_id = suppliers[0]['id']
        
        # Select the supplier
        headers = {}
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        select_response = requests.post(
            f"{BASE_URL}/api/suppliers/{product_id}/select/{supplier_id}",
            headers=headers
        )
        assert select_response.status_code == 200, f"Expected 200, got {select_response.status_code}: {select_response.text}"
        
        data = select_response.json()
        assert data.get('success') is True or 'supplier' in data
    
    def test_select_supplier_deselects_others(self, product_id, auth_token):
        """Test selecting a supplier deselects other suppliers"""
        # Get suppliers
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response.status_code == 200
        suppliers = response.json().get('suppliers', [])
        assert len(suppliers) >= 2, "Need at least 2 suppliers for this test"
        
        # Select the second supplier
        supplier_id = suppliers[1]['id']
        headers = {}
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        select_response = requests.post(
            f"{BASE_URL}/api/suppliers/{product_id}/select/{supplier_id}",
            headers=headers
        )
        assert select_response.status_code == 200
        
        # Verify GET shows only one selected
        verify_response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert verify_response.status_code == 200
        
        verified_suppliers = verify_response.json().get('suppliers', [])
        selected_count = sum(1 for s in verified_suppliers if s.get('is_selected', False))
        
        assert selected_count == 1, f"Expected exactly 1 selected supplier, got {selected_count}"
        
        # Verify the correct one is selected
        selected_supplier = next((s for s in verified_suppliers if s.get('is_selected')), None)
        assert selected_supplier is not None, "No supplier is selected"
        assert selected_supplier['id'] == supplier_id, "Wrong supplier selected"
    
    def test_select_invalid_supplier_returns_error(self, product_id, auth_token):
        """Test selecting an invalid supplier ID returns error"""
        headers = {}
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        response = requests.post(
            f"{BASE_URL}/api/suppliers/{product_id}/select/invalid-supplier-id",
            headers=headers
        )
        assert response.status_code == 200  # Returns 200 with error message
        
        data = response.json()
        assert 'error' in data or data.get('success', True) is False
    
    # =====================
    # TEST: Supplier listing structure
    # =====================
    
    def test_supplier_confidence_badges(self, product_id):
        """Test supplier confidence values are one of: estimated, verified, scraped, matched"""
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response.status_code == 200
        
        suppliers = response.json().get('suppliers', [])
        valid_confidence = ['estimated', 'verified', 'scraped', 'matched']
        
        for supplier in suppliers:
            assert supplier.get('confidence') in valid_confidence, \
                f"Invalid confidence value: {supplier.get('confidence')}"
            
            # Confidence note should explain the confidence level
            if supplier.get('confidence') == 'estimated':
                assert supplier.get('confidence_note'), "Estimated confidence should have a note"
    
    def test_supplier_urls_are_valid(self, product_id):
        """Test supplier URLs point to correct platforms"""
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}")
        assert response.status_code == 200
        
        suppliers = response.json().get('suppliers', [])
        
        for supplier in suppliers:
            url = supplier.get('supplier_url', '')
            source = supplier.get('source')
            
            if source == 'aliexpress':
                assert 'aliexpress' in url.lower(), f"AliExpress URL invalid: {url}"
            elif source == 'cj_dropshipping':
                assert 'cjdropshipping' in url.lower(), f"CJ URL invalid: {url}"


class TestSupplierAPIHealth:
    """Basic health checks for supplier API"""
    
    def test_api_health(self):
        """Test API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
    
    def test_products_endpoint_works(self):
        """Test products endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/products", params={"limit": 1})
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
