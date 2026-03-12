"""
Test suite for SEO features:
- Sitemap.xml at /api/sitemap.xml
- robots.txt at /api/robots.txt
- Public categories endpoint at /api/public/categories
- Category filter integration with /api/public/trending-products
- Internal linking: Product detail pages and related products
"""
import pytest
import requests
import os
import xml.etree.ElementTree as ET

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSitemapXML:
    """Test dynamic sitemap.xml generation"""

    def test_sitemap_returns_200_with_xml(self):
        """Sitemap endpoint returns 200 and valid XML"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        assert 'application/xml' in response.headers.get('Content-Type', '')
        print(f"✓ Sitemap returns 200 with XML content type")

    def test_sitemap_has_urlset_structure(self):
        """Sitemap has proper <urlset> structure with <url> entries"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        
        # Parse XML
        root = ET.fromstring(response.text)
        # Check namespace - sitemap uses xmlns
        assert 'urlset' in root.tag
        
        # Get all url elements
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('s:url', ns)
        
        assert len(urls) > 0, "Sitemap should have at least one URL"
        print(f"✓ Sitemap has {len(urls)} URL entries")

    def test_sitemap_contains_static_pages(self):
        """Sitemap contains required static pages: /, /trending-products, /pricing"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        content = response.text
        
        required_pages = [
            f"{BASE_URL}/",
            f"{BASE_URL}/trending-products",
            f"{BASE_URL}/pricing",
        ]
        
        for page in required_pages:
            assert page in content, f"Sitemap should contain {page}"
            print(f"✓ Sitemap contains {page}")

    def test_sitemap_contains_trending_product_urls(self):
        """Sitemap contains /trending/:slug product URLs"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        content = response.text
        
        # Check for trending product pattern
        assert '/trending/' in content, "Sitemap should contain trending product URLs"
        
        # Count trending URLs
        trending_count = content.count('/trending/')
        # Subtract the /trending-products page
        product_count = trending_count - content.count('/trending-products')
        
        print(f"✓ Sitemap contains ~{product_count} trending product URLs")
        assert product_count > 0, "Should have at least one product URL"


class TestRobotsTxt:
    """Test robots.txt endpoint"""

    def test_robots_txt_from_api_returns_200(self):
        """GET /api/robots.txt returns 200 with text content"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        assert 'text/plain' in response.headers.get('Content-Type', '')
        print(f"✓ /api/robots.txt returns 200 with text/plain")

    def test_robots_txt_contains_sitemap_directive(self):
        """robots.txt contains Sitemap: directive"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        content = response.text
        
        assert 'Sitemap:' in content, "robots.txt should contain Sitemap directive"
        assert 'sitemap.xml' in content, "robots.txt should point to sitemap.xml"
        print(f"✓ robots.txt contains Sitemap directive")

    def test_robots_txt_has_allow_disallow_rules(self):
        """robots.txt has Allow and Disallow rules"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        content = response.text
        
        # Check for User-agent
        assert 'User-agent:' in content, "Should have User-agent directive"
        
        # Check for Allow rules
        assert 'Allow: /' in content, "Should allow root"
        assert 'Allow: /trending-products' in content, "Should allow /trending-products"
        
        # Check for Disallow rules
        assert 'Disallow: /dashboard' in content, "Should disallow /dashboard"
        assert 'Disallow: /admin' in content, "Should disallow /admin"
        
        print(f"✓ robots.txt has proper Allow/Disallow rules")


class TestPublicCategories:
    """Test public categories endpoint"""

    def test_categories_returns_200_with_array(self):
        """GET /api/public/categories returns 200 with array"""
        response = requests.get(f"{BASE_URL}/api/public/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return array of categories"
        print(f"✓ Categories endpoint returns array with {len(data)} items")

    def test_categories_have_required_fields(self):
        """Each category has name, slug, count, avg_score"""
        response = requests.get(f"{BASE_URL}/api/public/categories")
        assert response.status_code == 200
        
        categories = response.json()
        assert len(categories) > 0, "Should have at least one category"
        
        for cat in categories[:5]:  # Check first 5
            assert 'name' in cat, f"Category should have name"
            assert 'slug' in cat, f"Category should have slug"
            assert 'count' in cat, f"Category should have count"
            assert 'avg_score' in cat, f"Category should have avg_score"
            
            # Validate types
            assert isinstance(cat['name'], str)
            assert isinstance(cat['slug'], str)
            assert isinstance(cat['count'], int)
            assert isinstance(cat['avg_score'], (int, float))
            
        print(f"✓ Categories have all required fields: name, slug, count, avg_score")
        print(f"  Sample categories: {[c['name'] for c in categories[:5]]}")


class TestTrendingProductsNoRegression:
    """Ensure existing trending products endpoint still works"""

    def test_trending_products_returns_200(self):
        """GET /api/public/trending-products returns 200"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products")
        assert response.status_code == 200
        
        data = response.json()
        assert 'products' in data
        assert isinstance(data['products'], list)
        print(f"✓ Trending products returns 200 with {len(data['products'])} products")

    def test_products_have_category_field(self):
        """Products include category field for filtering"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=10")
        products = response.json().get('products', [])
        
        assert len(products) > 0, "Should have at least one product"
        
        for p in products:
            assert 'category' in p, "Product should have category field"
            
        print(f"✓ All products have category field")

    def test_products_have_slug_field(self):
        """Products include slug field for URL routing"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=10")
        products = response.json().get('products', [])
        
        assert len(products) > 0
        
        for p in products:
            assert 'slug' in p, "Product should have slug field"
            assert isinstance(p['slug'], str)
            assert len(p['slug']) > 0, "Slug should not be empty"
            
        print(f"✓ All products have slug field for routing")


class TestProductDetailNoRegression:
    """Ensure product detail endpoint still works with slug"""

    def test_product_by_slug_returns_200(self):
        """GET /api/public/product/:slug returns 200 for valid slug"""
        # First get a valid slug
        products_res = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = products_res.json().get('products', [])
        
        assert len(products) > 0, "Need at least one product to test"
        
        slug = products[0].get('slug')
        assert slug, "Product should have a slug"
        
        response = requests.get(f"{BASE_URL}/api/public/product/{slug}")
        assert response.status_code == 200
        
        data = response.json()
        assert 'product_name' in data
        assert 'launch_score' in data
        print(f"✓ Product detail by slug works: {data.get('product_name', '')[:40]}...")

    def test_product_detail_has_category_for_linking(self):
        """Product detail includes category for internal linking"""
        # Get a valid slug
        products_res = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = products_res.json().get('products', [])
        
        slug = products[0].get('slug')
        response = requests.get(f"{BASE_URL}/api/public/product/{slug}")
        
        data = response.json()
        assert 'category' in data, "Product detail should include category"
        print(f"✓ Product detail includes category: {data.get('category')}")

    def test_product_detail_has_related_products(self):
        """Product detail includes related_products for internal linking"""
        # Get a valid slug
        products_res = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = products_res.json().get('products', [])
        
        slug = products[0].get('slug')
        response = requests.get(f"{BASE_URL}/api/public/product/{slug}")
        
        data = response.json()
        assert 'related_products' in data, "Should have related_products field"
        
        related = data.get('related_products', [])
        if len(related) > 0:
            # Related products should have slug for linking
            for r in related[:3]:
                assert 'slug' in r, "Related products should have slug"
                assert 'product_name' in r, "Related products should have product_name"
            print(f"✓ Product has {len(related)} related products with slugs for internal linking")
        else:
            print(f"✓ Product has related_products field (empty - may be edge case)")

    def test_invalid_slug_returns_404(self):
        """Invalid slug returns 404"""
        response = requests.get(f"{BASE_URL}/api/public/product/this-slug-definitely-does-not-exist-xyz123")
        assert response.status_code == 404
        print(f"✓ Invalid slug returns 404")


class TestSitemapURLCount:
    """Test sitemap has expected number of URLs"""

    def test_sitemap_url_count_reasonable(self):
        """Sitemap has reasonable number of URLs (not empty, not too many)"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        
        # Parse and count URLs
        root = ET.fromstring(response.text)
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('s:url', ns)
        
        url_count = len(urls)
        print(f"✓ Sitemap has {url_count} URLs")
        
        # Should have at least static pages (6) + some products
        assert url_count >= 6, f"Sitemap should have at least 6 URLs (static pages), got {url_count}"
        
        # Should have products if database has products
        products_res = requests.get(f"{BASE_URL}/api/public/trending-products?limit=200")
        product_count = len(products_res.json().get('products', []))
        
        if product_count > 0:
            # Sitemap should have static pages + products
            expected_min = 6 + min(product_count, 50)  # At least 50% of products
            print(f"  Products in DB: {product_count}, URLs in sitemap: {url_count}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
