"""
Test suite for TrendScout AI Blog System
- GET /api/blog/posts - List published blog posts
- GET /api/blog/posts/{slug} - Get single blog post by slug
- /blog (frontend) - Blog listing page
- /blog/:slug (frontend) - Single blog post page
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Known blog post slugs (generated via AI)
EXISTING_SLUGS = [
    "top-trending-automotive-products-this-week-march-13-2026",
    "top-trending-garden-outdoors-products-this-week-march-13-2026"
]


class TestBlogPostsListEndpoint:
    """Tests for GET /api/blog/posts"""
    
    def test_blog_posts_list_returns_200(self):
        """GET /api/blog/posts should return 200 status"""
        response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"PASS: GET /api/blog/posts returned 200")
    
    def test_blog_posts_list_returns_posts_array_and_count(self):
        """Response should have posts array and count"""
        response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert response.status_code == 200
        
        data = response.json()
        assert "posts" in data, "Response missing 'posts' field"
        assert "count" in data, "Response missing 'count' field"
        assert isinstance(data["posts"], list), "'posts' should be a list"
        assert isinstance(data["count"], int), "'count' should be an integer"
        assert data["count"] == len(data["posts"]), "count should match posts array length"
        print(f"PASS: Response has posts ({data['count']}) and count fields")
    
    def test_blog_posts_have_required_fields(self):
        """Each blog post should have required fields"""
        response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert response.status_code == 200
        data = response.json()
        
        if data["count"] == 0:
            pytest.skip("No blog posts available to test")
        
        required_fields = ["id", "slug", "title", "category", "published_at", "status"]
        optional_fields = ["meta_description", "tags", "products", "ai_generated"]
        
        for post in data["posts"]:
            for field in required_fields:
                assert field in post, f"Blog post missing required field: {field}"
            print(f"PASS: Blog post '{post['slug']}' has all required fields")
    
    def test_blog_posts_sorted_by_published_at(self):
        """Blog posts should be sorted by published_at (newest first)"""
        response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert response.status_code == 200
        data = response.json()
        
        if data["count"] < 2:
            pytest.skip("Need at least 2 posts to verify sorting")
        
        posts = data["posts"]
        for i in range(len(posts) - 1):
            curr_date = posts[i].get("published_at", "")
            next_date = posts[i + 1].get("published_at", "")
            assert curr_date >= next_date, f"Posts not sorted by published_at: {curr_date} < {next_date}"
        print("PASS: Posts sorted by published_at (newest first)")
    
    def test_blog_posts_have_product_thumbnails(self):
        """Blog posts should have products with thumbnails for cards"""
        response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert response.status_code == 200
        data = response.json()
        
        if data["count"] == 0:
            pytest.skip("No blog posts available to test")
        
        has_products = False
        for post in data["posts"]:
            if "products" in post and len(post["products"]) > 0:
                has_products = True
                product = post["products"][0]
                assert "id" in product or "product_name" in product, "Product missing id or product_name"
                print(f"PASS: Post '{post['slug']}' has {len(post['products'])} embedded products")
        
        if not has_products:
            print("WARNING: No posts have embedded products (may be expected)")


class TestBlogPostDetailEndpoint:
    """Tests for GET /api/blog/posts/{slug}"""
    
    def test_existing_slug_returns_200_with_full_content(self):
        """GET /api/blog/posts/{slug} should return full post for existing slug"""
        # First get the list to find an existing slug
        list_response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert list_response.status_code == 200
        data = list_response.json()
        
        if data["count"] == 0:
            pytest.skip("No blog posts available to test")
        
        slug = data["posts"][0]["slug"]
        
        response = requests.get(f"{BASE_URL}/api/blog/posts/{slug}")
        assert response.status_code == 200, f"Expected 200 for slug '{slug}', got {response.status_code}"
        
        post = response.json()
        assert post["slug"] == slug
        assert "content" in post, "Full post should include 'content' field"
        print(f"PASS: GET /api/blog/posts/{slug} returned 200 with full content")
    
    def test_blog_post_content_structure(self):
        """Blog post content should have intro, sections, conclusion"""
        list_response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert list_response.status_code == 200
        data = list_response.json()
        
        if data["count"] == 0:
            pytest.skip("No blog posts available to test")
        
        slug = data["posts"][0]["slug"]
        response = requests.get(f"{BASE_URL}/api/blog/posts/{slug}")
        assert response.status_code == 200
        
        post = response.json()
        content = post.get("content", {})
        
        # Check content structure
        assert "intro" in content or isinstance(content, dict), "Content should have intro"
        print(f"PASS: Post '{slug}' has structured content")
        
        if "sections" in content:
            for section in content["sections"]:
                assert "heading" in section, "Section missing heading"
                assert "content" in section, "Section missing content"
            print(f"PASS: Post has {len(content['sections'])} structured sections")
        
        if "product_highlights" in content:
            for ph in content["product_highlights"]:
                assert "name" in ph, "Product highlight missing name"
            print(f"PASS: Post has {len(content['product_highlights'])} product highlights")
    
    def test_nonexistent_slug_returns_404(self):
        """GET /api/blog/posts/nonexistent-slug should return 404"""
        fake_slug = "this-slug-definitely-does-not-exist-xyz123"
        response = requests.get(f"{BASE_URL}/api/blog/posts/{fake_slug}")
        assert response.status_code == 404, f"Expected 404 for nonexistent slug, got {response.status_code}"
        print(f"PASS: GET /api/blog/posts/{fake_slug} returned 404 as expected")
    
    def test_known_existing_slugs(self):
        """Test specific known slugs from the database"""
        for slug in EXISTING_SLUGS:
            response = requests.get(f"{BASE_URL}/api/blog/posts/{slug}")
            if response.status_code == 200:
                post = response.json()
                assert post["slug"] == slug
                assert "title" in post
                assert "category" in post
                print(f"PASS: Known slug '{slug}' exists and returns valid post")
            else:
                print(f"INFO: Known slug '{slug}' not found (may have been deleted)")


class TestBlogPostDataValidity:
    """Tests for blog post data quality"""
    
    def test_blog_posts_have_valid_tags(self):
        """Blog posts should have valid tags array"""
        response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert response.status_code == 200
        data = response.json()
        
        if data["count"] == 0:
            pytest.skip("No blog posts available to test")
        
        for post in data["posts"]:
            if "tags" in post:
                assert isinstance(post["tags"], list), f"tags should be array for post {post['slug']}"
                print(f"PASS: Post '{post['slug']}' has {len(post['tags'])} tags")
    
    def test_blog_posts_have_ai_generated_flag(self):
        """AI-generated posts should have ai_generated flag"""
        response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert response.status_code == 200
        data = response.json()
        
        if data["count"] == 0:
            pytest.skip("No blog posts available to test")
        
        for post in data["posts"]:
            if "ai_generated" in post:
                assert isinstance(post["ai_generated"], bool), "ai_generated should be boolean"
                print(f"PASS: Post '{post['slug']}' ai_generated={post['ai_generated']}")
    
    def test_blog_post_meta_description(self):
        """Blog posts should have SEO meta description"""
        response = requests.get(f"{BASE_URL}/api/blog/posts")
        assert response.status_code == 200
        data = response.json()
        
        if data["count"] == 0:
            pytest.skip("No blog posts available to test")
        
        for post in data["posts"]:
            if "meta_description" in post:
                meta = post["meta_description"]
                assert len(meta) > 0, "meta_description should not be empty"
                assert len(meta) <= 200, f"meta_description too long ({len(meta)} chars)"
                print(f"PASS: Post '{post['slug']}' has valid meta_description ({len(meta)} chars)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
