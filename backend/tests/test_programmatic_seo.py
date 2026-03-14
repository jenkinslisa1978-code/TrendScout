"""
Test suite for Programmatic SEO Features:
- Part 1: Core SEO pages (/trending-products-today, /trending-products-this-week, /trending-products-this-month)
- Part 2: Category trend pages (/category/:slug)
- Part 3: Product page SEO enhancement (Product, BreadcrumbList, FAQ schema)
- Part 4: Internal linking between page types
- Part 5: Sitemap upgrade with new pages
- Part 6: Structured data in responses
"""
import pytest
import requests
import os
import xml.etree.ElementTree as ET

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSeoTrendingToday:
    """Part 1: Test /api/public/seo/trending-today endpoint"""

    def test_trending_today_returns_200(self):
        """GET /api/public/seo/trending-today returns 200"""
        response = requests.get(f"{BASE_URL}/api/public/seo/trending-today")
        assert response.status_code == 200
        print("✓ SEO Trending Today returns 200")

    def test_trending_today_has_correct_structure(self):
        """Response has title, products array, count, date"""
        response = requests.get(f"{BASE_URL}/api/public/seo/trending-today")
        data = response.json()
        
        assert 'title' in data, "Response should have title"
        assert 'products' in data, "Response should have products array"
        assert 'count' in data, "Response should have count"
        assert 'date' in data, "Response should have date"
        
        assert data['title'] == 'Trending Products Today'
        assert isinstance(data['products'], list)
        print(f"✓ Trending Today has correct structure with {len(data['products'])} products")

    def test_trending_today_products_have_required_fields(self):
        """Each product has id, slug, product_name, launch_score, etc."""
        response = requests.get(f"{BASE_URL}/api/public/seo/trending-today")
        products = response.json().get('products', [])
        
        assert len(products) > 0, "Should have at least one product"
        
        required_fields = ['id', 'slug', 'product_name', 'category', 'image_url', 
                          'launch_score', 'trend_stage', 'margin_percent', 
                          'supplier_cost', 'retail_price']
        
        for field in required_fields:
            assert field in products[0], f"Product should have {field}"
        
        # Check rank is present
        assert products[0].get('rank') == 1, "First product should have rank 1"
        print(f"✓ Products have all required fields including rank")


class TestSeoTrendingThisWeek:
    """Part 1: Test /api/public/seo/trending-this-week endpoint"""

    def test_trending_this_week_returns_200(self):
        """GET /api/public/seo/trending-this-week returns 200"""
        response = requests.get(f"{BASE_URL}/api/public/seo/trending-this-week")
        assert response.status_code == 200
        print("✓ SEO Trending This Week returns 200")

    def test_trending_this_week_has_correct_structure(self):
        """Response has title, products array, count, week_of"""
        response = requests.get(f"{BASE_URL}/api/public/seo/trending-this-week")
        data = response.json()
        
        assert data['title'] == 'Trending Products This Week'
        assert 'products' in data
        assert 'count' in data
        assert 'week_of' in data
        print(f"✓ Trending This Week has correct structure with {len(data['products'])} products")


class TestSeoTrendingThisMonth:
    """Part 1: Test /api/public/seo/trending-this-month endpoint"""

    def test_trending_this_month_returns_200(self):
        """GET /api/public/seo/trending-this-month returns 200"""
        response = requests.get(f"{BASE_URL}/api/public/seo/trending-this-month")
        assert response.status_code == 200
        print("✓ SEO Trending This Month returns 200")

    def test_trending_this_month_has_correct_structure(self):
        """Response has title, products array, count, month"""
        response = requests.get(f"{BASE_URL}/api/public/seo/trending-this-month")
        data = response.json()
        
        assert data['title'] == 'Trending Products This Month'
        assert 'products' in data
        assert 'count' in data
        assert 'month' in data
        print(f"✓ Trending This Month has correct structure with {len(data['products'])} products")


class TestSeoCategoryPage:
    """Part 2: Test /api/public/seo/category/:slug endpoint"""

    def test_category_page_returns_200_for_valid_category(self):
        """GET /api/public/seo/category/:slug returns 200 for valid category"""
        # First get all categories
        cats_response = requests.get(f"{BASE_URL}/api/public/seo/all-categories")
        categories = cats_response.json()
        
        assert len(categories) > 0, "Should have at least one category"
        
        # Test with first category
        slug = categories[0].get('slug')
        response = requests.get(f"{BASE_URL}/api/public/seo/category/{slug}")
        assert response.status_code == 200
        print(f"✓ Category page returns 200 for slug: {slug}")

    def test_category_page_has_correct_structure(self):
        """Category page response has category, title, products, count"""
        cats_response = requests.get(f"{BASE_URL}/api/public/seo/all-categories")
        categories = cats_response.json()
        slug = categories[0].get('slug')
        
        response = requests.get(f"{BASE_URL}/api/public/seo/category/{slug}")
        data = response.json()
        
        assert 'category' in data, "Response should have category name"
        assert 'category_slug' in data, "Response should have category_slug"
        assert 'title' in data, "Response should have title"
        assert 'products' in data, "Response should have products array"
        assert 'count' in data, "Response should have count"
        
        # Title should include category name
        assert categories[0].get('name') in data['title']
        print(f"✓ Category page has correct structure: {data['title']}")

    def test_category_page_404_for_invalid_category(self):
        """Invalid category slug returns 404"""
        response = requests.get(f"{BASE_URL}/api/public/seo/category/invalid-nonexistent-category-xyz123")
        assert response.status_code == 404
        print("✓ Invalid category returns 404")


class TestSeoAllCategories:
    """Part 2: Test /api/public/seo/all-categories endpoint"""

    def test_all_categories_returns_200(self):
        """GET /api/public/seo/all-categories returns 200"""
        response = requests.get(f"{BASE_URL}/api/public/seo/all-categories")
        assert response.status_code == 200
        print("✓ All Categories returns 200")

    def test_all_categories_returns_array_with_required_fields(self):
        """Response is array with name, slug, count, avg_score"""
        response = requests.get(f"{BASE_URL}/api/public/seo/all-categories")
        categories = response.json()
        
        assert isinstance(categories, list), "Should return array"
        assert len(categories) > 0, "Should have at least one category"
        
        required_fields = ['name', 'slug', 'count', 'avg_score']
        for field in required_fields:
            assert field in categories[0], f"Category should have {field}"
        
        print(f"✓ All Categories returns {len(categories)} categories with correct fields")
        print(f"  Sample categories: {[c['name'] for c in categories[:5]]}")


class TestSitemapUpgrade:
    """Part 5: Test sitemap includes new SEO pages"""

    def test_sitemap_includes_trending_today(self):
        """Sitemap includes /trending-products-today"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert '/trending-products-today' in response.text
        print("✓ Sitemap includes /trending-products-today")

    def test_sitemap_includes_trending_this_week(self):
        """Sitemap includes /trending-products-this-week"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert '/trending-products-this-week' in response.text
        print("✓ Sitemap includes /trending-products-this-week")

    def test_sitemap_includes_trending_this_month(self):
        """Sitemap includes /trending-products-this-month"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert '/trending-products-this-month' in response.text
        print("✓ Sitemap includes /trending-products-this-month")

    def test_sitemap_includes_category_pages(self):
        """Sitemap includes /category/ pages"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert '/category/' in response.text
        
        # Count category pages
        category_count = response.text.count('/category/')
        print(f"✓ Sitemap includes {category_count} category pages")

    def test_sitemap_url_count(self):
        """Verify sitemap has expected number of URLs"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        root = ET.fromstring(response.text)
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('s:url', ns)
        
        url_count = len(urls)
        print(f"✓ Sitemap has {url_count} total URLs")
        
        # Should have more URLs now with categories
        assert url_count >= 50, f"Sitemap should have at least 50 URLs with new SEO pages"


class TestProductDataForStructuredData:
    """Part 3 & 6: Product data has fields needed for structured data"""

    def test_product_has_pricing_for_offers_schema(self):
        """Product detail has estimated_retail_price for Offers schema"""
        products_res = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = products_res.json().get('products', [])
        slug = products[0].get('slug')
        
        response = requests.get(f"{BASE_URL}/api/public/product/{slug}")
        data = response.json()
        
        assert 'estimated_retail_price' in data, "Product should have estimated_retail_price"
        assert 'supplier_cost' in data, "Product should have supplier_cost"
        print(f"✓ Product has pricing data for structured data: £{data.get('estimated_retail_price')}")

    def test_product_has_category_for_breadcrumb(self):
        """Product detail has category for BreadcrumbList schema"""
        products_res = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = products_res.json().get('products', [])
        slug = products[0].get('slug')
        
        response = requests.get(f"{BASE_URL}/api/public/product/{slug}")
        data = response.json()
        
        assert 'category' in data, "Product should have category for breadcrumb"
        print(f"✓ Product has category for breadcrumb: {data.get('category')}")

    def test_product_has_image_url(self):
        """Product detail has image_url for Product schema"""
        products_res = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        products = products_res.json().get('products', [])
        slug = products[0].get('slug')
        
        response = requests.get(f"{BASE_URL}/api/public/product/{slug}")
        data = response.json()
        
        assert 'image_url' in data, "Product should have image_url"
        print(f"✓ Product has image_url for structured data")


class TestInternalLinkingData:
    """Part 4: Test data supports internal linking"""

    def test_trending_products_have_slug_for_linking(self):
        """SEO trending pages include slug for internal product links"""
        response = requests.get(f"{BASE_URL}/api/public/seo/trending-today")
        products = response.json().get('products', [])
        
        assert len(products) > 0
        for p in products[:5]:
            assert 'slug' in p, "Product should have slug for internal linking"
            assert len(p['slug']) > 0, "Slug should not be empty"
        
        print(f"✓ Trending products have slugs for internal linking")

    def test_trending_products_have_category_for_linking(self):
        """SEO trending pages include category for category page links"""
        response = requests.get(f"{BASE_URL}/api/public/seo/trending-today")
        products = response.json().get('products', [])
        
        assert len(products) > 0
        for p in products[:5]:
            assert 'category' in p, "Product should have category"
        
        print(f"✓ Trending products have category for internal linking to category pages")

    def test_category_products_have_slug(self):
        """Category page products have slug for product detail links"""
        cats_response = requests.get(f"{BASE_URL}/api/public/seo/all-categories")
        categories = cats_response.json()
        slug = categories[0].get('slug')
        
        response = requests.get(f"{BASE_URL}/api/public/seo/category/{slug}")
        products = response.json().get('products', [])
        
        assert len(products) > 0
        for p in products[:5]:
            assert 'slug' in p, "Category product should have slug"
        
        print(f"✓ Category products have slugs for internal linking")


class TestCrossEndpointConsistency:
    """Test data consistency across SEO endpoints"""

    def test_product_count_matches(self):
        """Product count in response matches products array length"""
        response = requests.get(f"{BASE_URL}/api/public/seo/trending-today")
        data = response.json()
        
        assert data['count'] == len(data['products']), "count should match products array length"
        print(f"✓ Product count matches: {data['count']}")

    def test_categories_have_unique_slugs(self):
        """All categories have unique slugs"""
        response = requests.get(f"{BASE_URL}/api/public/seo/all-categories")
        categories = response.json()
        
        slugs = [c['slug'] for c in categories]
        unique_slugs = set(slugs)
        
        assert len(slugs) == len(unique_slugs), "All category slugs should be unique"
        print(f"✓ All {len(slugs)} category slugs are unique")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
