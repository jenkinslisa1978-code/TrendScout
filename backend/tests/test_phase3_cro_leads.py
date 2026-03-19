"""
Phase 3 CRO - Lead capture API tests
Tests the /api/leads/capture endpoint for email lead capture
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLeadCaptureAPI:
    """Tests for the leads/capture endpoint"""
    
    def test_valid_email_capture(self):
        """Test that valid email returns status: ok"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "test_user_phase3@example.com",
                "source": "free_tool",
                "context": "profit_margin_calculator"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print(f"Valid email capture test PASSED - Response: {data}")
    
    def test_invalid_email_missing_at(self):
        """Test that invalid email (no @) returns error"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "invalid-email-no-at.com",
                "source": "free_tool",
                "context": "roas_calculator"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "error"
        assert "Invalid email" in data.get("message", "")
        print(f"Invalid email test PASSED - Response: {data}")
    
    def test_empty_email(self):
        """Test that empty email returns error"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "",
                "source": "marketing_page",
                "context": "tiktok_landing"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "error"
        print(f"Empty email test PASSED - Response: {data}")
    
    def test_whitespace_only_email(self):
        """Test that whitespace-only email returns error"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "   ",
                "source": "best_products_page"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "error"
        print(f"Whitespace email test PASSED - Response: {data}")
    
    def test_lead_capture_with_source_and_context(self):
        """Test that source and context are accepted"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "uk_seller_phase3@trendscout.test",
                "source": "sample_analysis",
                "context": "neck_fan_analysis"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print(f"Lead with source/context test PASSED - Response: {data}")
    
    def test_lead_capture_minimal_payload(self):
        """Test minimal payload with just email"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={"email": "minimal_phase3@test.com"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print(f"Minimal payload test PASSED - Response: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
