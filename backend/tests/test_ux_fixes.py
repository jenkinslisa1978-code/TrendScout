"""
UX Fixes Testing - Iteration 64
Testing the following fixes:
1. Supplier prices in pounds (£) not dollars ($)
2. Score tooltips/explanations
3. Plain English descriptions in score breakdown
4. No 'View Supplier' button in header (removed)
5. Supplier button says 'Search on AliExpress' (not 'View on')
6. Trend alerts show consistent severity
7. API returns real recommendations (not insufficient_data) for products
8. Correct product images (bike pump, kids tablet)
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://db-seeding-async.preview.emergentagent.com')

class TestProductValidationAPI:
    """Test that product validation returns real recommendations"""
    
    def test_sunset_lamp_returns_real_recommendation(self):
        """Sunset Projection Lamp should NOT return 'insufficient_data'"""
        product_id = "93ca0ae0-4de4-49dd-a8a5-18b0036cdc11"
        response = requests.get(f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}", timeout=30)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Should NOT be insufficient_data
        assert data.get("recommendation") != "insufficient_data", \
            f"Recommendation should NOT be 'insufficient_data', got: {data.get('recommendation')}"
        
        # Should have a meaningful recommendation
        assert data.get("recommendation") in ["launch_opportunity", "promising_monitor", "high_risk"], \
            f"Expected valid recommendation, got: {data.get('recommendation')}"
        
        # Label should NOT contain 'Insufficient Data'
        assert "Insufficient Data" not in (data.get("recommendation_label") or ""), \
            f"Label should NOT contain 'Insufficient Data', got: {data.get('recommendation_label')}"
        
        print(f"SUCCESS: Sunset Lamp recommendation = {data.get('recommendation_label')}")
    
    def test_validation_has_strengths_array(self):
        """Validation result should have populated strengths array"""
        product_id = "93ca0ae0-4de4-49dd-a8a5-18b0036cdc11"
        response = requests.get(f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}", timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        
        # Strengths should exist and have entries
        strengths = data.get("strengths", [])
        assert len(strengths) > 0, "Strengths array should not be empty"
        print(f"SUCCESS: Found {len(strengths)} strengths: {strengths}")
    
    def test_validation_no_missing_data_weakness(self):
        """Weaknesses should NOT contain 'Missing data:' entries"""
        product_id = "93ca0ae0-4de4-49dd-a8a5-18b0036cdc11"
        response = requests.get(f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}", timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        
        weaknesses = data.get("weaknesses", [])
        for w in weaknesses:
            assert "Missing data:" not in w, f"Found 'Missing data:' in weakness: {w}"
        
        print(f"SUCCESS: No 'Missing data:' in weaknesses array")
    
    def test_confidence_above_minimum(self):
        """Confidence should be above MIN_CONFIDENCE (25%)"""
        product_id = "93ca0ae0-4de4-49dd-a8a5-18b0036cdc11"
        response = requests.get(f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}", timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        
        confidence = data.get("confidence", 0)
        assert confidence >= 25, f"Confidence should be >= 25, got: {confidence}"
        print(f"SUCCESS: Confidence = {confidence}%")
    
    def test_success_probability_positive(self):
        """Success probability should be > 0 for valid products"""
        product_id = "93ca0ae0-4de4-49dd-a8a5-18b0036cdc11"
        response = requests.get(f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}", timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        
        success_prob = data.get("success_probability", 0)
        assert success_prob > 0, f"Success probability should be > 0, got: {success_prob}"
        print(f"SUCCESS: Success probability = {success_prob}%")


class TestSupplierAPI:
    """Test supplier API returns correct format"""
    
    def test_supplier_returns_data(self):
        """Supplier endpoint should return suppliers"""
        product_id = "93ca0ae0-4de4-49dd-a8a5-18b0036cdc11"
        response = requests.get(f"{BASE_URL}/api/suppliers/{product_id}", timeout=30)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        suppliers = data.get("suppliers", [])
        print(f"Found {len(suppliers)} suppliers")
        
        # Check supplier format (prices should be numeric for £ display)
        for supplier in suppliers:
            cost = supplier.get("supplier_cost", 0)
            shipping = supplier.get("estimated_shipping_cost", 0)
            source = supplier.get("source", "unknown")
            
            assert isinstance(cost, (int, float)), f"Cost should be numeric, got: {type(cost)}"
            assert isinstance(shipping, (int, float)), f"Shipping should be numeric, got: {type(shipping)}"
            print(f"Supplier {source}: cost={cost}, shipping={shipping}")


class TestAlertsAPI:
    """Test alerts API returns consistent data"""
    
    def test_alerts_endpoint_exists(self):
        """Alerts endpoint should be accessible"""
        response = requests.get(f"{BASE_URL}/api/alerts/?limit=10", timeout=30)
        
        # May require auth, so 200 or 401 are acceptable
        assert response.status_code in [200, 401], f"Expected 200 or 401, got {response.status_code}"
        print(f"Alerts endpoint status: {response.status_code}")


class TestHealthAPI:
    """Basic health check"""
    
    def test_health_endpoint(self):
        """Health endpoint should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "healthy"
        assert data.get("database") == "connected"
        print(f"SUCCESS: Backend is healthy")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
