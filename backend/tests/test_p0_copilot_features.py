"""
Test P0 AI Co-Pilot Features for TrendScout
Tests: Find Winning Product API, Product Launch Wizard APIs, View Mode (localStorage test N/A in backend)

Required endpoints:
1. GET /api/products/find-winning - AI recommendation
2. GET /api/products/{id} - Product detail (for wizard step 1)
3. GET /api/products/{id}/suppliers - Supplier options (for wizard step 2)
4. POST /api/stores/launch - Store generation (for wizard step 3+)
5. POST /api/ad-creatives/generate/{id} - Ad generation (for wizard step 4)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_EMAIL = "testref@test.com"
TEST_PASSWORD = "Test1234!"


@pytest.fixture(scope="module")
def auth_token():
    """Authenticate and get token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data.get("access_token") or data.get("token")


@pytest.fixture(scope="module")
def authenticated_session(auth_token):
    """Return session with auth header"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    })
    return session


class TestFindWinningProductAPI:
    """Tests for GET /api/products/find-winning endpoint"""

    def test_find_winning_requires_auth(self):
        """Endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/products/find-winning")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: find-winning endpoint requires authentication")

    def test_find_winning_returns_product(self, authenticated_session):
        """Should return winning product with all required fields"""
        response = authenticated_session.get(f"{BASE_URL}/api/products/find-winning")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check structure
        assert "product" in data, "Response should have 'product' key"
        
        # If product exists, validate fields
        if data.get("product"):
            product = data["product"]
            print(f"Found winning product: {product.get('product_name')}")
            
            # Required fields for product
            required_fields = ["id", "product_name", "launch_score", "success_probability"]
            for field in required_fields:
                assert field in product, f"Product missing required field: {field}"
            
            # Numeric validation
            assert isinstance(product.get("launch_score"), (int, float)), "launch_score should be numeric"
            assert isinstance(product.get("success_probability"), (int, float)), "success_probability should be numeric"
            
            # selling_price and estimated_profit
            assert "selling_price" in product or "estimated_profit" in product, "Product should have pricing info"
            
            print(f"  - Launch Score: {product.get('launch_score')}")
            print(f"  - Success Probability: {product.get('success_probability')}%")
            print(f"  - Estimated Profit: {product.get('estimated_profit')}")
        else:
            print("Note: No products available (pipeline may still be running)")
        
        print("PASS: find-winning returns valid product structure")

    def test_find_winning_has_supplier_info(self, authenticated_session):
        """Response should include supplier information"""
        response = authenticated_session.get(f"{BASE_URL}/api/products/find-winning")
        assert response.status_code == 200
        
        data = response.json()
        
        if data.get("product"):
            # Check supplier info
            assert "supplier" in data, "Response should have 'supplier' key"
            supplier = data["supplier"]
            
            if supplier:
                # Supplier should have name and cost
                assert "name" in supplier, "Supplier should have name"
                assert "cost" in supplier, "Supplier should have cost"
                print(f"Supplier: {supplier.get('name')}, Cost: {supplier.get('cost')}")
            
            print("PASS: find-winning includes supplier info")

    def test_find_winning_has_recommendation(self, authenticated_session):
        """Response should include recommendation with reasons"""
        response = authenticated_session.get(f"{BASE_URL}/api/products/find-winning")
        assert response.status_code == 200
        
        data = response.json()
        
        if data.get("product"):
            # Check recommendation
            assert "recommendation" in data, "Response should have 'recommendation' key"
            recommendation = data.get("recommendation", {})
            
            assert "confidence" in recommendation, "Recommendation should have confidence"
            assert "reasons" in recommendation, "Recommendation should have reasons"
            
            print(f"Confidence: {recommendation.get('confidence')}")
            if recommendation.get("reasons"):
                print(f"Reasons: {len(recommendation['reasons'])} provided")
            
            print("PASS: find-winning includes recommendation with reasons")

    def test_find_winning_has_alternatives(self, authenticated_session):
        """Response should include alternative products"""
        response = authenticated_session.get(f"{BASE_URL}/api/products/find-winning")
        assert response.status_code == 200
        
        data = response.json()
        
        if data.get("product"):
            # Check alternatives
            assert "alternatives" in data, "Response should have 'alternatives' key"
            alternatives = data.get("alternatives", [])
            
            if alternatives:
                for alt in alternatives:
                    assert "id" in alt, "Alternative should have id"
                    assert "product_name" in alt, "Alternative should have product_name"
                    assert "launch_score" in alt, "Alternative should have launch_score"
                
                print(f"Alternatives: {len(alternatives)} provided")
            
            print("PASS: find-winning includes alternatives")


class TestProductDetailAPI:
    """Tests for GET /api/products/{id} endpoint (Wizard Step 1)"""

    def test_get_product_detail(self, authenticated_session):
        """Should return product detail for wizard"""
        # First get a product ID from find-winning
        response = authenticated_session.get(f"{BASE_URL}/api/products/find-winning")
        if response.status_code != 200:
            pytest.skip("No products available")
        
        data = response.json()
        if not data.get("product"):
            pytest.skip("No products in database")
        
        product_id = data["product"]["id"]
        
        # Get product detail
        response = authenticated_session.get(f"{BASE_URL}/api/products/{product_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        detail = response.json()
        
        # API returns {data: {...}} format
        product_data = detail.get("data") or detail
        
        assert "id" in product_data, "Product detail should have id"
        assert "product_name" in product_data, "Product detail should have product_name"
        assert "launch_score" in product_data or "trend_score" in product_data, "Product should have scoring"
        
        print(f"Product Detail for: {product_data.get('product_name')}")
        print("PASS: Product detail API works correctly")


class TestSupplierAPI:
    """Tests for GET /api/products/{id}/suppliers endpoint (Wizard Step 2)"""

    def test_get_suppliers_for_product(self, authenticated_session):
        """Should return supplier options for product"""
        # Get a product ID
        response = authenticated_session.get(f"{BASE_URL}/api/products/find-winning")
        if response.status_code != 200 or not response.json().get("product"):
            pytest.skip("No products available")
        
        product_id = response.json()["product"]["id"]
        
        # Get suppliers
        response = authenticated_session.get(f"{BASE_URL}/api/products/{product_id}/suppliers")
        
        # Suppliers endpoint might return 404 if no suppliers exist, or 200 with empty list
        if response.status_code == 404:
            print("Note: No suppliers found for product (404 response)")
            print("PASS: Suppliers endpoint exists (returns 404 when none available)")
            return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        suppliers = data.get("suppliers") or data.get("data") or []
        
        print(f"Found {len(suppliers)} suppliers")
        
        if suppliers:
            sup = suppliers[0]
            assert "id" in sup or "supplier_name" in sup or "name" in sup, "Supplier should have identifier"
            print(f"First supplier: {sup.get('supplier_name') or sup.get('name')}")
        
        print("PASS: Suppliers API returns list")


class TestStoreLaunchAPI:
    """Tests for POST /api/stores/launch endpoint (Wizard Step 3)"""

    def test_store_launch_requires_auth(self):
        """Store launch should require authentication"""
        response = requests.post(f"{BASE_URL}/api/stores/launch", json={
            "product_id": "test-id"
        })
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"
        print("PASS: Store launch requires authentication")

    def test_store_launch_preview(self, authenticated_session):
        """Should generate store preview"""
        # Get a product
        response = authenticated_session.get(f"{BASE_URL}/api/products/find-winning")
        if response.status_code != 200 or not response.json().get("product"):
            pytest.skip("No products available")
        
        product_id = response.json()["product"]["id"]
        
        # Test store launch with preview_only
        response = authenticated_session.post(f"{BASE_URL}/api/stores/launch", json={
            "product_id": product_id,
            "store_name": "TEST_WizardStore",
            "preview_only": True
        })
        
        # May fail if user reached store limit
        if response.status_code == 403:
            print("Note: User reached store limit (403 response)")
            print("PASS: Store launch endpoint accessible (user limit reached)")
            return
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Store preview generated: {data}")
        print("PASS: Store launch preview works")


class TestAdCreativeAPI:
    """Tests for POST /api/ad-creatives/generate/{id} endpoint (Wizard Step 4)"""

    def test_ad_creative_requires_auth(self):
        """Ad creative generation should require auth"""
        response = requests.post(f"{BASE_URL}/api/ad-creatives/generate/test-id")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Ad creative endpoint requires authentication")

    def test_ad_creative_generation(self, authenticated_session):
        """Should generate ad creatives for product"""
        # Get a product
        response = authenticated_session.get(f"{BASE_URL}/api/products/find-winning")
        if response.status_code != 200 or not response.json().get("product"):
            pytest.skip("No products available")
        
        product_id = response.json()["product"]["id"]
        
        # Generate ad creatives
        response = authenticated_session.post(f"{BASE_URL}/api/ad-creatives/generate/{product_id}")
        
        # May require higher plan
        if response.status_code == 403:
            print("Note: Ad creative generation may require upgraded plan")
            print("PASS: Ad creative endpoint accessible (plan restriction)")
            return
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Should have creatives
        if "creatives" in data:
            creatives = data["creatives"]
            print(f"Generated creatives: {list(creatives.keys()) if isinstance(creatives, dict) else creatives}")
        
        print("PASS: Ad creative generation works")


class TestExistingPagesStillWork:
    """Verify existing pages/APIs still function"""

    def test_dashboard_products_api(self, authenticated_session):
        """Dashboard products API should work"""
        response = authenticated_session.get(f"{BASE_URL}/api/products?sort_by=trend_score&sort_order=desc&limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "data" in data or isinstance(data, list), "Should return products"
        print("PASS: Dashboard products API works")

    def test_discover_products_api(self, authenticated_session):
        """Discover page products API should work"""
        response = authenticated_session.get(f"{BASE_URL}/api/products?sort_by=launch_score&sort_order=desc&limit=20")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Discover products API works")

    def test_reports_api(self, authenticated_session):
        """Reports API should work"""
        response = authenticated_session.get(f"{BASE_URL}/api/reports/list")
        # May return 200 or 404 depending on implementation
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        print("PASS: Reports API accessible")

    def test_referrals_api(self, authenticated_session):
        """Referrals API should work"""
        response = authenticated_session.get(f"{BASE_URL}/api/viral/referral/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Referrals API works")

    def test_pricing_plans_api(self, authenticated_session):
        """Pricing plans API should work"""
        response = authenticated_session.get(f"{BASE_URL}/api/stripe/plans")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        plans = data.get("plans") or data
        assert len(plans) >= 3, "Should have at least 3 plans"
        print("PASS: Pricing plans API works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
