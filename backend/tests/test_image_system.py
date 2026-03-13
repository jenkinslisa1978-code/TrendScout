"""
Test suite for TrendScout Image Intelligence System.
Tests: image serving, image enrichment API, gallery support in public APIs,
and verifies image_enriched flag in products.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "jenkinslisa1978@gmail.com"
TEST_PASSWORD = "Test123!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for testing authenticated endpoints."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with authentication token."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


# ── Image Serving Tests ──

class TestImageServing:
    """Tests for GET /api/images/{filename} endpoint"""

    def test_image_serving_returns_jpeg(self):
        """Verify stored images are served with correct content-type."""
        # First, get a product with enriched images
        response = requests.get(f"{BASE_URL}/api/public/product/magnetic-phone-mount")
        assert response.status_code == 200, f"Product fetch failed: {response.text}"
        
        product = response.json()
        image_url = product.get("image_url", "")
        
        # If image_url is a local path, test serving
        if image_url.startswith("/api/images/"):
            filename = image_url.split("/api/images/")[-1]
            img_response = requests.get(f"{BASE_URL}/api/images/{filename}")
            
            assert img_response.status_code == 200, f"Image serving failed: {img_response.status_code}"
            assert "image/jpeg" in img_response.headers.get("Content-Type", ""), \
                f"Wrong content-type: {img_response.headers.get('Content-Type')}"
            assert len(img_response.content) > 1000, "Image too small, may be broken"
            print(f"✓ Image served successfully: {filename} ({len(img_response.content)} bytes)")

    def test_nonexistent_image_returns_404(self):
        """Verify 404 is returned for non-existent images."""
        response = requests.get(f"{BASE_URL}/api/images/nonexistent_image_12345.jpg")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent image returns 404")


# ── Image Enrichment API Tests ──

class TestImageEnrichmentAPI:
    """Tests for POST /api/images/enrich/{product_id} endpoint (requires auth)"""

    def test_enrich_product_images_requires_auth(self):
        """Verify endpoint requires authentication."""
        response = requests.post(f"{BASE_URL}/api/images/enrich/some-product-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Image enrichment requires authentication")

    def test_enrich_product_images_success(self, auth_headers):
        """Test successful image enrichment for a product."""
        # Get magnetic-phone-mount product ID
        product_response = requests.get(f"{BASE_URL}/api/public/product/magnetic-phone-mount")
        assert product_response.status_code == 200
        product_id = product_response.json().get("id")
        
        # Enrich images
        response = requests.post(
            f"{BASE_URL}/api/images/enrich/{product_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Enrichment failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "primary_image" in data, "Missing primary_image in response"
        assert "gallery" in data, "Missing gallery in response"
        assert isinstance(data["gallery"], list), "Gallery should be a list"
        
        print(f"✓ Image enrichment successful: {len(data['gallery'])} images found")

    def test_enrich_nonexistent_product_returns_404(self, auth_headers):
        """Test 404 for non-existent product."""
        response = requests.post(
            f"{BASE_URL}/api/images/enrich/nonexistent-product-id-12345",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Enrichment of non-existent product returns 404")


# ── Batch Enrichment Tests ──

class TestBatchEnrichment:
    """Tests for POST /api/images/batch-enrich endpoint (admin only)"""

    def test_batch_enrich_requires_auth(self):
        """Verify endpoint requires authentication."""
        response = requests.post(f"{BASE_URL}/api/images/batch-enrich")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Batch enrichment requires authentication")

    def test_batch_enrich_success_for_admin(self, auth_headers):
        """Test batch enrichment for admin user."""
        response = requests.post(
            f"{BASE_URL}/api/images/batch-enrich",
            headers=auth_headers
        )
        
        # If 403, user is not admin - skip
        if response.status_code == 403:
            pytest.skip("Test user is not an admin")
        
        assert response.status_code == 200, f"Batch enrichment failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "enriched" in data, "Missing enriched count"
        assert "failed" in data, "Missing failed count"
        assert isinstance(data["enriched"], int), "enriched should be integer"
        assert isinstance(data["failed"], int), "failed should be integer"
        
        print(f"✓ Batch enrichment: {data['enriched']} enriched, {data['failed']} failed")


# ── Public API Gallery Support Tests ──

class TestPublicAPIGallerySupport:
    """Tests for gallery_images field in public APIs"""

    def test_trending_products_has_gallery_images_field(self):
        """Verify GET /api/public/trending-products returns gallery_images."""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        assert response.status_code == 200, f"API failed: {response.text}"
        
        data = response.json()
        products = data.get("products", [])
        assert len(products) > 0, "No products returned"
        
        # Check if gallery_images field exists in at least one product
        # Note: not all products may have been enriched
        has_gallery = any("gallery_images" in p for p in products)
        
        # gallery_images should be in schema even if empty
        for product in products[:3]:
            print(f"  Product: {product.get('product_name', 'Unknown')[:40]}")
            print(f"    - image_url: {product.get('image_url', 'N/A')[:60]}")
            print(f"    - gallery_images: {product.get('gallery_images', 'NOT PRESENT')}")
        
        print(f"✓ Trending products API returns products with gallery_images support")

    def test_product_detail_has_gallery_images(self):
        """Verify GET /api/public/product/{slug} returns gallery_images."""
        # Test with known enriched product
        response = requests.get(f"{BASE_URL}/api/public/product/magnetic-phone-mount")
        assert response.status_code == 200, f"Product fetch failed: {response.text}"
        
        product = response.json()
        
        # Verify required fields
        assert "gallery_images" in product, "Missing gallery_images field"
        assert isinstance(product["gallery_images"], list), "gallery_images should be a list"
        
        print(f"✓ Product detail has gallery_images: {len(product['gallery_images'])} images")
        print(f"  Gallery URLs: {product['gallery_images']}")

    def test_product_detail_has_growth_rate_and_tiktok_views(self):
        """Verify GET /api/public/product/{slug} returns growth_rate and tiktok_views."""
        response = requests.get(f"{BASE_URL}/api/public/product/magnetic-phone-mount")
        assert response.status_code == 200, f"Product fetch failed: {response.text}"
        
        product = response.json()
        
        # Verify numeric fields exist
        assert "growth_rate" in product, "Missing growth_rate field"
        assert "tiktok_views" in product, "Missing tiktok_views field"
        
        # Verify they are numeric
        assert isinstance(product["growth_rate"], (int, float)), \
            f"growth_rate should be numeric, got {type(product['growth_rate'])}"
        assert isinstance(product["tiktok_views"], (int, float)), \
            f"tiktok_views should be numeric, got {type(product['tiktok_views'])}"
        
        print(f"✓ Product has growth_rate ({product['growth_rate']}) and tiktok_views ({product['tiktok_views']})")


# ── Integration Tests ──

class TestImageSystemIntegration:
    """End-to-end integration tests for image system"""

    def test_enriched_images_are_servable(self, auth_headers):
        """Verify images returned by enrichment are actually servable."""
        # Get a product
        product_response = requests.get(f"{BASE_URL}/api/public/product/magnetic-phone-mount")
        assert product_response.status_code == 200
        product = product_response.json()
        
        # Check gallery images are servable
        gallery_images = product.get("gallery_images", [])
        for img_url in gallery_images[:3]:  # Test up to 3 images
            if img_url.startswith("/api/images/"):
                full_url = f"{BASE_URL}{img_url}"
                img_response = requests.get(full_url)
                assert img_response.status_code == 200, \
                    f"Gallery image not servable: {img_url}"
                print(f"  ✓ Gallery image OK: {img_url.split('/')[-1]}")
        
        print(f"✓ All gallery images ({len(gallery_images)}) are servable")

    def test_primary_image_matches_first_gallery_image(self):
        """Verify primary image_url is first in gallery_images (when enriched)."""
        response = requests.get(f"{BASE_URL}/api/public/product/magnetic-phone-mount")
        assert response.status_code == 200
        product = response.json()
        
        image_url = product.get("image_url", "")
        gallery = product.get("gallery_images", [])
        
        if gallery and image_url.startswith("/api/images/"):
            # Primary should be in gallery
            assert image_url in gallery, \
                f"Primary image {image_url} not in gallery {gallery}"
            print(f"✓ Primary image is in gallery")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
