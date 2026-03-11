"""
Authentication API Tests for TrendScout
Tests: /api/auth/register, /api/auth/login, /api/auth/profile
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from the review request
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "admin123456"
TEST_USER_EMAIL = "testuser@test.com"
TEST_USER_PASSWORD = "test123456"


class TestHealthCheck:
    """Basic API health check"""
    
    def test_api_health(self):
        """Test that the API is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("API health check: PASS")


class TestUserRegistration:
    """Registration endpoint tests - POST /api/auth/register"""
    
    def test_register_new_user(self):
        """Test registering a new user"""
        test_email = f"test_auth_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "full_name": "Test User"
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "token" in data, "Response should contain token"
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == test_email
        assert len(data["token"]) > 0, "Token should not be empty"
        print(f"Register new user: PASS - email: {test_email}")
    
    def test_register_duplicate_email(self):
        """Test that registering with existing email fails"""
        # First register a user
        test_email = f"test_dup_{uuid.uuid4().hex[:8]}@test.com"
        first_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "full_name": "Test User"
        })
        assert first_response.status_code == 200
        
        # Try to register again with same email
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "differentpass",
            "full_name": "Another Name"
        })
        assert response.status_code == 400, "Should reject duplicate email"
        print("Register duplicate email: PASS - correctly rejected")
    
    def test_register_invalid_email(self):
        """Test registration with invalid email"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "notanemail",
            "password": "testpass123",
            "full_name": "Test User"
        })
        assert response.status_code == 400, "Should reject invalid email"
        print("Register invalid email: PASS - correctly rejected")
    
    def test_register_short_password(self):
        """Test registration with password less than 6 chars"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "password": "12345",  # Only 5 chars
            "full_name": "Test User"
        })
        assert response.status_code == 400, "Should reject short password"
        print("Register short password: PASS - correctly rejected")


class TestUserLogin:
    """Login endpoint tests - POST /api/auth/login"""
    
    def test_login_admin_user(self):
        """Test login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        
        assert "token" in data, "Response should contain token"
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"Admin login: PASS - email: {ADMIN_EMAIL}")
        return data["token"]
    
    def test_login_regular_user(self):
        """Test login with regular user credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"User login failed: {response.text}"
        data = response.json()
        
        assert "token" in data, "Response should contain token"
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == TEST_USER_EMAIL
        print(f"Regular user login: PASS - email: {TEST_USER_EMAIL}")
        return data["token"]
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": "wrongpassword123"
        })
        assert response.status_code == 401, "Should reject invalid credentials"
        print("Login invalid credentials: PASS - correctly rejected")
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent email"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "somepassword"
        })
        assert response.status_code == 401, "Should reject non-existent user"
        print("Login non-existent user: PASS - correctly rejected")
    
    def test_login_missing_fields(self):
        """Test login with missing email or password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "",
            "password": ""
        })
        assert response.status_code == 400, "Should reject empty fields"
        print("Login missing fields: PASS - correctly rejected")


class TestUserProfile:
    """Profile endpoint tests - GET /api/auth/profile"""
    
    def test_profile_with_valid_token(self):
        """Test getting profile with valid admin token"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Now get profile
        response = requests.get(
            f"{BASE_URL}/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Profile fetch failed: {response.text}"
        data = response.json()
        
        # Admin should have is_admin=true
        assert data.get("is_admin") == True, f"Admin user should have is_admin=true, got: {data}"
        assert data.get("email") == ADMIN_EMAIL
        print(f"Admin profile: PASS - is_admin={data.get('is_admin')}")
    
    def test_profile_regular_user(self):
        """Test getting profile for regular user (not admin)"""
        # Login as regular user
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Get profile
        response = requests.get(
            f"{BASE_URL}/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Profile fetch failed: {response.text}"
        data = response.json()
        
        # Regular user should NOT be admin
        assert data.get("is_admin") != True, f"Regular user should not be admin, got: {data}"
        print(f"Regular user profile: PASS - is_admin={data.get('is_admin', False)}")
    
    def test_profile_without_token(self):
        """Test profile endpoint without auth token"""
        response = requests.get(f"{BASE_URL}/api/auth/profile")
        assert response.status_code == 401, "Should reject request without token"
        print("Profile without token: PASS - correctly rejected")
    
    def test_profile_with_invalid_token(self):
        """Test profile endpoint with invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/profile",
            headers={"Authorization": "Bearer invalidtoken123"}
        )
        assert response.status_code == 401, "Should reject invalid token"
        print("Profile with invalid token: PASS - correctly rejected")


class TestAuthFlow:
    """Full authentication flow tests"""
    
    def test_register_login_profile_flow(self):
        """Test complete auth flow: register -> login -> get profile"""
        test_email = f"test_flow_{uuid.uuid4().hex[:8]}@test.com"
        test_password = "flowtest123"
        test_name = "Flow Test User"
        
        # 1. Register
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": test_password,
            "full_name": test_name
        })
        assert register_response.status_code == 200
        register_token = register_response.json()["token"]
        print(f"Step 1 - Register: PASS")
        
        # 2. Login with same credentials
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        assert login_response.status_code == 200
        login_token = login_response.json()["token"]
        print(f"Step 2 - Login: PASS")
        
        # 3. Get profile with login token
        profile_response = requests.get(
            f"{BASE_URL}/api/auth/profile",
            headers={"Authorization": f"Bearer {login_token}"}
        )
        assert profile_response.status_code == 200
        profile = profile_response.json()
        assert profile.get("email") == test_email
        print(f"Step 3 - Profile: PASS - email={profile.get('email')}")
        
        print(f"Full auth flow: PASS")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
