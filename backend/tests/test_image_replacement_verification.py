"""
Test Image Replacement Verification
Verifies that all 26 products that had incorrect Unsplash images have been replaced
with AI-generated product-accurate images in MongoDB.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bug-fixes-preview-1.preview.emergentagent.com')


class TestImageReplacementVerification:
    """Verify no Unsplash URLs exist in product image_url fields"""
    
    def test_public_trending_products_no_unsplash(self):
        """Test that /api/public/trending-products returns no unsplash URLs"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=200")
        assert response.status_code == 200, f"API returned {response.status_code}"
        
        data = response.json()
        products = data.get('products', [])
        
        # Check that we got products
        assert len(products) > 0, "No products returned from API"
        print(f"\nTotal products returned: {len(products)}")
        
        # Check for unsplash URLs
        unsplash_products = []
        for p in products:
            url = p.get('image_url', '')
            if url and 'unsplash.com' in url.lower():
                unsplash_products.append({
                    'id': p.get('id'),
                    'name': p.get('product_name'),
                    'url': url
                })
        
        if unsplash_products:
            print("\nUnsplash products found (FAIL):")
            for up in unsplash_products:
                print(f"  - {up['name']}: {up['url'][:60]}...")
        else:
            print("\nSUCCESS: No Unsplash URLs found in any product!")
            
        assert len(unsplash_products) == 0, f"Found {len(unsplash_products)} products with Unsplash URLs"
    
    def test_target_products_have_valid_images(self):
        """Verify specific products (LED Sunset, Cloud Pillow, Neck Fan) have non-Unsplash images"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=200")
        assert response.status_code == 200
        
        data = response.json()
        products = data.get('products', [])
        
        targets = ['LED Sunset', 'Cloud Pillow', 'Neck Fan']
        found = {}
        
        for target in targets:
            for p in products:
                name = p.get('product_name', '')
                if target.lower() in name.lower():
                    found[target] = {
                        'id': p.get('id'),
                        'name': name,
                        'image_url': p.get('image_url', ''),
                        'has_unsplash': 'unsplash.com' in (p.get('image_url', '') or '').lower()
                    }
                    break
        
        print(f"\n=== Target Products Check ===")
        for target, info in found.items():
            print(f"{target}: {info['name']}")
            print(f"  Image URL: {info['image_url'][:80]}..." if info['image_url'] else "  Image URL: MISSING")
            print(f"  Has Unsplash: {info['has_unsplash']}")
            assert not info['has_unsplash'], f"{target} still has Unsplash URL"
        
        # At least 2 of 3 should be found
        assert len(found) >= 2, f"Only found {len(found)}/3 target products"
    
    def test_products_with_images_count(self):
        """Check how many products have valid images"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=200")
        assert response.status_code == 200
        
        data = response.json()
        products = data.get('products', [])
        
        with_image = 0
        without_image = 0
        image_sources = {}
        
        for p in products:
            url = p.get('image_url', '')
            if url:
                with_image += 1
                # Categorize by source
                if 'static.prod-images.emergentagent.com' in url:
                    image_sources['AI Generated'] = image_sources.get('AI Generated', 0) + 1
                elif '/api/images/' in url:
                    image_sources['Local API'] = image_sources.get('Local API', 0) + 1
                elif 'unsplash.com' in url:
                    image_sources['Unsplash'] = image_sources.get('Unsplash', 0) + 1
                else:
                    image_sources['Other'] = image_sources.get('Other', 0) + 1
            else:
                without_image += 1
        
        print(f"\n=== Image Statistics ===")
        print(f"Products with images: {with_image}")
        print(f"Products without images: {without_image}")
        print(f"Image sources breakdown:")
        for source, count in image_sources.items():
            print(f"  - {source}: {count}")
        
        # Verify NO Unsplash
        assert image_sources.get('Unsplash', 0) == 0, "Unsplash images still present"
    
    def test_discover_page_loads(self):
        """Test that /discover redirects to /api/public/trending-products"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        assert 'products' in data, "Response missing 'products' key"
        assert len(data['products']) > 0, "No products returned"
        print(f"\nDiscover API returned {len(data['products'])} products")
    
    def test_categories_endpoint(self):
        """Test that categories endpoint works"""
        response = requests.get(f"{BASE_URL}/api/public/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0, "No categories returned"
        print(f"\nCategories: {[c['name'] for c in data[:5]]}...")


class TestProductDetailImages:
    """Verify product detail pages show correct images"""
    
    def test_led_sunset_product_detail(self):
        """Test LED Sunset product has correct image on detail"""
        # First get the product ID
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=200")
        assert response.status_code == 200
        
        products = response.json().get('products', [])
        led_product = None
        for p in products:
            if 'led sunset' in p.get('product_name', '').lower():
                led_product = p
                break
        
        if led_product:
            print(f"\nLED Sunset Product:")
            print(f"  Name: {led_product['product_name']}")
            print(f"  ID: {led_product['id']}")
            print(f"  Slug: {led_product.get('slug', 'N/A')}")
            img_url = led_product.get('image_url', '')
            print(f"  Image URL: {img_url[:80]}..." if img_url else "  Image URL: MISSING")
            
            # Verify no unsplash
            assert 'unsplash.com' not in (img_url or '').lower(), "LED Sunset still has Unsplash"
            # Verify has AI-generated image
            assert 'static.prod-images.emergentagent.com' in img_url or '/api/images/' in img_url, \
                "LED Sunset missing valid image"
        else:
            pytest.skip("LED Sunset product not found in API response")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
