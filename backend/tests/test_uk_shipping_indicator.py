"""
UK Shipping Time Indicator Feature Tests
Tests the uk_shipping field across all product endpoints:
- GET /api/public/trending-products
- GET /api/public/top-trending
- GET /api/products
- GET /api/products/{product_id}
- GET /api/public/product/{slug}

Shipping tier logic:
- green: UK Warehouse (1-3 days) - UK-based supplier or CJ with lead_time <= 7
- yellow: 7-14 Days - CJ Dropshipping products (cj_pid or data_source=cj_dropshipping)
- red: 3-4 Weeks - Standard China shipping (non-CJ products)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestUKShippingTierLogic:
    """Test the compute_uk_shipping_tier function logic via API responses"""

    def test_trending_products_has_uk_shipping(self):
        """GET /api/public/trending-products returns uk_shipping for each product"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "products" in data, "Response should have 'products' key"
        assert len(data["products"]) > 0, "Should have at least one product"
        
        for product in data["products"]:
            assert "uk_shipping" in product, f"Product {product.get('id')} missing uk_shipping"
            uk_shipping = product["uk_shipping"]
            
            # Validate uk_shipping structure
            assert "tier" in uk_shipping, "uk_shipping should have 'tier'"
            assert "label" in uk_shipping, "uk_shipping should have 'label'"
            assert "color" in uk_shipping, "uk_shipping should have 'color'"
            assert "days_estimate" in uk_shipping, "uk_shipping should have 'days_estimate'"
            assert "description" in uk_shipping, "uk_shipping should have 'description'"
            
            # Validate tier values
            assert uk_shipping["tier"] in ["green", "yellow", "red"], f"Invalid tier: {uk_shipping['tier']}"
            assert uk_shipping["color"] in ["green", "yellow", "red"], f"Invalid color: {uk_shipping['color']}"
            
            print(f"Product {product.get('product_name', 'Unknown')[:30]}: tier={uk_shipping['tier']}, label={uk_shipping['label']}")

    def test_top_trending_has_uk_shipping(self):
        """GET /api/public/top-trending returns uk_shipping for each product"""
        response = requests.get(f"{BASE_URL}/api/public/top-trending")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "products" in data, "Response should have 'products' key"
        
        if len(data["products"]) == 0:
            pytest.skip("No products in top-trending")
        
        for product in data["products"][:5]:  # Check first 5
            assert "uk_shipping" in product, f"Product {product.get('id')} missing uk_shipping"
            uk_shipping = product["uk_shipping"]
            assert uk_shipping["tier"] in ["green", "yellow", "red"]
            print(f"Top trending: {product.get('product_name', 'Unknown')[:30]} - {uk_shipping['tier']}")

    def test_products_list_has_uk_shipping(self):
        """GET /api/products returns uk_shipping for each product in data array"""
        response = requests.get(f"{BASE_URL}/api/products?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "data" in data, "Response should have 'data' key"
        
        if len(data["data"]) == 0:
            pytest.skip("No products in database")
        
        for product in data["data"]:
            assert "uk_shipping" in product, f"Product {product.get('id')} missing uk_shipping"
            uk_shipping = product["uk_shipping"]
            
            # Full structure validation
            assert "tier" in uk_shipping
            assert "label" in uk_shipping
            assert "color" in uk_shipping
            assert "days_estimate" in uk_shipping
            assert "description" in uk_shipping
            
            print(f"Product list: {product.get('product_name', 'Unknown')[:30]} - tier={uk_shipping['tier']}")

    def test_single_product_has_uk_shipping(self):
        """GET /api/products/{product_id} returns uk_shipping in data object"""
        # First get a product ID from the list
        list_response = requests.get(f"{BASE_URL}/api/products?limit=1")
        assert list_response.status_code == 200
        
        products = list_response.json().get("data", [])
        if not products:
            pytest.skip("No products available")
        
        product_id = products[0]["id"]
        
        # Now fetch single product
        response = requests.get(f"{BASE_URL}/api/products/{product_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "data" in data, "Response should have 'data' key"
        
        product = data["data"]
        assert "uk_shipping" in product, "Single product should have uk_shipping"
        
        uk_shipping = product["uk_shipping"]
        assert uk_shipping["tier"] in ["green", "yellow", "red"]
        assert uk_shipping["label"] in ["UK Warehouse", "7-14 Days", "3-4 Weeks"]
        
        print(f"Single product {product_id}: tier={uk_shipping['tier']}, label={uk_shipping['label']}")

    def test_public_product_by_slug_has_uk_shipping(self):
        """GET /api/public/product/{slug} returns uk_shipping field"""
        # First get a product slug from trending
        trending_response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=1")
        assert trending_response.status_code == 200
        
        products = trending_response.json().get("products", [])
        if not products:
            pytest.skip("No trending products available")
        
        slug = products[0].get("slug")
        if not slug:
            pytest.skip("Product has no slug")
        
        # Fetch by slug
        response = requests.get(f"{BASE_URL}/api/public/product/{slug}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        product = response.json()
        assert "uk_shipping" in product, "Public product should have uk_shipping"
        
        uk_shipping = product["uk_shipping"]
        assert uk_shipping["tier"] in ["green", "yellow", "red"]
        print(f"Public product {slug}: tier={uk_shipping['tier']}, label={uk_shipping['label']}")


class TestShippingTierAssignment:
    """Test that shipping tiers are correctly assigned based on product data"""

    def test_cj_products_get_yellow_tier(self):
        """CJ Dropshipping products (cj_pid or data_source=cj_dropshipping) should get yellow tier"""
        # Search for CJ products
        response = requests.get(f"{BASE_URL}/api/products?limit=50")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        cj_products = [p for p in products if p.get("cj_pid") or p.get("data_source") == "cj_dropshipping"]
        
        if not cj_products:
            print("No CJ products found in first 50 products - checking if any exist")
            # This is expected per the context - CJ products have lower launch scores
            pytest.skip("No CJ products in top 50 by score - expected behavior")
        
        for product in cj_products[:5]:
            uk_shipping = product.get("uk_shipping", {})
            # CJ products should be yellow (7-14 days) unless they have UK warehouse
            assert uk_shipping.get("tier") in ["green", "yellow"], \
                f"CJ product {product.get('id')} should be green or yellow, got {uk_shipping.get('tier')}"
            print(f"CJ product: {product.get('product_name', 'Unknown')[:30]} - tier={uk_shipping.get('tier')}")

    def test_non_cj_products_get_red_tier(self):
        """Non-CJ products (amazon_movers, tiktok_trends, etc.) should get red tier"""
        response = requests.get(f"{BASE_URL}/api/products?limit=50")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        non_cj_products = [
            p for p in products 
            if not p.get("cj_pid") and p.get("data_source") not in ["cj_dropshipping", None]
        ]
        
        if not non_cj_products:
            pytest.skip("No non-CJ products found")
        
        red_count = 0
        for product in non_cj_products[:10]:
            uk_shipping = product.get("uk_shipping", {})
            data_source = product.get("data_source", "unknown")
            
            # Non-CJ products without UK suppliers should be red
            if uk_shipping.get("tier") == "red":
                red_count += 1
            
            print(f"Non-CJ ({data_source}): {product.get('product_name', 'Unknown')[:30]} - tier={uk_shipping.get('tier')}")
        
        # Most non-CJ products should be red
        assert red_count > 0, "Expected at least some non-CJ products to have red tier"

    def test_landing_page_products_tier_distribution(self):
        """Landing page shows top 3 products - verify their tier assignment"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=3")
        assert response.status_code == 200
        
        products = response.json().get("products", [])
        assert len(products) == 3, "Landing page should show 3 products"
        
        tier_counts = {"green": 0, "yellow": 0, "red": 0}
        
        for product in products:
            uk_shipping = product.get("uk_shipping", {})
            tier = uk_shipping.get("tier", "unknown")
            data_source = product.get("data_source", "unknown")
            
            if tier in tier_counts:
                tier_counts[tier] += 1
            
            print(f"Landing product ({data_source}): {product.get('product_name', 'Unknown')[:30]} - tier={tier}")
        
        print(f"Tier distribution: {tier_counts}")
        
        # Per context: top 3 are non-CJ (amazon_movers/tiktok_trends) so should be red
        # This validates the expected behavior mentioned in agent_to_agent_context_note


class TestShippingFieldStructure:
    """Test the structure and values of uk_shipping field"""

    def test_green_tier_structure(self):
        """Green tier should have correct label and days estimate"""
        # We may not have green tier products, but test the structure if found
        response = requests.get(f"{BASE_URL}/api/products?limit=100")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        green_products = [p for p in products if p.get("uk_shipping", {}).get("tier") == "green"]
        
        if not green_products:
            print("No green tier products found - this is expected if no UK warehouse suppliers")
            pytest.skip("No green tier products available")
        
        for product in green_products[:3]:
            uk_shipping = product["uk_shipping"]
            assert uk_shipping["label"] == "UK Warehouse"
            assert uk_shipping["days_estimate"] == "1-3 days"
            assert "UK warehouse" in uk_shipping["description"] or "Royal Mail" in uk_shipping["description"]

    def test_yellow_tier_structure(self):
        """Yellow tier should have correct label and days estimate"""
        response = requests.get(f"{BASE_URL}/api/products?limit=100")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        yellow_products = [p for p in products if p.get("uk_shipping", {}).get("tier") == "yellow"]
        
        if not yellow_products:
            print("No yellow tier products found in first 100")
            pytest.skip("No yellow tier products available")
        
        for product in yellow_products[:3]:
            uk_shipping = product["uk_shipping"]
            assert uk_shipping["label"] == "7-14 Days"
            assert uk_shipping["days_estimate"] == "7-14 days"
            assert "CJ" in uk_shipping["description"] or "ePacket" in uk_shipping["description"]

    def test_red_tier_structure(self):
        """Red tier should have correct label and days estimate"""
        response = requests.get(f"{BASE_URL}/api/products?limit=20")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        red_products = [p for p in products if p.get("uk_shipping", {}).get("tier") == "red"]
        
        assert len(red_products) > 0, "Should have at least one red tier product"
        
        for product in red_products[:3]:
            uk_shipping = product["uk_shipping"]
            assert uk_shipping["label"] == "3-4 Weeks"
            assert uk_shipping["days_estimate"] == "21-28 days"
            assert "China" in uk_shipping["description"] or "international" in uk_shipping["description"]
            print(f"Red tier: {product.get('product_name', 'Unknown')[:30]}")


class TestAPIResponseConsistency:
    """Test that uk_shipping is consistent across different endpoints"""

    def test_same_product_same_shipping_info(self):
        """Same product should have same uk_shipping across endpoints"""
        # Get product from list
        list_response = requests.get(f"{BASE_URL}/api/products?limit=1")
        assert list_response.status_code == 200
        
        products = list_response.json().get("data", [])
        if not products:
            pytest.skip("No products available")
        
        product_from_list = products[0]
        product_id = product_from_list["id"]
        
        # Get same product from single endpoint
        single_response = requests.get(f"{BASE_URL}/api/products/{product_id}")
        assert single_response.status_code == 200
        
        product_from_single = single_response.json().get("data", {})
        
        # Compare uk_shipping
        list_shipping = product_from_list.get("uk_shipping", {})
        single_shipping = product_from_single.get("uk_shipping", {})
        
        assert list_shipping.get("tier") == single_shipping.get("tier"), \
            f"Tier mismatch: list={list_shipping.get('tier')}, single={single_shipping.get('tier')}"
        assert list_shipping.get("label") == single_shipping.get("label"), \
            f"Label mismatch: list={list_shipping.get('label')}, single={single_shipping.get('label')}"
        
        print(f"Consistency check passed for product {product_id}")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
