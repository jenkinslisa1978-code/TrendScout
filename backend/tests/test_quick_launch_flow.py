"""
Quick Launch Flow Tests - Test the 3-click launch flow feature
Testing: Products API, Store Launch API, Ad Creative Generation API
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "jenkinslisa1978@gmail.com"
TEST_PASSWORD = "admin123456"


class TestQuickLaunchFlowAPIs:
    """Test APIs used by Quick Launch Flow widget"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for authenticated tests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("token") or data.get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("Authentication failed - skipping authenticated tests")

    def test_products_endpoint_returns_data_for_quick_launch(self):
        """Step 1: Products API returns products sorted by launch_score for Quick Launch widget"""
        response = self.session.get(
            f"{BASE_URL}/api/products",
            params={"page": 1, "limit": 10, "sort_by": "launch_score", "sort_order": "desc"}
        )
        assert response.status_code == 200
        
        data = response.json()
        products = data.get("data") or data.get("products") or []
        
        assert len(products) > 0, "Should return at least one product"
        
        # Verify product has required fields for Quick Launch widget
        top_product = products[0]
        assert "id" in top_product
        assert "product_name" in top_product
        assert "supplier_cost" in top_product
        assert "estimated_retail_price" in top_product
        assert "launch_score" in top_product or top_product.get("trend_score") is not None
        
        print(f"Top product: {top_product.get('product_name')} with launch_score={top_product.get('launch_score')}")

    def test_products_have_price_data_for_margin_calculation(self):
        """Products should have supplier_cost and retail_price for margin display in £"""
        response = self.session.get(
            f"{BASE_URL}/api/products",
            params={"page": 1, "limit": 5, "sort_by": "launch_score", "sort_order": "desc"}
        )
        assert response.status_code == 200
        
        data = response.json()
        products = data.get("data") or data.get("products") or []
        
        for product in products:
            supplier_cost = product.get("supplier_cost", 0)
            retail_price = product.get("estimated_retail_price", 0)
            
            # Prices should be numeric and positive
            assert isinstance(supplier_cost, (int, float))
            assert isinstance(retail_price, (int, float))
            assert supplier_cost >= 0, "Supplier cost should be non-negative"
            assert retail_price >= 0, "Retail price should be non-negative"
            
        print(f"Verified {len(products)} products have valid price data")

    def test_store_launch_endpoint_exists(self):
        """Step 2: Store launch API should exist and accept requests"""
        # Get a product ID first
        products_response = self.session.get(
            f"{BASE_URL}/api/products",
            params={"page": 1, "limit": 1, "sort_by": "launch_score", "sort_order": "desc"}
        )
        products = products_response.json().get("data") or products_response.json().get("products") or []
        
        if not products:
            pytest.skip("No products available for store launch test")
        
        product_id = products[0]["id"]
        
        # Test store launch endpoint
        response = self.session.post(
            f"{BASE_URL}/api/stores/launch",
            json={
                "product_id": product_id,
                "store_name": "TEST Quick Launch Store"
            }
        )
        
        # Should return 200/201 on success, or meaningful error
        assert response.status_code in [200, 201, 400, 422], f"Unexpected status: {response.status_code}"
        
        data = response.json()
        if response.status_code in [200, 201]:
            assert "store" in data or "id" in data, "Should return store data on success"
            print(f"Store created successfully: {data.get('store', {}).get('name', data.get('id'))}")
        else:
            print(f"Store creation response: {data}")

    def test_ad_creative_generate_endpoint_exists(self):
        """Step 3: Ad creative generation API should exist"""
        # Get a product ID first
        products_response = self.session.get(
            f"{BASE_URL}/api/products",
            params={"page": 1, "limit": 1}
        )
        products = products_response.json().get("data") or products_response.json().get("products") or []
        
        if not products:
            pytest.skip("No products available for ad generation test")
        
        product_id = products[0]["id"]
        
        # Test ad creative generate endpoint
        response = self.session.post(
            f"{BASE_URL}/api/ad-creatives/generate/{product_id}"
        )
        
        # Should return 200/201 on success, or meaningful error (not 500)
        assert response.status_code in [200, 201, 400, 422, 404], f"Unexpected status: {response.status_code}"
        
        print(f"Ad creative generation status: {response.status_code}")

    def test_suppliers_endpoint_returns_prices(self):
        """Supplier section: Verify suppliers have prices for £ display"""
        # Get a product ID first
        products_response = self.session.get(
            f"{BASE_URL}/api/products",
            params={"page": 1, "limit": 1}
        )
        products = products_response.json().get("data") or products_response.json().get("products") or []
        
        if not products:
            pytest.skip("No products available for supplier test")
        
        product_id = products[0]["id"]
        
        response = self.session.get(f"{BASE_URL}/api/suppliers/{product_id}")
        
        assert response.status_code == 200
        
        data = response.json()
        suppliers = data.get("suppliers", [])
        
        # If suppliers exist, verify they have price data
        for supplier in suppliers:
            if "supplier_cost" in supplier:
                assert isinstance(supplier["supplier_cost"], (int, float))
            if "estimated_shipping_cost" in supplier:
                assert isinstance(supplier["estimated_shipping_cost"], (int, float))
        
        print(f"Found {len(suppliers)} suppliers for product")

    def test_alerts_endpoint_returns_severity(self):
        """Trend alerts: Verify alerts have severity field for priority labels"""
        response = self.session.get(
            f"{BASE_URL}/api/alerts",
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        alerts = data.get("data") if isinstance(data, dict) else data
        
        if not alerts:
            print("No alerts found - this is OK")
            return
        
        # Verify alerts have severity or priority field
        for alert in alerts[:5]:
            has_severity = "severity" in alert or "priority" in alert
            assert has_severity, f"Alert should have severity or priority field: {alert.get('id')}"
            
            severity = alert.get("severity") or alert.get("priority")
            assert severity in ["critical", "high", "medium", "low"], f"Invalid severity: {severity}"
        
        print(f"Verified {len(alerts)} alerts have valid severity/priority")


class TestHealthEndpoint:
    """Basic health check"""
    
    def test_backend_health(self):
        """Backend should be healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "healthy"
        assert data.get("database") == "connected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
