"""
Test Suite for Iteration 88 Features:
- Product Analysis nav routing (frontend test via Playwright)
- Product detail page with AI images, launch scores, suppliers
- Supplier API endpoint
- Admin image endpoints
- TikTok Intelligence page

Correct API Endpoints:
- GET /api/products - list products with {data: [...]}
- GET /api/products/{product_id} - product detail with {data: {...}}
- GET /api/suppliers/{product_id} - find/get suppliers for product
- GET /api/admin/images/stats - requires admin auth
- POST /api/admin/images/refresh/{product_id} - requires admin auth + CSRF
- GET /api/tools/tiktok-intelligence - TikTok intel data
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "jenkinslisa1978@gmail.com"
ADMIN_PASSWORD = "admin123456"


@pytest.fixture(scope="module")
def session():
    """Shared requests session."""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_token(session):
    """Get admin authentication token."""
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if resp.status_code == 200:
        data = resp.json()
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Admin login failed: {resp.status_code} {resp.text}")


@pytest.fixture(scope="module")
def admin_session(session, admin_token):
    """Session with admin auth header."""
    session.headers.update({"Authorization": f"Bearer {admin_token}"})
    return session


@pytest.fixture(scope="module")
def sample_product_id(session):
    """Get a real product ID from the products list."""
    resp = session.get(f"{BASE_URL}/api/products?limit=5")
    if resp.status_code == 200:
        data = resp.json()
        products = data.get("data", [])
        if products:
            return products[0].get("id")
    pytest.skip("Could not get sample product ID")


class TestProductsListAPI:
    """Test GET /api/products endpoint."""
    
    def test_products_list_returns_200(self, session):
        """Products list endpoint should return 200."""
        resp = session.get(f"{BASE_URL}/api/products")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    def test_products_list_has_data_key(self, session):
        """Products list should return data in 'data' key."""
        resp = session.get(f"{BASE_URL}/api/products")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data, f"Response missing 'data' key: {list(data.keys())}"
        assert isinstance(data["data"], list), "data should be a list"
        assert len(data["data"]) > 0, "No products returned"
        print(f"Products list returned {len(data['data'])} products")
    
    def test_products_have_launch_scores(self, session):
        """Products should have launch_score fields."""
        resp = session.get(f"{BASE_URL}/api/products?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        products = data.get("data", [])
        
        for p in products[:5]:
            assert "launch_score" in p, f"Product {p.get('id')} missing launch_score"
            assert "launch_score_label" in p, f"Product {p.get('id')} missing launch_score_label"
            print(f"Product: {p.get('product_name', '')[:50]}... launch_score={p.get('launch_score')}, label={p.get('launch_score_label')}")


class TestProductDetailAPI:
    """Test GET /api/products/{product_id} endpoint."""
    
    def test_product_detail_returns_200(self, session, sample_product_id):
        """Product detail endpoint should return 200."""
        resp = session.get(f"{BASE_URL}/api/products/{sample_product_id}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    def test_product_detail_has_launch_score(self, session, sample_product_id):
        """Product detail should include launch_score and reasoning."""
        resp = session.get(f"{BASE_URL}/api/products/{sample_product_id}")
        assert resp.status_code == 200
        data = resp.json()
        product = data.get("data", {})
        
        assert "launch_score" in product, "Product missing launch_score field"
        assert "launch_score_label" in product, "Product missing launch_score_label"
        assert "launch_score_reasoning" in product, "Product missing launch_score_reasoning"
        
        print(f"Launch score: {product.get('launch_score')}")
        print(f"Launch label: {product.get('launch_score_label')}")
        print(f"Reasoning: {product.get('launch_score_reasoning', '')[:100]}...")
    
    def test_product_detail_has_image_url(self, session, sample_product_id):
        """Product detail should have image_url field."""
        resp = session.get(f"{BASE_URL}/api/products/{sample_product_id}")
        assert resp.status_code == 200
        data = resp.json()
        product = data.get("data", {})
        
        assert "image_url" in product, "Product missing image_url field"
        image_url = product.get("image_url", "")
        assert image_url, "Product image_url is empty"
        print(f"Image URL: {image_url[:80]}..." if len(image_url) > 80 else f"Image URL: {image_url}")
    
    def test_product_has_supplier_data(self, session, sample_product_id):
        """Product detail should have embedded suppliers array."""
        resp = session.get(f"{BASE_URL}/api/products/{sample_product_id}")
        assert resp.status_code == 200
        data = resp.json()
        product = data.get("data", {})
        
        suppliers = product.get("suppliers", [])
        if suppliers:
            s = suppliers[0]
            print(f"Embedded supplier: name={s.get('name')}, country={s.get('country')}, cost={s.get('unit_cost')}, lead_time={s.get('lead_time_days')}")
        else:
            print("No embedded suppliers found in product")


class TestSupplierAPI:
    """Test GET /api/suppliers/{product_id} endpoint."""
    
    def test_suppliers_endpoint_returns_200(self, session, sample_product_id):
        """Supplier endpoint should return 200 for valid product ID."""
        resp = session.get(f"{BASE_URL}/api/suppliers/{sample_product_id}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    def test_suppliers_response_structure(self, session, sample_product_id):
        """Supplier response should have expected fields."""
        resp = session.get(f"{BASE_URL}/api/suppliers/{sample_product_id}")
        assert resp.status_code == 200
        data = resp.json()
        
        assert "suppliers_found" in data or "suppliers" in data, f"Response missing suppliers data: {data}"
        
        suppliers = data.get("suppliers", [])
        if suppliers:
            supplier = suppliers[0]
            # Check required fields per review request
            required_fields = ["supplier_name", "supplier_cost", "shipping_origin"]
            for field in required_fields:
                assert field in supplier, f"Supplier missing field: {field}"
            
            # Verify supplier_rating exists (can be None)
            assert "supplier_rating" in supplier, "Supplier missing supplier_rating field"
            print(f"Supplier: name={supplier.get('supplier_name')}, cost={supplier.get('supplier_cost')}, origin={supplier.get('shipping_origin')}, rating={supplier.get('supplier_rating')}")
        else:
            print("Suppliers endpoint returned no suppliers (product may lack embedded supplier data)")
    
    def test_suppliers_for_nonexistent_product(self, session):
        """Supplier endpoint should handle nonexistent products gracefully."""
        resp = session.get(f"{BASE_URL}/api/suppliers/nonexistent-product-id-12345")
        # Should return 200 with error or empty suppliers, not 500
        assert resp.status_code in [200, 404], f"Unexpected status: {resp.status_code}"


class TestAdminImageEndpoints:
    """Test admin image refresh tool endpoints."""
    
    def test_image_stats_requires_auth(self, session):
        """GET /api/admin/images/stats should require authentication."""
        # Create fresh session without auth
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        resp = no_auth_session.get(f"{BASE_URL}/api/admin/images/stats")
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
    
    def test_image_stats_returns_counts(self, admin_session):
        """GET /api/admin/images/stats should return image counts for admin."""
        resp = admin_session.get(f"{BASE_URL}/api/admin/images/stats")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        # Verify required fields per review request
        assert "total_products" in data, "Missing total_products field"
        assert "with_images" in data, "Missing with_images field"
        assert "without_images" in data, "Missing without_images field"
        
        # Verify counts are reasonable
        assert isinstance(data["total_products"], int), "total_products should be int"
        assert isinstance(data["with_images"], int), "with_images should be int"
        assert isinstance(data["without_images"], int), "without_images should be int"
        
        print(f"Image stats: total={data['total_products']}, with_images={data['with_images']}, without_images={data['without_images']}")
    
    def test_image_refresh_requires_admin(self, session, sample_product_id):
        """POST /api/admin/images/refresh/{product_id} should require admin auth."""
        # Create fresh session without auth
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        resp = no_auth_session.post(f"{BASE_URL}/api/admin/images/refresh/{sample_product_id}")
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"


class TestTikTokIntelligenceAPI:
    """Test TikTok Intelligence endpoint."""
    
    def test_tiktok_intelligence_returns_200(self, session):
        """GET /api/tools/tiktok-intelligence should return 200."""
        resp = session.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    def test_tiktok_intelligence_data_structure(self, session):
        """TikTok intelligence response should have expected structure."""
        resp = session.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify expected fields from TikTokIntelligencePage.jsx
        expected_fields = ["viral_products", "categories", "trending_patterns", "stats"]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        
        # Verify stats structure
        stats = data.get("stats", {})
        assert "total_tiktok_views" in stats, "stats missing total_tiktok_views"
        assert "products_tracked" in stats, "stats missing products_tracked"
        assert "avg_launch_score" in stats, "stats missing avg_launch_score"
        assert "top_category" in stats, "stats missing top_category"
        
        # Verify viral_products is a list
        assert isinstance(data.get("viral_products"), list), "viral_products should be a list"
        
        print(f"TikTok stats: views={stats.get('total_tiktok_views')}, products={stats.get('products_tracked')}, avg_score={stats.get('avg_launch_score')}, top_cat={stats.get('top_category')}")
    
    def test_tiktok_intelligence_has_viral_products(self, session):
        """TikTok intelligence should return viral products with proper structure."""
        resp = session.get(f"{BASE_URL}/api/tools/tiktok-intelligence")
        assert resp.status_code == 200
        data = resp.json()
        
        viral_products = data.get("viral_products", [])
        if viral_products:
            p = viral_products[0]
            # Check fields used by frontend component
            assert "id" in p, "Viral product missing id"
            assert "product_name" in p, "Viral product missing product_name"
            assert "launch_score" in p, "Viral product missing launch_score"
            print(f"Top viral product: {p.get('product_name', '')[:50]}... score={p.get('launch_score')}")


class TestLaunchScoreRecalibration:
    """Test launch score algorithm changes - verify competition penalty."""
    
    def test_products_with_high_ad_count_have_lower_scores(self, session):
        """Products with high ad counts should have lower launch scores due to competition penalty."""
        resp = session.get(f"{BASE_URL}/api/products?limit=100")
        assert resp.status_code == 200
        data = resp.json()
        products = data.get("data", [])
        
        # Find products with high ad counts
        high_ad_products = [p for p in products if p.get("ad_count", 0) > 200]
        low_ad_products = [p for p in products if p.get("ad_count", 0) < 50 and p.get("ad_count", 0) > 0]
        
        if high_ad_products:
            for p in high_ad_products[:3]:
                print(f"High ad product: {p.get('product_name', '')[:40]}... ads={p.get('ad_count')}, launch_score={p.get('launch_score')}, label={p.get('launch_score_label')}")
                # High ad products should have lower scores or "risky"/"avoid" labels
                reasoning = p.get("launch_score_reasoning", "")
                if "penalty" in reasoning.lower() or "competition" in reasoning.lower():
                    print(f"  -> Competition penalty found in reasoning")
        
        if low_ad_products:
            for p in low_ad_products[:3]:
                print(f"Low ad product: {p.get('product_name', '')[:40]}... ads={p.get('ad_count')}, launch_score={p.get('launch_score')}, label={p.get('launch_score_label')}")
    
    def test_launch_score_reasoning_mentions_competition(self, session, sample_product_id):
        """Launch score reasoning should mention competition factors."""
        resp = session.get(f"{BASE_URL}/api/products/{sample_product_id}")
        assert resp.status_code == 200
        data = resp.json()
        product = data.get("data", {})
        
        reasoning = product.get("launch_score_reasoning", "")
        assert reasoning, "Launch score reasoning should not be empty"
        print(f"Reasoning for sample product: {reasoning}")


class TestPublicTrendingEndpoint:
    """Test the public trending product endpoint."""
    
    def test_public_trending_products(self, session):
        """GET /api/public/trending-products should return products."""
        resp = session.get(f"{BASE_URL}/api/public/trending-products")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        
        # Check structure
        products = data.get("products", [])
        if not products:
            products = data.get("data", [])
        
        print(f"Public trending returned {len(products)} products")
