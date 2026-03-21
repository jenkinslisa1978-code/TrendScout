"""
Test suite for POST /api/leads/capture endpoint
Tests email capture gate functionality for Quick Viability Search
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLeadsCaptureEndpoint:
    """Tests for POST /api/leads/capture endpoint"""
    
    def test_capture_valid_email_with_source(self):
        """Test capturing a valid email with quick_viability_gate source"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "test_valid@example.com",
                "source": "quick_viability_gate",
                "context": "Searched: LED sunset lamp"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_capture_email_without_at_symbol(self):
        """Test that email without @ is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "invalid-email",
                "source": "quick_viability_gate",
                "context": "test"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Invalid email" in data.get("message", "")
    
    def test_capture_empty_email(self):
        """Test that empty email is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "",
                "source": "quick_viability_gate",
                "context": "test"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Invalid email" in data.get("message", "")
    
    def test_capture_whitespace_email(self):
        """Test that whitespace-only email is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "   ",
                "source": "quick_viability_gate",
                "context": "test"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
    
    def test_capture_email_with_different_source(self):
        """Test capturing email with different source value"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "test_other_source@example.com",
                "source": "newsletter",
                "context": "Homepage signup"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_capture_email_without_context(self):
        """Test capturing email without context field"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "test_no_context@example.com",
                "source": "quick_viability_gate"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_capture_email_without_source(self):
        """Test capturing email without source field (defaults to 'unknown')"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "test_no_source@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_capture_duplicate_email_upsert(self):
        """Test that duplicate email is handled via upsert (no error)"""
        email = "test_duplicate@example.com"
        # First capture
        response1 = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={"email": email, "source": "quick_viability_gate", "context": "First search"}
        )
        assert response1.status_code == 200
        assert response1.json()["status"] == "ok"
        
        # Second capture with same email (should upsert, not fail)
        response2 = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={"email": email, "source": "quick_viability_gate", "context": "Second search"}
        )
        assert response2.status_code == 200
        assert response2.json()["status"] == "ok"
    
    def test_capture_email_case_insensitive(self):
        """Test that email is normalized to lowercase"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "TEST_UPPERCASE@EXAMPLE.COM",
                "source": "quick_viability_gate",
                "context": "Test case sensitivity"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_capture_email_with_special_chars_in_context(self):
        """Test capturing email with special characters in context"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "test_special@example.com",
                "source": "quick_viability_gate",
                "context": "Searched: LED sunset lamp (£25-£50) & posture corrector"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
