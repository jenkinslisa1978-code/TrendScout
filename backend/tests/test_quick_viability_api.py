"""
Test suite for Quick Viability API endpoint
Tests the POST /api/public/quick-viability endpoint that provides AI-powered product viability analysis
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cro-audit-staging.preview.emergentagent.com')

class TestQuickViabilityAPI:
    """Tests for POST /api/public/quick-viability endpoint"""
    
    def test_valid_product_name_returns_viability_data(self):
        """Test that a valid product name returns complete viability analysis"""
        response = requests.post(
            f"{BASE_URL}/api/public/quick-viability",
            json={"product_name": "Portable blender"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify required fields exist
        assert "score" in data, "Response missing 'score' field"
        assert "verdict" in data, "Response missing 'verdict' field"
        assert "signals" in data, "Response missing 'signals' field"
        assert "strengths" in data, "Response missing 'strengths' field"
        assert "risks" in data, "Response missing 'risks' field"
        assert "summary" in data, "Response missing 'summary' field"
        assert "product_name" in data, "Response missing 'product_name' field"
        
        # Verify score is valid number 0-100
        assert isinstance(data["score"], (int, float)), "Score should be a number"
        assert 0 <= data["score"] <= 100, f"Score {data['score']} should be between 0-100"
        
        # Verify verdict is one of expected values
        valid_verdicts = ["Strong Potential", "Promising", "Mixed Signals", "High Risk"]
        assert data["verdict"] in valid_verdicts, f"Verdict '{data['verdict']}' not in {valid_verdicts}"
        
        # Verify signals structure
        assert isinstance(data["signals"], dict), "Signals should be a dictionary"
        expected_signals = ["trend_momentum", "market_saturation", "margin_potential", "uk_fit"]
        for signal in expected_signals:
            assert signal in data["signals"], f"Missing signal: {signal}"
            assert isinstance(data["signals"][signal], (int, float)), f"Signal {signal} should be a number"
            assert 0 <= data["signals"][signal] <= 100, f"Signal {signal} should be 0-100"
        
        # Verify strengths and risks are lists
        assert isinstance(data["strengths"], list), "Strengths should be a list"
        assert isinstance(data["risks"], list), "Risks should be a list"
        assert len(data["strengths"]) > 0, "Should have at least one strength"
        assert len(data["risks"]) > 0, "Should have at least one risk"
        
        # Verify summary is non-empty string
        assert isinstance(data["summary"], str), "Summary should be a string"
        assert len(data["summary"]) > 20, "Summary should be meaningful text"
        
        # Verify product_name is echoed back
        assert data["product_name"] == "Portable blender"
    
    def test_empty_product_name_returns_400(self):
        """Test that empty product name returns 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/public/quick-viability",
            json={"product_name": ""},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_too_short_product_name_returns_400(self):
        """Test that product name < 2 chars returns 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/public/quick-viability",
            json={"product_name": "a"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_whitespace_only_product_name_returns_400(self):
        """Test that whitespace-only product name returns 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/public/quick-viability",
            json={"product_name": "   "},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_missing_product_name_field_returns_400(self):
        """Test that missing product_name field returns 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/public/quick-viability",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_product_name_with_special_characters(self):
        """Test that product names with special characters work"""
        response = requests.post(
            f"{BASE_URL}/api/public/quick-viability",
            json={"product_name": "LED sunset lamp (RGB)"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "score" in data
        assert "verdict" in data
    
    def test_no_auth_required(self):
        """Test that endpoint works without authentication"""
        # Make request without any auth headers
        response = requests.post(
            f"{BASE_URL}/api/public/quick-viability",
            json={"product_name": "Ice roller"},
            timeout=30
        )
        
        # Should succeed without auth
        assert response.status_code == 200, f"Expected 200 without auth, got {response.status_code}"


class TestTrendingProductsAPI:
    """Tests for existing public trending products endpoint"""
    
    def test_trending_products_returns_data(self):
        """Test that trending products endpoint returns valid data"""
        response = requests.get(
            f"{BASE_URL}/api/public/trending-products?limit=3",
            timeout=15
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "products" in data
        assert "total" in data
        assert isinstance(data["products"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
