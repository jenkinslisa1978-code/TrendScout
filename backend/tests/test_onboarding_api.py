"""
Onboarding API Tests
Tests for the user onboarding flow endpoints.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ecommerce-guide-11.preview.emergentagent.com').rstrip('/')

# Demo token for testing authenticated endpoints
TEST_USER_ID = "test_onboarding_user_123"
DEMO_TOKEN = f"demo_{TEST_USER_ID}"
AUTH_HEADERS = {
    "Authorization": f"Bearer {DEMO_TOKEN}",
    "Content-Type": "application/json"
}


class TestOnboardingStatusEndpoint:
    """GET /api/user/onboarding-status - Check onboarding completion status"""
    
    def test_get_onboarding_status_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/user/onboarding-status")
        assert response.status_code == 401
        print("✓ GET /api/user/onboarding-status requires auth (401)")
    
    def test_get_onboarding_status_with_auth(self):
        """Test getting onboarding status with authentication"""
        response = requests.get(
            f"{BASE_URL}/api/user/onboarding-status",
            headers=AUTH_HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert "onboarding_completed" in data
        assert isinstance(data["onboarding_completed"], bool)
        print(f"✓ GET /api/user/onboarding-status returns onboarding_completed: {data['onboarding_completed']}")


class TestCompleteOnboardingEndpoint:
    """POST /api/user/complete-onboarding - Mark onboarding as completed"""
    
    def test_complete_onboarding_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/user/complete-onboarding")
        assert response.status_code == 401
        print("✓ POST /api/user/complete-onboarding requires auth (401)")
    
    def test_complete_onboarding_with_auth(self):
        """Test completing onboarding with authentication"""
        response = requests.post(
            f"{BASE_URL}/api/user/complete-onboarding",
            headers=AUTH_HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["onboarding_completed"] == True
        print("✓ POST /api/user/complete-onboarding returns success and onboarding_completed: true")
    
    def test_complete_onboarding_persists(self):
        """Test that completing onboarding persists the state"""
        # Complete onboarding
        complete_response = requests.post(
            f"{BASE_URL}/api/user/complete-onboarding",
            headers=AUTH_HEADERS
        )
        assert complete_response.status_code == 200
        
        # Verify status is now true
        status_response = requests.get(
            f"{BASE_URL}/api/user/onboarding-status",
            headers=AUTH_HEADERS
        )
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["onboarding_completed"] == True
        print("✓ Onboarding completion persists - status shows onboarding_completed: true")


class TestResetOnboardingEndpoint:
    """POST /api/user/reset-onboarding - Reset onboarding status for testing"""
    
    def test_reset_onboarding_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/user/reset-onboarding")
        assert response.status_code == 401
        print("✓ POST /api/user/reset-onboarding requires auth (401)")
    
    def test_reset_onboarding_with_auth(self):
        """Test resetting onboarding with authentication"""
        response = requests.post(
            f"{BASE_URL}/api/user/reset-onboarding",
            headers=AUTH_HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["onboarding_completed"] == False
        print("✓ POST /api/user/reset-onboarding returns success and onboarding_completed: false")
    
    def test_reset_onboarding_persists(self):
        """Test that resetting onboarding persists the state"""
        # First complete onboarding
        requests.post(f"{BASE_URL}/api/user/complete-onboarding", headers=AUTH_HEADERS)
        
        # Then reset
        reset_response = requests.post(
            f"{BASE_URL}/api/user/reset-onboarding",
            headers=AUTH_HEADERS
        )
        assert reset_response.status_code == 200
        
        # Verify status is now false
        status_response = requests.get(
            f"{BASE_URL}/api/user/onboarding-status",
            headers=AUTH_HEADERS
        )
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["onboarding_completed"] == False
        print("✓ Onboarding reset persists - status shows onboarding_completed: false")


class TestOnboardingFlow:
    """Full onboarding flow tests"""
    
    def test_complete_onboarding_flow(self):
        """Test the complete onboarding flow: reset -> check -> complete -> check"""
        # 1. Reset onboarding
        reset_response = requests.post(
            f"{BASE_URL}/api/user/reset-onboarding",
            headers=AUTH_HEADERS
        )
        assert reset_response.status_code == 200
        print("✓ Step 1: Reset onboarding")
        
        # 2. Check initial status (should be false)
        status_response = requests.get(
            f"{BASE_URL}/api/user/onboarding-status",
            headers=AUTH_HEADERS
        )
        assert status_response.status_code == 200
        assert status_response.json()["onboarding_completed"] == False
        print("✓ Step 2: Initial status is onboarding_completed: false")
        
        # 3. Complete onboarding
        complete_response = requests.post(
            f"{BASE_URL}/api/user/complete-onboarding",
            headers=AUTH_HEADERS
        )
        assert complete_response.status_code == 200
        print("✓ Step 3: Complete onboarding")
        
        # 4. Check final status (should be true)
        final_status = requests.get(
            f"{BASE_URL}/api/user/onboarding-status",
            headers=AUTH_HEADERS
        )
        assert final_status.status_code == 200
        assert final_status.json()["onboarding_completed"] == True
        print("✓ Step 4: Final status is onboarding_completed: true")
        
        print("✓ Complete onboarding flow test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
