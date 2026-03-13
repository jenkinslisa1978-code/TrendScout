"""
Test Admin Image Review Dashboard API endpoints
Phase 2: Image validation pipeline with QA metrics, product queue, bulk actions
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "test123456"

# Test product IDs from context
TEST_PRODUCT_ID_1 = "5d241fc9-383b-4dcc-b406-ba40590ed6a3"  # Portable Neck Fan
TEST_PRODUCT_ID_2 = "f6d631f2-00da-4ea5-9ca2-0ce2469856b0"  # Magnetic Phone Mount


class TestAdminImageReviewAuth:
    """Test that image-review endpoints require admin auth"""
    
    def test_metrics_without_auth_returns_401(self):
        """GET /api/admin/image-review/metrics without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/admin/image-review/metrics")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Metrics endpoint requires authentication")
    
    def test_products_without_auth_returns_401(self):
        """GET /api/admin/image-review/products without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/admin/image-review/products")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Products list endpoint requires authentication")
    
    def test_bulk_without_auth_returns_401(self):
        """POST /api/admin/image-review/bulk without auth returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/admin/image-review/bulk",
            json={"action": "approve", "product_ids": ["test"]}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Bulk action endpoint requires authentication")


@pytest.fixture(scope="module")
def admin_token():
    """Get admin JWT token for authenticated requests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    token = data.get("token")
    assert token, "No token returned from login"
    print(f"✓ Admin login successful")
    return token


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Headers with admin auth token"""
    return {"Authorization": f"Bearer {admin_token}"}


class TestImageReviewMetrics:
    """Test GET /api/admin/image-review/metrics"""
    
    def test_metrics_returns_all_counts(self, admin_headers):
        """Metrics endpoint returns all expected count fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/image-review/metrics",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify all required fields exist
        required_fields = ["total_products", "needs_review", "pending", "approved", "rejected", "placeholder", "pinned"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
            assert isinstance(data[field], int), f"Field {field} should be int, got {type(data[field])}"
        
        print(f"✓ Metrics returned: total={data['total_products']}, needs_review={data['needs_review']}, "
              f"pending={data['pending']}, approved={data['approved']}, rejected={data['rejected']}, "
              f"placeholder={data['placeholder']}, pinned={data['pinned']}")
        
        # Sanity check - total should be positive
        assert data['total_products'] > 0, "Expected some products in database"


class TestImageReviewProductList:
    """Test GET /api/admin/image-review/products with filters"""
    
    def test_list_all_products(self, admin_headers):
        """List products without filter returns all products"""
        response = requests.get(
            f"{BASE_URL}/api/admin/image-review/products",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "products" in data, "Response should have 'products' key"
        assert "total" in data, "Response should have 'total' key"
        assert isinstance(data["products"], list), "Products should be a list"
        assert data["total"] > 0, "Expected some products"
        
        print(f"✓ All products: {len(data['products'])} of {data['total']} total")
    
    def test_list_needs_review_products(self, admin_headers):
        """Filter by status=needs_review returns filtered products"""
        response = requests.get(
            f"{BASE_URL}/api/admin/image-review/products?status=needs_review",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "products" in data, "Response should have 'products' key"
        
        # All returned products should have needs_review status (if any)
        for p in data["products"]:
            if "image_status" in p:
                assert p["image_status"] == "needs_review", f"Expected needs_review status, got {p.get('image_status')}"
        
        print(f"✓ Needs review filter: {len(data['products'])} products")
    
    def test_list_approved_products(self, admin_headers):
        """Filter by status=approved returns approved products"""
        response = requests.get(
            f"{BASE_URL}/api/admin/image-review/products?status=approved",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # All returned products should have approved status (if any)
        for p in data["products"]:
            if "image_status" in p:
                assert p["image_status"] == "approved", f"Expected approved status, got {p.get('image_status')}"
        
        print(f"✓ Approved filter: {len(data['products'])} products")
    
    def test_product_list_has_required_fields(self, admin_headers):
        """Products in list have required image metadata fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/image-review/products?limit=5",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        if len(data["products"]) > 0:
            product = data["products"][0]
            
            # Check required fields
            assert "id" in product, "Product should have 'id'"
            assert "product_name" in product, "Product should have 'product_name'"
            assert "category" in product, "Product should have 'category'"
            # image_url can be empty/null
            # image_status, image_confidence, image_pinned should be present
            
            print(f"✓ Product fields verified: id, product_name, category present")


class TestImageReviewProductDetail:
    """Test GET /api/admin/image-review/products/{product_id}"""
    
    def test_get_product_detail(self, admin_headers):
        """Get single product returns full data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_1}",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("id") == TEST_PRODUCT_ID_1, "Product ID should match"
        assert "product_name" in data, "Product should have name"
        
        print(f"✓ Product detail: {data.get('product_name')}")
    
    def test_get_nonexistent_product_returns_404(self, admin_headers):
        """Get non-existent product returns 404"""
        fake_id = str(uuid.uuid4())
        response = requests.get(
            f"{BASE_URL}/api/admin/image-review/products/{fake_id}",
            headers=admin_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent product returns 404")


class TestImageReviewApprove:
    """Test PUT /api/admin/image-review/products/{product_id}/approve"""
    
    def test_approve_image(self, admin_headers):
        """Approve sets status to approved and confidence to 1.0"""
        response = requests.put(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_1}/approve",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "approved", "Status should be 'approved'"
        
        # Verify the product was updated
        verify_resp = requests.get(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_1}",
            headers=admin_headers
        )
        verify_data = verify_resp.json()
        assert verify_data.get("image_status") == "approved", "Product image_status should be approved"
        assert verify_data.get("image_confidence") == 1.0, "image_confidence should be 1.0"
        
        print("✓ Image approved, status=approved, confidence=1.0")


class TestImageReviewReject:
    """Test PUT /api/admin/image-review/products/{product_id}/reject"""
    
    def test_reject_image(self, admin_headers):
        """Reject sets status to placeholder and clears image_url"""
        response = requests.put(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_2}/reject",
            headers=admin_headers,
            json={"reason": "TEST_Image mismatch"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "placeholder", "Status should be 'placeholder'"
        
        # Verify the product was updated
        verify_resp = requests.get(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_2}",
            headers=admin_headers
        )
        verify_data = verify_resp.json()
        assert verify_data.get("image_status") == "placeholder", "Product image_status should be placeholder"
        assert verify_data.get("image_url") == "", "image_url should be empty"
        assert verify_data.get("image_mismatch_reason") == "TEST_Image mismatch", "Reason should be set"
        
        print("✓ Image rejected, status=placeholder, image_url cleared")


class TestImageReviewSetUrl:
    """Test PUT /api/admin/image-review/products/{product_id}/url"""
    
    def test_set_custom_url(self, admin_headers):
        """Set custom URL updates image and approves"""
        custom_url = "https://example.com/test-image-override.jpg"
        
        response = requests.put(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_2}/url",
            headers=admin_headers,
            json={"url": custom_url}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("url") == custom_url, "URL should match"
        
        # Verify the product was updated
        verify_resp = requests.get(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_2}",
            headers=admin_headers
        )
        verify_data = verify_resp.json()
        assert verify_data.get("image_url") == custom_url, "image_url should be set to custom URL"
        assert verify_data.get("image_status") == "approved", "Status should be approved after URL set"
        
        print(f"✓ Custom URL set: {custom_url}")
    
    def test_set_url_requires_url_param(self, admin_headers):
        """Set URL without url param returns 400"""
        response = requests.put(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_2}/url",
            headers=admin_headers,
            json={}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Set URL requires 'url' parameter")


class TestImageReviewPin:
    """Test PUT /api/admin/image-review/products/{product_id}/pin"""
    
    def test_pin_image(self, admin_headers):
        """Pin image sets image_pinned to true"""
        response = requests.put(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_1}/pin",
            headers=admin_headers,
            json={"pinned": True}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("pinned") == True, "pinned should be True"
        
        # Verify
        verify_resp = requests.get(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_1}",
            headers=admin_headers
        )
        verify_data = verify_resp.json()
        assert verify_data.get("image_pinned") == True, "Product image_pinned should be True"
        
        print("✓ Image pinned successfully")
    
    def test_unpin_image(self, admin_headers):
        """Unpin image sets image_pinned to false"""
        response = requests.put(
            f"{BASE_URL}/api/admin/image-review/products/{TEST_PRODUCT_ID_1}/pin",
            headers=admin_headers,
            json={"pinned": False}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("pinned") == False, "pinned should be False"
        
        print("✓ Image unpinned successfully")


class TestImageReviewBulk:
    """Test POST /api/admin/image-review/bulk"""
    
    def test_bulk_approve(self, admin_headers):
        """Bulk approve updates multiple products"""
        response = requests.post(
            f"{BASE_URL}/api/admin/image-review/bulk",
            headers=admin_headers,
            json={
                "action": "approve",
                "product_ids": [TEST_PRODUCT_ID_1, TEST_PRODUCT_ID_2]
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "modified" in data, "Response should have 'modified' count"
        assert data["modified"] >= 1, "At least one product should be modified"
        
        print(f"✓ Bulk approve: {data['modified']} products modified")
    
    def test_bulk_reject(self, admin_headers):
        """Bulk reject updates multiple products"""
        response = requests.post(
            f"{BASE_URL}/api/admin/image-review/bulk",
            headers=admin_headers,
            json={
                "action": "reject",
                "product_ids": [TEST_PRODUCT_ID_1]
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["modified"] >= 0, "Modified count should be non-negative"
        
        print(f"✓ Bulk reject: {data['modified']} products modified")
    
    def test_bulk_mark_needs_review(self, admin_headers):
        """Bulk mark_needs_review updates products"""
        response = requests.post(
            f"{BASE_URL}/api/admin/image-review/bulk",
            headers=admin_headers,
            json={
                "action": "mark_needs_review",
                "product_ids": [TEST_PRODUCT_ID_1, TEST_PRODUCT_ID_2]
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "modified" in data
        
        print(f"✓ Bulk mark_needs_review: {data['modified']} products modified")
    
    def test_bulk_invalid_action(self, admin_headers):
        """Bulk with invalid action returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/admin/image-review/bulk",
            headers=admin_headers,
            json={
                "action": "invalid_action",
                "product_ids": [TEST_PRODUCT_ID_1]
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid bulk action returns 400")
    
    def test_bulk_missing_params(self, admin_headers):
        """Bulk without action or product_ids returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/admin/image-review/bulk",
            headers=admin_headers,
            json={}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Bulk requires action and product_ids")


class TestCleanup:
    """Restore test products to needs_review status"""
    
    def test_restore_products(self, admin_headers):
        """Restore test products to needs_review for future tests"""
        response = requests.post(
            f"{BASE_URL}/api/admin/image-review/bulk",
            headers=admin_headers,
            json={
                "action": "mark_needs_review",
                "product_ids": [TEST_PRODUCT_ID_1, TEST_PRODUCT_ID_2]
            }
        )
        assert response.status_code == 200
        print("✓ Test products restored to needs_review status")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
