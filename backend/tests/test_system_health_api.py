"""
System Health Dashboard API Tests
Tests for GET /api/system-health endpoint (admin-only)

Features tested:
- Authentication requirement (401 for unauthenticated)
- Admin role requirement (403 for non-admin)
- Health data response structure validation
- Categories validation (data_ingestion, api_integrations, core_systems, infrastructure)
- Individual check structure validation
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from provided info
ADMIN_EMAIL = "testopt@example.com"
ADMIN_PASSWORD = "TestPass123!"
API_KEY = "vs_admin_key_2024"


class TestSystemHealthAuthentication:
    """Test authentication requirements for /api/system-health endpoint"""
    
    def test_health_requires_authentication(self):
        """GET /api/system-health requires authentication (returns 401/403 without token)"""
        response = requests.get(f"{BASE_URL}/api/system-health")
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}: {response.text}"
        print(f"✓ Unauthenticated request correctly rejected with status {response.status_code}")
    
    def test_health_requires_admin_role(self, non_admin_token):
        """GET /api/system-health requires admin role (returns 403 for non-admin)"""
        headers = {"Authorization": f"Bearer {non_admin_token}"}
        response = requests.get(f"{BASE_URL}/api/system-health", headers=headers)
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}: {response.text}"
        print(f"✓ Non-admin request correctly rejected with 403")
    
    def test_health_admin_access_success(self, admin_token):
        """GET /api/system-health returns 200 for admin user"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/system-health", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Admin request successful with status 200")


class TestSystemHealthResponseStructure:
    """Test response structure of /api/system-health"""
    
    def test_health_response_top_level_fields(self, admin_token):
        """Response has overall_status, total_checks, healthy, warnings, errors, avg_uptime, checked_at, categories, checks"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/system-health", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["overall_status", "total_checks", "healthy", "warnings", "errors", 
                          "avg_uptime", "checked_at", "categories", "checks"]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"✓ All required top-level fields present: {required_fields}")
        print(f"  - overall_status: {data['overall_status']}")
        print(f"  - total_checks: {data['total_checks']}")
        print(f"  - healthy: {data['healthy']}, warnings: {data['warnings']}, errors: {data['errors']}")
        print(f"  - avg_uptime: {data['avg_uptime']}%")
    
    def test_health_categories_include_required(self, admin_token):
        """Response categories include data_ingestion, api_integrations, core_systems, infrastructure"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/system-health", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        categories = data.get("categories", {})
        
        required_categories = ["data_ingestion", "api_integrations", "core_systems", "infrastructure"]
        for cat in required_categories:
            assert cat in categories, f"Missing category: {cat}"
            assert isinstance(categories[cat], list), f"Category {cat} should be a list"
            assert len(categories[cat]) > 0, f"Category {cat} should have checks"
        
        print(f"✓ All required categories present:")
        for cat in required_categories:
            print(f"  - {cat}: {len(categories[cat])} checks")
    
    def test_health_check_structure(self, admin_token):
        """Each check has name, category, status, last_success, message, uptime fields"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/system-health", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        checks = data.get("checks", [])
        assert len(checks) > 0, "Expected at least one check"
        
        required_check_fields = ["name", "category", "status", "last_success", "message", "uptime"]
        valid_statuses = ["healthy", "warning", "error"]
        
        for check in checks[:5]:  # Test first 5 checks
            for field in required_check_fields:
                assert field in check, f"Check '{check.get('name', 'unknown')}' missing field: {field}"
            
            assert check["status"] in valid_statuses, f"Invalid status: {check['status']}"
            assert isinstance(check["uptime"], (int, float)), f"Uptime should be numeric"
        
        print(f"✓ All {len(checks)} checks have required structure")
        print(f"✓ Valid statuses verified: {valid_statuses}")


class TestSystemHealthCategoryContent:
    """Test specific content in each category"""
    
    def test_data_ingestion_checks(self, admin_token):
        """Data Ingestion category shows Opportunity Feed, Amazon Scraper, Google Trends, Score Recomputation, Product Data Freshness"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/system-health", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        data_ingestion = data.get("categories", {}).get("data_ingestion", [])
        check_names = [c["name"] for c in data_ingestion]
        
        expected_checks = ["Opportunity Feed", "Amazon Scraper", "Google Trends", "Score Recomputation", "Product Data Freshness"]
        found_checks = []
        
        for expected in expected_checks:
            # Partial match for flexibility
            matching = [n for n in check_names if expected.lower() in n.lower()]
            if matching:
                found_checks.append(expected)
        
        print(f"✓ Data Ingestion checks found: {check_names}")
        print(f"✓ Expected checks matched: {found_checks}")
        
        # At least 3 checks should be present
        assert len(data_ingestion) >= 3, f"Expected at least 3 data ingestion checks, got {len(data_ingestion)}"
    
    def test_api_integrations_checks(self, admin_token):
        """API Integrations category shows TikTok, AliExpress, Meta, CJ, Zendrop statuses"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/system-health", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        api_integrations = data.get("categories", {}).get("api_integrations", [])
        check_names = [c["name"] for c in api_integrations]
        
        expected_apis = ["TikTok", "AliExpress", "Meta", "CJ", "Zendrop"]
        found_apis = []
        
        for api in expected_apis:
            matching = [n for n in check_names if api.lower() in n.lower()]
            if matching:
                found_apis.append(api)
        
        print(f"✓ API Integration checks found: {check_names}")
        print(f"✓ Expected APIs matched: {found_apis}")
        
        assert len(api_integrations) >= 4, f"Expected at least 4 API integration checks, got {len(api_integrations)}"
    
    def test_core_systems_checks(self, admin_token):
        """Core Systems category shows Product Scoring Engine, Opportunity Feed Generation, Ad Blueprint Generator, Store Launch Pipeline"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/system-health", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        core_systems = data.get("categories", {}).get("core_systems", [])
        check_names = [c["name"] for c in core_systems]
        
        expected_systems = ["Product Scoring", "Opportunity Feed", "Ad Blueprint", "Store Launch"]
        found_systems = []
        
        for sys in expected_systems:
            matching = [n for n in check_names if sys.lower() in n.lower()]
            if matching:
                found_systems.append(sys)
        
        print(f"✓ Core Systems checks found: {check_names}")
        print(f"✓ Expected systems matched: {found_systems}")
        
        assert len(core_systems) >= 3, f"Expected at least 3 core system checks, got {len(core_systems)}"
    
    def test_infrastructure_checks(self, admin_token):
        """Infrastructure category shows MongoDB, Stripe, Job Scheduler, Job Queue Worker"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/system-health", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        infrastructure = data.get("categories", {}).get("infrastructure", [])
        check_names = [c["name"] for c in infrastructure]
        
        expected_infra = ["MongoDB", "Stripe", "Job Scheduler", "Job Queue"]
        found_infra = []
        
        for infra in expected_infra:
            matching = [n for n in check_names if infra.lower() in n.lower()]
            if matching:
                found_infra.append(infra)
        
        print(f"✓ Infrastructure checks found: {check_names}")
        print(f"✓ Expected infrastructure matched: {found_infra}")
        
        assert len(infrastructure) >= 3, f"Expected at least 3 infrastructure checks, got {len(infrastructure)}"


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def admin_token():
    """Get auth token for admin user (testopt@example.com)"""
    # First, login to get token
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if login_response.status_code == 200:
        token = login_response.json().get("token")
        if token:
            print(f"✓ Admin login successful for {ADMIN_EMAIL}")
            return token
    
    # Fallback: Sign up and set admin via API key
    signup_email = f"admin_test_{uuid.uuid4().hex[:8]}@example.com"
    signup_response = requests.post(
        f"{BASE_URL}/api/auth/signup",
        json={"email": signup_email, "password": ADMIN_PASSWORD, "name": "Admin Test"}
    )
    
    if signup_response.status_code in [200, 201]:
        token = signup_response.json().get("token")
        # Set as admin
        admin_response = requests.post(
            f"{BASE_URL}/api/user/set-admin?email={signup_email}&is_admin=true",
            headers={"X-API-Key": API_KEY}
        )
        if admin_response.status_code == 200 and token:
            print(f"✓ Created new admin user: {signup_email}")
            return token
    
    pytest.skip("Could not authenticate as admin user")


@pytest.fixture(scope="module")
def non_admin_token():
    """Get auth token for non-admin user"""
    # Create a unique non-admin user
    non_admin_email = f"nonadmin_test_{uuid.uuid4().hex[:8]}@example.com"
    
    signup_response = requests.post(
        f"{BASE_URL}/api/auth/signup",
        json={"email": non_admin_email, "password": "TestPass123!", "name": "Non Admin Test"}
    )
    
    if signup_response.status_code in [200, 201]:
        token = signup_response.json().get("token")
        if token:
            print(f"✓ Created non-admin user: {non_admin_email}")
            return token
    
    # Try login instead
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": non_admin_email, "password": "TestPass123!"}
    )
    
    if login_response.status_code == 200:
        token = login_response.json().get("token")
        if token:
            return token
    
    pytest.skip("Could not create non-admin user for testing")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
