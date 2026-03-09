"""
ViralScout API Tests - Stage 3 Comprehensive Testing
Tests: Products, Alerts, Automation, Stripe endpoints
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealth:
    """Health check and basic API tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["database"] == "connected"
        print("PASS: Health endpoint returns healthy status")
    
    def test_root_endpoint(self):
        """Test /api/ returns API info"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        
        data = response.json()
        assert "ViralScout API" in data.get("message", "")
        print("PASS: Root endpoint returns API info")


class TestProductsAPI:
    """Products CRUD and filtering tests"""
    
    def test_get_products(self):
        """Test GET /api/products returns product list"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        
        # Verify product structure
        product = data["data"][0]
        assert "id" in product
        assert "product_name" in product
        assert "trend_score" in product
        assert "category" in product
        print(f"PASS: GET /api/products returns {len(data['data'])} products")
    
    def test_get_products_with_filters(self):
        """Test products API with category filter"""
        response = requests.get(f"{BASE_URL}/api/products?category=Electronics")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        
        # All returned products should be Electronics category
        for product in data["data"]:
            assert product["category"] == "Electronics"
        print(f"PASS: Category filter returns {len(data['data'])} Electronics products")
    
    def test_get_products_with_search(self):
        """Test products API with search filter"""
        response = requests.get(f"{BASE_URL}/api/products?search=Fan")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        # Should find Portable Neck Fan
        print(f"PASS: Search filter returns {len(data['data'])} matching products")
    
    def test_get_products_sorted(self):
        """Test products API with sorting"""
        response = requests.get(f"{BASE_URL}/api/products?sort_by=trend_score&sort_order=desc")
        assert response.status_code == 200
        
        data = response.json()
        products = data["data"]
        
        # Verify descending sort
        for i in range(len(products) - 1):
            assert products[i]["trend_score"] >= products[i+1]["trend_score"]
        print("PASS: Products sorted by trend_score descending")
    
    def test_create_product_with_automation(self):
        """Test POST /api/products creates product with auto-scoring"""
        unique_name = f"TEST_Product_{uuid.uuid4().hex[:8]}"
        new_product = {
            "product_name": unique_name,
            "category": "Test Category",
            "short_description": "Test product for automation testing",
            "supplier_cost": 10.0,
            "estimated_retail_price": 30.0,
            "tiktok_views": 5000000,
            "ad_count": 50,
            "competition_level": "low",
            "is_premium": False
        }
        
        response = requests.post(f"{BASE_URL}/api/products", json=new_product)
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        product = data["data"]
        
        # Verify automation ran
        assert "trend_score" in product
        assert product["trend_score"] > 0
        assert "trend_stage" in product
        assert "opportunity_rating" in product
        assert "ai_summary" in product
        assert product["ai_summary"] is not None
        assert product["estimated_margin"] == 20.0  # 30 - 10
        
        print(f"PASS: Created product with auto-scoring: trend_score={product['trend_score']}, stage={product['trend_stage']}")
        
        # Cleanup - delete test product
        product_id = product["id"]
        delete_response = requests.delete(f"{BASE_URL}/api/products/{product_id}")
        assert delete_response.status_code == 200
        print(f"PASS: Cleaned up test product {product_id}")
    
    def test_get_single_product(self):
        """Test GET /api/products/{id} returns single product"""
        # First get list to find a product ID
        list_response = requests.get(f"{BASE_URL}/api/products?limit=1")
        products = list_response.json()["data"]
        
        if len(products) > 0:
            product_id = products[0]["id"]
            response = requests.get(f"{BASE_URL}/api/products/{product_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert "data" in data
            assert data["data"]["id"] == product_id
            print(f"PASS: GET single product {product_id}")
    
    def test_get_nonexistent_product(self):
        """Test GET /api/products/{id} returns 404 for missing product"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/products/{fake_id}")
        assert response.status_code == 404
        print("PASS: Returns 404 for non-existent product")


class TestAlertsAPI:
    """Trend Alerts API tests"""
    
    def test_get_alerts(self):
        """Test GET /api/alerts returns alerts with stats"""
        response = requests.get(f"{BASE_URL}/api/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "stats" in data
        
        # Verify stats structure
        stats = data["stats"]
        assert "total" in stats
        assert "unread" in stats
        assert "critical" in stats
        assert "early_stage" in stats
        
        # Verify alert structure
        if len(data["data"]) > 0:
            alert = data["data"][0]
            assert "id" in alert
            assert "product_name" in alert
            assert "alert_type" in alert
            assert "priority" in alert
            assert "trend_score" in alert
        
        print(f"PASS: GET /api/alerts returns {len(data['data'])} alerts, stats: total={stats['total']}")
    
    def test_get_alerts_unread_only(self):
        """Test GET /api/alerts with unread_only filter"""
        response = requests.get(f"{BASE_URL}/api/alerts?unread_only=true")
        assert response.status_code == 200
        
        data = response.json()
        # All returned alerts should be unread
        for alert in data["data"]:
            assert alert.get("read") == False
            assert alert.get("dismissed") == False
        print(f"PASS: Unread filter returns {len(data['data'])} unread alerts")
    
    def test_mark_alert_read(self):
        """Test PUT /api/alerts/{id}/read marks alert as read"""
        # Get an alert
        alerts_response = requests.get(f"{BASE_URL}/api/alerts?limit=1")
        alerts = alerts_response.json()["data"]
        
        if len(alerts) > 0:
            alert_id = alerts[0]["id"]
            response = requests.put(f"{BASE_URL}/api/alerts/{alert_id}/read")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] == True
            print(f"PASS: Marked alert {alert_id} as read")


class TestAutomationAPI:
    """Automation pipeline API tests"""
    
    def test_get_automation_stats(self):
        """Test GET /api/automation/stats returns statistics"""
        response = requests.get(f"{BASE_URL}/api/automation/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_runs" in data
        assert "success_rate" in data
        assert "products_processed" in data
        assert "alerts_generated" in data
        assert "last_run" in data
        
        print(f"PASS: Automation stats: runs={data['total_runs']}, success={data['success_rate']}%")
    
    def test_get_automation_logs(self):
        """Test GET /api/automation/logs returns log history"""
        response = requests.get(f"{BASE_URL}/api/automation/logs")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        
        # Verify log structure
        if len(data["data"]) > 0:
            log = data["data"][0]
            assert "id" in log
            assert "job_type" in log
            assert "status" in log
            assert "started_at" in log
        
        print(f"PASS: GET /api/automation/logs returns {len(data['data'])} log entries")
    
    def test_run_automation_full_pipeline(self):
        """Test POST /api/automation/run executes full pipeline"""
        response = requests.post(
            f"{BASE_URL}/api/automation/run",
            json={"job_type": "full_pipeline"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "processed" in data
        assert "alerts_generated" in data
        assert "log_id" in data
        
        print(f"PASS: Automation pipeline processed {data['processed']} products, generated {data['alerts_generated']} alerts")
    
    def test_scheduled_daily_automation_with_api_key(self):
        """Test POST /api/automation/scheduled/daily with valid API key"""
        response = requests.post(
            f"{BASE_URL}/api/automation/scheduled/daily",
            headers={"X-API-Key": "vs_automation_key_2024"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        print(f"PASS: Scheduled daily automation with API key: processed {data['processed']} products")
    
    def test_scheduled_daily_automation_without_api_key(self):
        """Test POST /api/automation/scheduled/daily fails without API key"""
        response = requests.post(f"{BASE_URL}/api/automation/scheduled/daily")
        assert response.status_code == 401
        print("PASS: Scheduled automation rejects requests without API key")
    
    def test_scheduled_daily_automation_invalid_key(self):
        """Test POST /api/automation/scheduled/daily fails with invalid key"""
        response = requests.post(
            f"{BASE_URL}/api/automation/scheduled/daily",
            headers={"X-API-Key": "invalid_key"}
        )
        assert response.status_code == 401
        print("PASS: Scheduled automation rejects invalid API keys")


class TestStripeAPI:
    """Stripe subscription endpoints tests (Demo Mode)"""
    
    def test_create_checkout_session_demo_mode(self):
        """Test POST /api/stripe/create-checkout-session in demo mode"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/create-checkout-session",
            json={
                "user_id": "test_user_123",
                "price_id": "price_test_123",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        # In demo mode, should return success_url
        assert "url" in data
        assert data["demo_mode"] == True
        print("PASS: Checkout session in demo mode returns redirect URL")
    
    def test_create_portal_session_demo_mode(self):
        """Test POST /api/stripe/create-portal-session in demo mode"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/create-portal-session",
            json={
                "user_id": "test_user_123",
                "return_url": "https://example.com/account"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "url" in data
        assert data["demo_mode"] == True
        print("PASS: Portal session in demo mode returns redirect URL")
    
    def test_cancel_subscription_demo_mode(self):
        """Test POST /api/stripe/cancel-subscription in demo mode"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/cancel-subscription",
            json={
                "user_id": "test_user_123",
                "cancel_at_period_end": True
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["cancelled"] == True
        assert data["demo_mode"] == True
        print("PASS: Cancel subscription in demo mode succeeds")
    
    def test_stripe_webhook_demo_mode(self):
        """Test POST /api/stripe/webhook in demo mode"""
        response = requests.post(
            f"{BASE_URL}/api/stripe/webhook",
            json={"type": "checkout.session.completed"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["received"] == True
        assert data["demo_mode"] == True
        print("PASS: Webhook endpoint in demo mode acknowledges events")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
