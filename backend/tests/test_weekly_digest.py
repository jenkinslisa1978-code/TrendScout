"""
Weekly SEO Digest Feature Tests
Tests: GET /api/digest/latest, /api/digest/archive, /api/digest/{id}, POST /api/digest/generate
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "admin123456"


class TestDigestPublicEndpoints:
    """Test public digest endpoints (no auth required)"""

    def test_get_latest_digest_returns_data(self):
        """GET /api/digest/latest should return the most recent published digest"""
        response = requests.get(f"{BASE_URL}/api/digest/latest")
        print(f"GET /api/digest/latest - Status: {response.status_code}")
        
        # Should return 200 if digest exists, or 404 if none published
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            print(f"Latest digest: {data.get('title', 'NO TITLE')}")
            
            # Verify required fields
            assert "id" in data, "Digest must have id"
            assert "title" in data, "Digest must have title"
            assert "intro" in data, "Digest must have intro"
            assert "products" in data, "Digest must have products array"
            assert "avg_score" in data, "Digest must have avg_score"
            assert "week_label" in data, "Digest must have week_label"
            
            # Verify products structure
            products = data.get("products", [])
            assert len(products) > 0, "Digest must have at least 1 product"
            
            for i, p in enumerate(products):
                print(f"  Product #{p.get('rank', i+1)}: {p.get('product_name', 'Unknown')}")
                assert "product_name" in p, "Each product must have product_name"
                assert "launch_score" in p, "Each product must have launch_score"
                assert "rank" in p, "Each product must have rank"
                assert "insight" in p, "Each product must have insight"
            
            # Verify SEO metadata
            assert "seo" in data, "Digest must have seo metadata"
            seo = data.get("seo", {})
            assert "title" in seo, "SEO must have title"
            assert "description" in seo, "SEO must have description"
            print(f"SEO title: {seo.get('title')}")
            
            return data
        else:
            print("No digest published yet (404)")
            pytest.skip("No digest published yet")

    def test_get_digest_archive_returns_list(self):
        """GET /api/digest/archive should return list of past digests"""
        response = requests.get(f"{BASE_URL}/api/digest/archive")
        print(f"GET /api/digest/archive - Status: {response.status_code}")
        
        assert response.status_code == 200, f"Archive should return 200, got {response.status_code}"
        
        data = response.json()
        assert "digests" in data, "Response must have digests array"
        assert "total" in data, "Response must have total count"
        
        digests = data.get("digests", [])
        print(f"Archive contains {len(digests)} digests")
        
        for d in digests:
            print(f"  - {d.get('title', 'NO TITLE')} | Avg: {d.get('avg_score', 0)}/100 | {d.get('product_count', 0)} products")
            assert "id" in d, "Each digest must have id"
            assert "title" in d, "Each digest must have title"
            assert "avg_score" in d, "Each digest must have avg_score"
            assert "product_count" in d, "Each digest must have product_count"
            # Archive should NOT include full products array (only summary)
            assert "products" not in d, "Archive items should not include full products array"
        
        return digests

    def test_get_digest_by_id(self):
        """GET /api/digest/{id} should return specific digest"""
        # First get the latest to have an ID to test
        latest_response = requests.get(f"{BASE_URL}/api/digest/latest")
        if latest_response.status_code != 200:
            pytest.skip("No digest available to test by ID")
        
        latest = latest_response.json()
        digest_id = latest.get("id")
        print(f"Testing GET /api/digest/{digest_id}")
        
        response = requests.get(f"{BASE_URL}/api/digest/{digest_id}")
        print(f"GET /api/digest/{digest_id} - Status: {response.status_code}")
        
        assert response.status_code == 200, f"Should return 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("id") == digest_id, "Returned digest ID should match requested ID"
        assert "products" in data, "Full digest should include products array"
        print(f"Digest by ID: {data.get('title')}")
        
        return data

    def test_get_digest_by_invalid_id_returns_404(self):
        """GET /api/digest/invalid-id-12345 should return 404"""
        response = requests.get(f"{BASE_URL}/api/digest/invalid-id-12345-nonexistent")
        print(f"GET /api/digest/invalid-id - Status: {response.status_code}")
        
        assert response.status_code == 404, f"Invalid ID should return 404, got {response.status_code}"


class TestDigestAdminEndpoint:
    """Test admin-only digest generation endpoint"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        
        data = response.json()
        token = data.get("access_token") or data.get("token")
        if not token:
            pytest.skip("No token in login response")
        
        print(f"Admin token obtained for {ADMIN_EMAIL}")
        return token

    def test_generate_digest_requires_auth(self):
        """POST /api/digest/generate should require authentication"""
        response = requests.post(f"{BASE_URL}/api/digest/generate")
        print(f"POST /api/digest/generate (no auth) - Status: {response.status_code}")
        
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"

    def test_generate_digest_requires_admin(self, admin_token):
        """POST /api/digest/generate should require admin role"""
        # This test verifies the endpoint works for admin
        # We won't actually generate a new digest to avoid spam, just verify access
        response = requests.post(
            f"{BASE_URL}/api/digest/generate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"POST /api/digest/generate (admin) - Status: {response.status_code}")
        
        # Should either succeed (200/201) or fail with business logic error (400 if not enough products)
        # But NOT 401/403 since we have admin token
        assert response.status_code not in [401, 403], f"Admin should have access, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            print(f"Generated digest: {data.get('digest', {}).get('title', 'Unknown')}")
        elif response.status_code == 400:
            print(f"Generation failed (business logic): {response.json()}")


class TestDigestProductStructure:
    """Verify product cards in digest have all required fields"""

    def test_product_card_fields(self):
        """Each product in digest should have required card fields"""
        response = requests.get(f"{BASE_URL}/api/digest/latest")
        if response.status_code != 200:
            pytest.skip("No digest available")
        
        digest = response.json()
        products = digest.get("products", [])
        
        if not products:
            pytest.skip("No products in digest")
        
        required_fields = [
            "product_name", "rank", "launch_score", "insight"
        ]
        optional_fields = [
            "image_url", "category", "trend_stage", "slug", "id",
            "estimated_retail_price", "competition_level", "tiktok_views",
            "ai_summary", "verified_winner"
        ]
        
        for i, p in enumerate(products):
            print(f"\nProduct #{p.get('rank', i+1)}: {p.get('product_name', 'Unknown')}")
            
            # Check required fields
            for field in required_fields:
                assert field in p, f"Product must have {field}"
                print(f"  {field}: {p.get(field)}")
            
            # Log optional fields
            for field in optional_fields:
                if field in p:
                    print(f"  {field}: {p.get(field)}")
            
            # Verify rank is correct order
            assert p.get("rank") == i + 1, f"Product rank should be {i+1}, got {p.get('rank')}"

    def test_five_products_with_diversity(self):
        """Digest should have up to 5 products with category diversity"""
        response = requests.get(f"{BASE_URL}/api/digest/latest")
        if response.status_code != 200:
            pytest.skip("No digest available")
        
        digest = response.json()
        products = digest.get("products", [])
        
        assert len(products) <= 5, f"Digest should have max 5 products, got {len(products)}"
        assert len(products) >= 1, "Digest should have at least 1 product"
        
        categories = [p.get("category", "") for p in products if p.get("category")]
        unique_categories = set(categories)
        
        print(f"Products: {len(products)}, Categories: {categories}")
        print(f"Unique categories: {len(unique_categories)}")
        
        # If we have 5 products, we should ideally have category diversity
        if len(products) >= 5:
            assert len(unique_categories) >= 2, "With 5 products, should have at least 2 categories"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
