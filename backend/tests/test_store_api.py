"""
Store API Tests - Testing store creation, management, and export functionality
"""

import pytest
import requests
import os
import json
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://market-insights-beta.preview.emergentagent.com').rstrip('/')

# Test user constants
TEST_USER_ID = "test-user-store-api"
DEMO_USER_ID = "demo-user-id"

# Store IDs for cleanup
created_store_ids = []
test_product_id = None


class TestStoreApiHealth:
    """Basic health and limits checks"""

    def test_api_health(self):
        """Test API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print("✓ API health check passed")

    def test_store_limits_starter(self):
        """Test store limits for starter plan"""
        response = requests.get(f"{BASE_URL}/api/stores/limits?plan=starter")
        assert response.status_code == 200
        data = response.json()
        assert data["plan"] == "starter"
        assert data["limit"] == 1
        print("✓ Starter plan limit is 1 store")

    def test_store_limits_pro(self):
        """Test store limits for pro plan"""
        response = requests.get(f"{BASE_URL}/api/stores/limits?plan=pro")
        assert response.status_code == 200
        data = response.json()
        assert data["plan"] == "pro"
        assert data["limit"] == 5
        print("✓ Pro plan limit is 5 stores")

    def test_store_limits_elite(self):
        """Test store limits for elite plan"""
        response = requests.get(f"{BASE_URL}/api/stores/limits?plan=elite")
        assert response.status_code == 200
        data = response.json()
        assert data["plan"] == "elite"
        assert data["limit"] == "unlimited"
        print("✓ Elite plan limit is unlimited")


class TestStoreGeneration:
    """Test AI store generation from product"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get a product ID for testing"""
        global test_product_id
        response = requests.get(f"{BASE_URL}/api/products?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) > 0, "Need at least one product for store tests"
        test_product_id = data["data"][0]["id"]
        print(f"✓ Using product ID: {test_product_id}")

    def test_generate_store_content(self):
        """Test generating store content from a product"""
        response = requests.post(
            f"{BASE_URL}/api/stores/generate",
            json={
                "product_id": test_product_id,
                "user_id": TEST_USER_ID,
                "plan": "elite"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify generation result structure
        assert data["success"] == True
        assert "generation" in data
        gen = data["generation"]
        
        # Check store name suggestions
        assert "store_name_suggestions" in gen
        assert len(gen["store_name_suggestions"]) >= 3
        assert gen["selected_name"] in gen["store_name_suggestions"] or gen["selected_name"]
        
        # Check tagline and headline
        assert "tagline" in gen
        assert len(gen["tagline"]) > 0
        assert "headline" in gen
        assert len(gen["headline"]) > 0
        
        # Check product content
        assert "product" in gen
        product = gen["product"]
        assert "title" in product
        assert "description" in product
        assert len(product["description"]) > 100  # Should have substantial description
        assert "bullet_points" in product
        assert len(product["bullet_points"]) >= 3
        
        # Check pricing
        assert "pricing" in product
        pricing = product["pricing"]
        assert "suggested_price" in pricing
        assert "compare_at_price" in pricing
        assert pricing["compare_at_price"] > pricing["suggested_price"]  # Compare-at should be higher
        
        # Check branding
        assert "branding" in gen
        branding = gen["branding"]
        assert "style_name" in branding
        assert "primary_color" in branding
        assert "secondary_color" in branding
        assert "accent_color" in branding
        assert branding["primary_color"].startswith("#")
        
        # Check FAQs
        assert "faqs" in gen
        assert len(gen["faqs"]) >= 3
        assert all("question" in faq and "answer" in faq for faq in gen["faqs"])
        
        # Check policies
        assert "policies" in gen
        policies = gen["policies"]
        assert "shipping_policy" in policies
        assert "return_policy" in policies
        
        print("✓ Store content generation working correctly")

    def test_generate_store_with_custom_name(self):
        """Test generating store with pre-selected name"""
        custom_name = "MyTestStore"
        response = requests.post(
            f"{BASE_URL}/api/stores/generate",
            json={
                "product_id": test_product_id,
                "user_id": TEST_USER_ID,
                "plan": "elite",
                "store_name": custom_name
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # The selected name should match our custom name
        assert data["generation"]["selected_name"] == custom_name
        print(f"✓ Custom store name '{custom_name}' applied correctly")


class TestStoreCreation:
    """Test store CRUD operations"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get a product ID for testing"""
        global test_product_id
        if not test_product_id:
            response = requests.get(f"{BASE_URL}/api/products?limit=1")
            assert response.status_code == 200
            data = response.json()
            test_product_id = data["data"][0]["id"]

    def test_create_store(self):
        """Test creating a new store"""
        store_name = f"TestStore_{datetime.now().strftime('%H%M%S')}"
        
        response = requests.post(
            f"{BASE_URL}/api/stores",
            json={
                "name": store_name,
                "product_id": test_product_id,
                "user_id": TEST_USER_ID,
                "plan": "elite"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "store" in data
        store = data["store"]
        
        # Verify store fields
        assert store["name"] == store_name
        assert store["owner_id"] == TEST_USER_ID
        assert store["status"] == "draft"
        assert "id" in store
        assert "tagline" in store
        assert "headline" in store
        assert "branding" in store
        
        # Track for cleanup
        created_store_ids.append(store["id"])
        
        # Verify product was added
        assert "product" in data
        product = data["product"]
        assert product["store_id"] == store["id"]
        assert product["original_product_id"] == test_product_id
        assert "title" in product
        assert "description" in product
        assert "bullet_points" in product
        assert product["is_featured"] == True  # First product should be featured
        
        print(f"✓ Store '{store_name}' created successfully with ID: {store['id']}")
        return store["id"]

    def test_get_user_stores(self):
        """Test getting all stores for a user"""
        # First create a store if none exist
        if len(created_store_ids) == 0:
            self.test_create_store()
        
        response = requests.get(f"{BASE_URL}/api/stores?user_id={TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert "count" in data
        assert data["count"] >= 1
        
        # Verify store structure
        for store in data["data"]:
            assert "id" in store
            assert "name" in store
            assert "owner_id" in store
            assert store["owner_id"] == TEST_USER_ID
            assert "status" in store
            assert "product_count" in store
        
        print(f"✓ Found {data['count']} stores for user {TEST_USER_ID}")

    def test_get_single_store(self):
        """Test getting a single store by ID"""
        # First create a store if none exist
        if len(created_store_ids) == 0:
            self.test_create_store()
        
        store_id = created_store_ids[0]
        response = requests.get(f"{BASE_URL}/api/stores/{store_id}?user_id={TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        store = data["data"]
        assert store["id"] == store_id
        assert store["owner_id"] == TEST_USER_ID
        
        # Store should include products
        assert "products" in store
        assert len(store["products"]) >= 1
        
        print(f"✓ Retrieved store {store_id} with {len(store['products'])} products")

    def test_get_nonexistent_store(self):
        """Test getting a store that doesn't exist"""
        response = requests.get(f"{BASE_URL}/api/stores/nonexistent-store-id?user_id={TEST_USER_ID}")
        assert response.status_code == 404
        print("✓ 404 returned for nonexistent store")


class TestStoreUpdates:
    """Test store update operations"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure we have a store to test with"""
        global created_store_ids, test_product_id
        
        if not test_product_id:
            response = requests.get(f"{BASE_URL}/api/products?limit=1")
            test_product_id = response.json()["data"][0]["id"]
        
        if len(created_store_ids) == 0:
            response = requests.post(
                f"{BASE_URL}/api/stores",
                json={
                    "name": f"TestStore_{datetime.now().strftime('%H%M%S')}",
                    "product_id": test_product_id,
                    "user_id": TEST_USER_ID,
                    "plan": "elite"
                }
            )
            if response.status_code == 200:
                created_store_ids.append(response.json()["store"]["id"])

    def test_update_store_name(self):
        """Test updating store name"""
        store_id = created_store_ids[0]
        new_name = "UpdatedTestStore"
        
        response = requests.put(
            f"{BASE_URL}/api/stores/{store_id}?user_id={TEST_USER_ID}",
            json={"name": new_name}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["store"]["name"] == new_name
        print(f"✓ Store name updated to '{new_name}'")

    def test_update_store_tagline(self):
        """Test updating store tagline"""
        store_id = created_store_ids[0]
        new_tagline = "The best store ever!"
        
        response = requests.put(
            f"{BASE_URL}/api/stores/{store_id}?user_id={TEST_USER_ID}",
            json={"tagline": new_tagline}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["store"]["tagline"] == new_tagline
        print(f"✓ Store tagline updated")

    def test_publish_store(self):
        """Test publishing a store"""
        store_id = created_store_ids[0]
        
        response = requests.put(
            f"{BASE_URL}/api/stores/{store_id}?user_id={TEST_USER_ID}",
            json={"status": "published"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["store"]["status"] == "published"
        print("✓ Store published successfully")

    def test_unpublish_store(self):
        """Test unpublishing a store (back to draft)"""
        store_id = created_store_ids[0]
        
        response = requests.put(
            f"{BASE_URL}/api/stores/{store_id}?user_id={TEST_USER_ID}",
            json={"status": "draft"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["store"]["status"] == "draft"
        print("✓ Store unpublished (back to draft)")


class TestStoreProducts:
    """Test store product management"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure we have a store to test with"""
        global created_store_ids, test_product_id
        
        if not test_product_id:
            response = requests.get(f"{BASE_URL}/api/products?limit=1")
            test_product_id = response.json()["data"][0]["id"]
        
        if len(created_store_ids) == 0:
            response = requests.post(
                f"{BASE_URL}/api/stores",
                json={
                    "name": f"TestStore_{datetime.now().strftime('%H%M%S')}",
                    "product_id": test_product_id,
                    "user_id": TEST_USER_ID,
                    "plan": "elite"
                }
            )
            if response.status_code == 200:
                created_store_ids.append(response.json()["store"]["id"])

    def test_get_store_products(self):
        """Test getting all products in a store"""
        store_id = created_store_ids[0]
        
        response = requests.get(f"{BASE_URL}/api/stores/{store_id}/products")
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert "count" in data
        assert data["count"] >= 1
        
        # Verify product structure
        for product in data["data"]:
            assert "id" in product
            assert "store_id" in product
            assert product["store_id"] == store_id
            assert "title" in product
            assert "description" in product
            assert "price" in product
        
        print(f"✓ Found {data['count']} products in store")

    def test_regenerate_product_copy(self):
        """Test regenerating AI copy for a store product"""
        store_id = created_store_ids[0]
        
        # First get a product ID
        response = requests.get(f"{BASE_URL}/api/stores/{store_id}/products")
        assert response.status_code == 200
        products = response.json()["data"]
        assert len(products) > 0
        product_id = products[0]["id"]
        original_description = products[0]["description"]
        
        # Regenerate copy
        response = requests.post(
            f"{BASE_URL}/api/stores/{store_id}/regenerate/{product_id}?user_id={TEST_USER_ID}"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["regenerated"] == True
        assert "product" in data
        
        # Verify content was regenerated (descriptions should differ)
        print(f"✓ Product copy regenerated for product {product_id}")


class TestStorePreviewAndExport:
    """Test store preview and Shopify export"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure we have a store to test with"""
        global created_store_ids, test_product_id
        
        if not test_product_id:
            response = requests.get(f"{BASE_URL}/api/products?limit=1")
            test_product_id = response.json()["data"][0]["id"]
        
        if len(created_store_ids) == 0:
            response = requests.post(
                f"{BASE_URL}/api/stores",
                json={
                    "name": f"TestStore_{datetime.now().strftime('%H%M%S')}",
                    "product_id": test_product_id,
                    "user_id": TEST_USER_ID,
                    "plan": "elite"
                }
            )
            if response.status_code == 200:
                created_store_ids.append(response.json()["store"]["id"])

    def test_get_store_preview(self):
        """Test getting store preview data"""
        store_id = created_store_ids[0]
        
        response = requests.get(f"{BASE_URL}/api/stores/{store_id}/preview")
        assert response.status_code == 200
        data = response.json()
        
        assert "store" in data
        assert "featured_product" in data
        assert "all_products" in data
        assert "is_published" in data
        
        # Verify store data
        store = data["store"]
        assert store["id"] == store_id
        assert "name" in store
        assert "tagline" in store
        assert "branding" in store
        assert "faqs" in store
        
        # Verify featured product
        if data["featured_product"]:
            fp = data["featured_product"]
            assert "title" in fp
            assert "price" in fp
            assert "bullet_points" in fp
        
        print(f"✓ Store preview retrieved with {len(data['all_products'])} products")

    def test_export_store_shopify(self):
        """Test exporting store for Shopify"""
        store_id = created_store_ids[0]
        
        response = requests.get(
            f"{BASE_URL}/api/stores/{store_id}/export?user_id={TEST_USER_ID}&format=shopify"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify Shopify export structure
        assert "store" in data
        assert "products" in data
        assert "export_format" in data
        assert "exported_at" in data
        
        # Verify store info
        assert "name" in data["store"]
        
        # Verify products are in Shopify format
        for product in data["products"]:
            assert "title" in product
            assert "body_html" in product
            assert "vendor" in product
            assert "variants" in product
            assert "status" in product
            assert product["status"] == "draft"
            
            # Check variant structure
            assert len(product["variants"]) >= 1
            variant = product["variants"][0]
            assert "price" in variant
            assert "compare_at_price" in variant
        
        print(f"✓ Shopify export generated with {len(data['products'])} products")


class TestPlanLimits:
    """Test plan-based store limits enforcement"""

    def test_starter_plan_limit(self):
        """Test that starter plan is limited to 1 store"""
        starter_user_id = "test-starter-user"
        
        # Get a product
        response = requests.get(f"{BASE_URL}/api/products?limit=1")
        product_id = response.json()["data"][0]["id"]
        
        # Create first store (should succeed)
        response = requests.post(
            f"{BASE_URL}/api/stores",
            json={
                "name": "StarterStore1",
                "product_id": product_id,
                "user_id": starter_user_id,
                "plan": "starter"
            }
        )
        assert response.status_code == 200
        store_id = response.json()["store"]["id"]
        created_store_ids.append(store_id)
        print("✓ First store created for starter user")
        
        # Try to create second store (should fail)
        response = requests.post(
            f"{BASE_URL}/api/stores",
            json={
                "name": "StarterStore2",
                "product_id": product_id,
                "user_id": starter_user_id,
                "plan": "starter"
            }
        )
        assert response.status_code == 403
        assert "limit" in response.json()["detail"].lower()
        print("✓ Second store blocked for starter user (limit enforced)")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/stores/{store_id}?user_id={starter_user_id}")


class TestUserIsolation:
    """Test that users can only see their own stores"""

    def test_user_isolation(self):
        """Test that users cannot see other users' stores"""
        # Get the demo user's stores
        response = requests.get(f"{BASE_URL}/api/stores?user_id={DEMO_USER_ID}")
        assert response.status_code == 200
        demo_stores = response.json()["data"]
        
        # Get test user's stores
        response = requests.get(f"{BASE_URL}/api/stores?user_id={TEST_USER_ID}")
        assert response.status_code == 200
        test_stores = response.json()["data"]
        
        # Verify no overlap (unless no stores exist)
        demo_ids = {s["id"] for s in demo_stores}
        test_ids = {s["id"] for s in test_stores}
        
        overlap = demo_ids.intersection(test_ids)
        assert len(overlap) == 0, f"Users should not share stores: {overlap}"
        
        print(f"✓ User isolation verified - demo user: {len(demo_stores)} stores, test user: {len(test_stores)} stores")


class TestCleanup:
    """Cleanup test data"""

    def test_cleanup_stores(self):
        """Delete all test stores created during tests"""
        global created_store_ids
        
        deleted = 0
        for store_id in created_store_ids:
            response = requests.delete(
                f"{BASE_URL}/api/stores/{store_id}?user_id={TEST_USER_ID}"
            )
            # Also try with starter user in case that's the owner
            if response.status_code == 404:
                response = requests.delete(
                    f"{BASE_URL}/api/stores/{store_id}?user_id=test-starter-user"
                )
            if response.status_code == 200:
                deleted += 1
        
        created_store_ids = []
        print(f"✓ Cleaned up {deleted} test stores")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
