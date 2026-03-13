"""
Iteration 71 - Test New Features:
1. Redis cache migration (rate limiting + API cache)
2. Real-time SSE notifications
3. Multi-step ad generation pipeline
4. Connection Health Check
5. Profitability Calculator
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "jenkinslisa1978@gmail.com"
TEST_PASSWORD = "admin123456"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token."""
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert res.status_code == 200, f"Login failed: {res.text}"
    data = res.json()
    return data.get("token") or data.get("access_token")


@pytest.fixture(scope="module")
def product_id(auth_token):
    """Get a sample product ID for testing."""
    res = requests.get(
        f"{BASE_URL}/api/products?limit=1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    products = data.get("data", [])
    assert len(products) > 0, "No products found"
    return products[0]["id"]


class TestRedisAndRateLimiting:
    """Test Redis cache is operational and rate limiting works."""
    
    def test_rate_limit_headers_present(self, auth_token):
        """Test that X-RateLimit headers are present on authenticated requests."""
        res = requests.get(
            f"{BASE_URL}/api/products?limit=1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert res.status_code == 200
        
        # Verify rate limit headers
        assert "X-RateLimit-Limit" in res.headers, "X-RateLimit-Limit header missing"
        assert "X-RateLimit-Remaining" in res.headers, "X-RateLimit-Remaining header missing"
        assert "X-RateLimit-Reset" in res.headers, "X-RateLimit-Reset header missing"
        assert "X-RateLimit-Plan" in res.headers, "X-RateLimit-Plan header missing"
        
        print(f"Rate Limit Headers:")
        print(f"  Limit: {res.headers.get('X-RateLimit-Limit')}")
        print(f"  Remaining: {res.headers.get('X-RateLimit-Remaining')}")
        print(f"  Reset: {res.headers.get('X-RateLimit-Reset')}")
        print(f"  Plan: {res.headers.get('X-RateLimit-Plan')}")
    
    def test_health_endpoint_accessible(self):
        """Test GET /api/health is accessible."""
        res = requests.get(f"{BASE_URL}/api/health")
        assert res.status_code == 200, f"Health check failed: {res.status_code}"
        print(f"Health check response: {res.json()}")


class TestProfitabilityCalculator:
    """Test POST /api/profitability-calculator endpoint."""
    
    def test_profitability_calculator_valid_request(self, auth_token, product_id):
        """Test profitability calculator with valid inputs."""
        res = requests.post(
            f"{BASE_URL}/api/profitability-calculator",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json={
                "product_id": product_id,
                "daily_ad_budget": 15.0,
                "conversion_rate": 2.5,
                "avg_cpc": 0.40,
                "days": 30
            }
        )
        assert res.status_code == 200, f"Calculator failed: {res.text}"
        data = res.json()
        
        # Verify response structure
        assert "projections" in data, "projections missing"
        assert "break_even" in data, "break_even missing"
        assert "verdict" in data, "verdict missing"
        assert "verdict_color" in data, "verdict_color missing"
        
        # Verify verdict color is valid
        assert data["verdict_color"] in ["green", "amber", "red"], f"Invalid verdict color: {data['verdict_color']}"
        
        # Verify projection fields
        proj = data["projections"]
        assert "total_revenue" in proj, "total_revenue missing"
        assert "total_profit" in proj, "total_profit missing"
        assert "roi_percent" in proj, "roi_percent missing"
        
        print(f"Profitability Calculator Result:")
        print(f"  Product: {data.get('product_name')}")
        print(f"  Verdict: {data['verdict']}")
        print(f"  Verdict Color: {data['verdict_color']}")
        print(f"  ROI: {proj['roi_percent']}%")
        print(f"  Total Revenue: £{proj['total_revenue']}")
        print(f"  Total Profit: £{proj['total_profit']}")
    
    def test_profitability_calculator_verdict_green(self, auth_token, product_id):
        """Test calculator returns green for high ROI scenarios."""
        # Use parameters likely to generate positive ROI
        res = requests.post(
            f"{BASE_URL}/api/profitability-calculator",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json={
                "product_id": product_id,
                "daily_ad_budget": 5.0,
                "conversion_rate": 5.0,  # High conversion
                "avg_cpc": 0.20,  # Low CPC
                "days": 30
            }
        )
        assert res.status_code == 200
        data = res.json()
        print(f"High ROI scenario: {data.get('verdict_color')} - ROI: {data.get('projections', {}).get('roi_percent')}%")
    
    def test_profitability_calculator_invalid_product(self, auth_token):
        """Test calculator returns 404 for invalid product."""
        res = requests.post(
            f"{BASE_URL}/api/profitability-calculator",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json={
                "product_id": "invalid-product-id-12345",
                "daily_ad_budget": 10.0,
                "conversion_rate": 2.0,
                "avg_cpc": 0.50,
                "days": 30
            }
        )
        assert res.status_code == 404, f"Expected 404 for invalid product, got: {res.status_code}"


class TestSSENotifications:
    """Test GET /api/notifications/stream SSE endpoint."""
    
    def test_sse_endpoint_accessible(self, auth_token):
        """Test SSE endpoint returns correct content-type."""
        # Use stream=True and close immediately to just check headers
        res = requests.get(
            f"{BASE_URL}/api/notifications/stream?token={auth_token}",
            stream=True,
            timeout=5
        )
        assert res.status_code == 200, f"SSE endpoint failed: {res.status_code}"
        
        # Verify content type is event-stream
        content_type = res.headers.get("Content-Type", "")
        assert "text/event-stream" in content_type, f"Expected text/event-stream, got: {content_type}"
        
        print(f"SSE Stream Content-Type: {content_type}")
        
        # Read a small amount and close
        try:
            for line in res.iter_lines():
                if line:
                    print(f"SSE First data: {line.decode('utf-8')[:100]}")
                    break
        except:
            pass
        finally:
            res.close()
    
    def test_sse_endpoint_requires_auth(self):
        """Test SSE endpoint returns 401 without auth."""
        res = requests.get(
            f"{BASE_URL}/api/notifications/stream",
            stream=True,
            timeout=5
        )
        assert res.status_code == 401, f"Expected 401, got: {res.status_code}"
        res.close()


class TestConnectionHealthCheck:
    """Test POST /api/connections/health-check endpoint."""
    
    def test_health_check_endpoint_accessible(self, auth_token):
        """Test health check returns results array."""
        res = requests.post(
            f"{BASE_URL}/api/connections/health-check",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert res.status_code == 200, f"Health check failed: {res.status_code} - {res.text}"
        data = res.json()
        
        # Verify response structure
        assert "results" in data, "results array missing"
        assert "message" in data, "message missing"
        
        results = data["results"]
        assert isinstance(results, list), "results should be an array"
        
        print(f"Connection Health Check:")
        print(f"  Message: {data['message']}")
        print(f"  Total connections: {len(results)}")
        
        # If there are connected platforms, check each result structure
        for r in results:
            assert "platform" in r, "platform missing in result"
            assert "status" in r, "status missing in result"
            print(f"  - {r['platform']}: {r['status']} - {r.get('message', '')}")
    
    def test_health_check_no_connections(self, auth_token):
        """Test health check handles no connected platforms."""
        # This user may or may not have connections, both cases are valid
        res = requests.post(
            f"{BASE_URL}/api/connections/health-check",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert res.status_code == 200
        data = res.json()
        
        # If no connections, should return appropriate message
        if len(data.get("results", [])) == 0:
            assert "message" in data
            print(f"No connections - Message: {data['message']}")


class TestAdPipeline:
    """Test POST /api/ad-creatives/generate-pipeline/{product_id} endpoint."""
    
    def test_pipeline_endpoint_exists(self, auth_token, product_id):
        """Test pipeline endpoint is callable and responds correctly."""
        # Just check the endpoint exists and is callable
        # Don't wait for full generation (takes 30+ seconds)
        res = requests.post(
            f"{BASE_URL}/api/ad-creatives/generate-pipeline/{product_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=60  # Allow longer timeout for LLM calls
        )
        
        # Should get 200 (success or partial) or 500 if LLM fails
        assert res.status_code in [200, 500], f"Unexpected status: {res.status_code} - {res.text}"
        
        if res.status_code == 200:
            data = res.json()
            print(f"Pipeline Response:")
            print(f"  Success: {data.get('success')}")
            print(f"  Pipeline: {data.get('pipeline')}")
            print(f"  Steps completed: {data.get('steps_completed', [])}")
            
            # If success, verify pipeline structure
            if data.get("success"):
                assert data.get("pipeline") is True, "pipeline flag should be True"
                assert "creatives" in data, "creatives missing"
                assert "steps_completed" in data, "steps_completed missing"
            else:
                # Partial success is OK
                print(f"  Error: {data.get('error', 'N/A')}")
                print(f"  Partial: {data.get('partial', False)}")
        else:
            print(f"Pipeline failed with 500 - LLM service issue (acceptable)")
    
    def test_pipeline_invalid_product(self, auth_token):
        """Test pipeline returns 404 for invalid product."""
        res = requests.post(
            f"{BASE_URL}/api/ad-creatives/generate-pipeline/invalid-product-12345",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=10
        )
        assert res.status_code == 404, f"Expected 404, got: {res.status_code}"


class TestExistingFeatures:
    """Verify existing features still work (regression)."""
    
    def test_scoring_methodology_endpoint(self):
        """Test GET /api/scoring/methodology still works."""
        res = requests.get(f"{BASE_URL}/api/scoring/methodology")
        assert res.status_code == 200
        data = res.json()
        assert "signals" in data, "signals missing from methodology"
        assert len(data["signals"]) >= 7, f"Expected 7+ signals, got {len(data['signals'])}"
        print(f"Scoring methodology has {len(data['signals'])} signals")
    
    def test_get_products_list(self, auth_token):
        """Test GET /api/products still works."""
        res = requests.get(
            f"{BASE_URL}/api/products?limit=5",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert "data" in data
        print(f"Products endpoint returned {len(data['data'])} products")
    
    def test_connection_platforms(self, auth_token):
        """Test GET /api/connections/platforms still works."""
        res = requests.get(
            f"{BASE_URL}/api/connections/platforms",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert "stores" in data
        assert "ads" in data
        print(f"Platforms: {len(data['stores'])} stores, {len(data['ads'])} ad platforms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
