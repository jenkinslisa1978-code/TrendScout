"""
Test Product Validation Engine Fix - 'Insufficient Data' Bug Fix

Purpose: Verify that the product validation engine now returns real recommendations
instead of 'Insufficient Data - Cannot Validate' for products with valid data.

Root Cause (Fixed):
- The validation engine was looking for 'trend_velocity' but product has 'view_growth_rate'
- The validation engine was looking for 'supplier_orders' but product has 'supplier_order_velocity'
- This caused most signals to be marked as MISSING, dropping confidence below threshold

Fix Applied:
- _analyze_trend_velocity now uses fallback: product.get("trend_velocity") or product.get("view_growth_rate")
- _analyze_supplier_demand now uses fallback: product.get("supplier_orders") or product.get("supplier_order_velocity")
- Base confidence raised from 50 to 60, penalty reduced from -8 to -5 per missing signal
- MIN_CONFIDENCE lowered to 25%
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://measurable-proof.preview.emergentagent.com')

class TestProductValidationFix:
    """Tests for product validation 'Insufficient Data' bug fix"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "jenkinslisa1978@gmail.com",
                "password": "admin123456"
            }
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def product_ids(self, auth_token):
        """Get product IDs from API"""
        response = requests.get(
            f"{BASE_URL}/api/products?page=1&limit=5",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        products = data.get("data", [])
        assert len(products) >= 3, "Need at least 3 products for testing"
        return [p["id"] for p in products[:5]]
    
    def test_complete_analysis_not_insufficient_data(self, auth_token, product_ids):
        """
        Test: GET /api/intelligence/complete-analysis/{product_id} returns a real recommendation
        Expected: recommendation should be 'launch_opportunity', 'promising_monitor', or 'high_risk'
        NOT: 'insufficient_data'
        """
        for product_id in product_ids[:3]:
            response = requests.get(
                f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == 200, f"API call failed for {product_id}: {response.text}"
            data = response.json()
            
            recommendation = data.get("recommendation")
            valid_recommendations = ["launch_opportunity", "promising_monitor", "high_risk"]
            
            # KEY ASSERTION: Not insufficient_data
            assert recommendation != "insufficient_data", \
                f"Product {product_id} still returns 'insufficient_data' - FIX NOT WORKING!"
            
            assert recommendation in valid_recommendations, \
                f"Product {product_id} has unexpected recommendation: {recommendation}"
    
    def test_recommendation_label_not_insufficient(self, auth_token, product_ids):
        """
        Test: recommendation_label should contain actionable text
        Expected: 'Launch Opportunity', 'Promising', or 'High Risk'
        NOT: 'Insufficient Data - Cannot Validate'
        """
        product_id = product_ids[0]
        response = requests.get(
            f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        label = data.get("recommendation_label", "")
        
        # KEY ASSERTION: Label is not "Insufficient Data"
        assert "Insufficient Data" not in label, \
            f"Product {product_id} label still shows 'Insufficient Data': {label}"
        
        # Should contain one of the valid labels
        valid_keywords = ["Launch", "Promising", "Risk"]
        has_valid_keyword = any(keyword in label for keyword in valid_keywords)
        assert has_valid_keyword, f"Label does not contain valid recommendation: {label}"
    
    def test_strengths_array_populated(self, auth_token, product_ids):
        """
        Test: Validation strengths array should be populated with real strengths
        Expected: At least one strength for products with valid data
        """
        product_id = product_ids[0]  # Known product with good data
        response = requests.get(
            f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        strengths = data.get("strengths", [])
        
        # Products with data should have at least some strengths
        assert len(strengths) > 0, f"Product {product_id} has no strengths identified"
        
        # Check strengths are actual text, not "Missing data"
        for strength in strengths:
            assert "Missing data" not in strength, f"Strength contains 'Missing data': {strength}"
    
    def test_weaknesses_no_missing_data(self, auth_token, product_ids):
        """
        Test: Weaknesses array should NOT contain 'Missing data:' entries
        Expected: Weaknesses should be actual product concerns, not data gaps
        """
        for product_id in product_ids[:3]:
            response = requests.get(
                f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            weaknesses = data.get("weaknesses", [])
            
            # KEY ASSERTION: No "Missing data" in weaknesses
            for weakness in weaknesses:
                assert "Missing data" not in weakness, \
                    f"Product {product_id} has 'Missing data' in weaknesses: {weakness}"
    
    def test_confidence_above_minimum(self, auth_token, product_ids):
        """
        Test: Confidence score should be above MIN_CONFIDENCE (25%)
        Expected: confidence >= 25 for products with real data
        """
        for product_id in product_ids[:3]:
            response = requests.get(
                f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            confidence = data.get("confidence", 0)
            
            # Confidence should be above minimum threshold
            assert confidence >= 25, \
                f"Product {product_id} has confidence {confidence}% which is below MIN_CONFIDENCE (25%)"
    
    def test_success_probability_above_zero(self, auth_token, product_ids):
        """
        Test: Success probability should be > 0% for products with real data
        Expected: success_probability > 0
        """
        for product_id in product_ids[:3]:
            response = requests.get(
                f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            success_prob = data.get("success_probability", 0)
            
            # Success probability should be positive
            assert success_prob > 0, \
                f"Product {product_id} has success_probability of 0%"
    
    def test_multiple_products_have_valid_recommendations(self, auth_token, product_ids):
        """
        Test: At least 3 products return valid recommendations via /api/intelligence/complete-analysis/
        This verifies the fix works broadly, not just for one product
        """
        valid_count = 0
        invalid_products = []
        
        for product_id in product_ids:
            response = requests.get(
                f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                recommendation = data.get("recommendation")
                
                if recommendation != "insufficient_data":
                    valid_count += 1
                else:
                    invalid_products.append(product_id)
        
        # At least 3 products should have valid recommendations
        assert valid_count >= 3, \
            f"Only {valid_count} products have valid recommendations. Invalid products: {invalid_products}"
    
    def test_validation_details_have_signals(self, auth_token, product_ids):
        """
        Test: The validation details should include signal breakdown
        Expected: TREND, MARGIN, COMPETITION, AD ACTIVITY, SUPPLIER signals
        """
        product_id = product_ids[0]
        response = requests.get(
            f"{BASE_URL}/api/intelligence/complete-analysis/{product_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for validation details with signals
        details = data.get("details", {})
        validation = details.get("validation", {})
        signals = validation.get("signals", [])
        
        # Should have all 6 signals
        expected_signals = ["Trend Velocity", "Profit Margin", "Competition Level", 
                          "Ad Activity", "Supplier Demand", "Social Engagement"]
        
        signal_names = [s.get("name") for s in signals]
        
        for expected in expected_signals:
            assert expected in signal_names, \
                f"Missing signal '{expected}' in validation. Found: {signal_names}"


class TestValidateEndpoint:
    """Tests for /api/intelligence/validate endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "jenkinslisa1978@gmail.com",
                "password": "admin123456"
            }
        )
        assert response.status_code == 200
        return response.json().get("token")
    
    def test_validate_endpoint_returns_recommendation(self, auth_token):
        """Test the direct validate endpoint"""
        product_id = "2e3d8782-0026-4fef-a04a-a1d3426e2d26"
        
        response = requests.get(
            f"{BASE_URL}/api/intelligence/validate/{product_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        validation = data.get("validation", {})
        recommendation = validation.get("recommendation")
        
        # Should not be insufficient_data
        assert recommendation != "insufficient_data", \
            f"Validate endpoint still returns insufficient_data"


class TestTrendAnalysisEndpoint:
    """Tests for /api/intelligence/trend-analysis endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "jenkinslisa1978@gmail.com",
                "password": "admin123456"
            }
        )
        assert response.status_code == 200
        return response.json().get("token")
    
    def test_trend_analysis_uses_view_growth_rate(self, auth_token):
        """Test that trend analysis works with view_growth_rate field"""
        product_id = "2e3d8782-0026-4fef-a04a-a1d3426e2d26"
        
        response = requests.get(
            f"{BASE_URL}/api/intelligence/trend-analysis/{product_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        trend_analysis = data.get("trend_analysis", {})
        
        # Should have valid trend stage (not unknown)
        trend_stage = trend_analysis.get("trend_stage")
        assert trend_stage is not None, "Trend stage is missing"
        assert trend_stage != "unknown", f"Trend stage is 'unknown', expected valid stage"


class TestSuccessPredictionEndpoint:
    """Tests for /api/intelligence/success-prediction endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "jenkinslisa1978@gmail.com",
                "password": "admin123456"
            }
        )
        assert response.status_code == 200
        return response.json().get("token")
    
    def test_success_prediction_uses_fallback_fields(self, auth_token):
        """Test that success prediction works with fallback field names"""
        product_id = "2e3d8782-0026-4fef-a04a-a1d3426e2d26"
        
        response = requests.get(
            f"{BASE_URL}/api/intelligence/success-prediction/{product_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        prediction = data.get("prediction", {})
        success_prob = prediction.get("success_probability", 0)
        
        # Success probability should be > 0 (not stuck at base 50 with all zeros)
        assert success_prob > 0, "Success probability is 0 or negative"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
