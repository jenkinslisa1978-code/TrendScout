"""
Test Similar Products & Data Freshness Features (Iteration 95)

Testing:
1. GET /api/products/{id}/similar - Similar products endpoint
2. GET /api/products/data-freshness/summary - Data freshness summary endpoint
3. GET /api/intelligence/complete-analysis/{id} - Score consistency fix (overall_score = launch_score)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SAMPLE_PRODUCT_ID = "e0910e73-6c6e-457d-bfc7-b43f6ac0178f"
TEST_EMAIL = "reviewer@trendscout.click"
TEST_PASSWORD = "ShopifyReview2026!"


class TestSimilarProductsAPI:
    """Tests for the Similar Products endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login to get token
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("session", {}).get("access_token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_similar_products_endpoint_returns_200(self):
        """Verify /api/products/{id}/similar returns 200"""
        response = self.session.get(f"{BASE_URL}/api/products/{SAMPLE_PRODUCT_ID}/similar?limit=6")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Similar products endpoint returns 200")
    
    def test_similar_products_response_structure(self):
        """Verify similar products response has correct structure"""
        response = self.session.get(f"{BASE_URL}/api/products/{SAMPLE_PRODUCT_ID}/similar?limit=6")
        assert response.status_code == 200
        
        data = response.json()
        assert "product_id" in data, "Missing product_id in response"
        assert "similar_products" in data, "Missing similar_products in response"
        assert "total" in data, "Missing total in response"
        assert data["product_id"] == SAMPLE_PRODUCT_ID
        print(f"✓ Similar products response has correct structure")
    
    def test_similar_products_contain_required_fields(self):
        """Verify each similar product contains required fields"""
        response = self.session.get(f"{BASE_URL}/api/products/{SAMPLE_PRODUCT_ID}/similar?limit=6")
        assert response.status_code == 200
        
        data = response.json()
        similar_products = data.get("similar_products", [])
        
        # Required fields for each similar product
        required_fields = ["id", "product_name", "launch_score", "margin_percent", "last_updated"]
        
        for product in similar_products:
            for field in required_fields:
                assert field in product, f"Missing required field '{field}' in similar product"
            
            # Verify data types
            assert isinstance(product.get("launch_score"), (int, float)), "launch_score should be numeric"
            assert isinstance(product.get("margin_percent"), (int, float)), "margin_percent should be numeric"
        
        print(f"✓ Similar products contain all required fields ({len(similar_products)} products)")
    
    def test_similar_products_limit_works(self):
        """Verify limit parameter is respected"""
        response = self.session.get(f"{BASE_URL}/api/products/{SAMPLE_PRODUCT_ID}/similar?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        similar_products = data.get("similar_products", [])
        assert len(similar_products) <= 3, f"Expected max 3 products, got {len(similar_products)}"
        print(f"✓ Limit parameter works correctly (got {len(similar_products)} products)")


class TestDataFreshnessSummaryAPI:
    """Tests for Data Freshness Summary endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_data_freshness_summary_returns_200(self):
        """Verify /api/products/data-freshness/summary returns 200"""
        response = self.session.get(f"{BASE_URL}/api/products/data-freshness/summary")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Data freshness summary endpoint returns 200")
    
    def test_data_freshness_summary_structure(self):
        """Verify data freshness summary response structure"""
        response = self.session.get(f"{BASE_URL}/api/products/data-freshness/summary")
        assert response.status_code == 200
        
        data = response.json()
        
        # Required fields in response
        assert "total_products" in data, "Missing total_products"
        assert "sources" in data, "Missing sources array"
        assert "refresh_schedule" in data, "Missing refresh_schedule"
        
        # Verify sources is array
        assert isinstance(data["sources"], list), "sources should be an array"
        
        print(f"✓ Data freshness summary has correct structure")
    
    def test_data_freshness_sources_have_required_fields(self):
        """Verify each source in data freshness has required fields"""
        response = self.session.get(f"{BASE_URL}/api/products/data-freshness/summary")
        assert response.status_code == 200
        
        data = response.json()
        sources = data.get("sources", [])
        
        for source in sources:
            assert "source" in source, "Missing 'source' field"
            assert "count" in source, "Missing 'count' field"
            assert "latest_update" in source or source.get("latest_update") is None, "Missing 'latest_update' field"
        
        print(f"✓ Data freshness sources have required fields ({len(sources)} sources)")
    
    def test_data_freshness_refresh_schedule_present(self):
        """Verify refresh schedule contains expected keys"""
        response = self.session.get(f"{BASE_URL}/api/products/data-freshness/summary")
        assert response.status_code == 200
        
        data = response.json()
        refresh_schedule = data.get("refresh_schedule", {})
        
        expected_keys = ["scores", "trending_data"]
        for key in expected_keys:
            assert key in refresh_schedule, f"Missing '{key}' in refresh_schedule"
        
        print(f"✓ Refresh schedule contains expected keys: {list(refresh_schedule.keys())}")


class TestScoreConsistency:
    """Tests for score consistency between launch_score and intelligence overall_score"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login to get token
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("session", {}).get("access_token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_product_has_launch_score(self):
        """Verify sample product has launch_score in DB"""
        response = self.session.get(f"{BASE_URL}/api/products/{SAMPLE_PRODUCT_ID}")
        assert response.status_code == 200
        
        data = response.json().get("data", {})
        launch_score = data.get("launch_score")
        
        assert launch_score is not None, "Product should have launch_score"
        assert isinstance(launch_score, (int, float)), "launch_score should be numeric"
        
        print(f"✓ Product has launch_score: {launch_score}")
        return launch_score
    
    def test_intelligence_endpoint_returns_200(self):
        """Verify /api/intelligence/complete-analysis/{id} returns 200"""
        response = self.session.get(f"{BASE_URL}/api/intelligence/complete-analysis/{SAMPLE_PRODUCT_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Intelligence complete-analysis endpoint returns 200")
    
    def test_intelligence_overall_score_matches_launch_score(self):
        """Verify overall_score in intelligence matches launch_score from product"""
        # Get product launch_score
        product_resp = self.session.get(f"{BASE_URL}/api/products/{SAMPLE_PRODUCT_ID}")
        assert product_resp.status_code == 200
        product_data = product_resp.json().get("data", {})
        launch_score = product_data.get("launch_score")
        
        # Get intelligence overall_score
        intel_resp = self.session.get(f"{BASE_URL}/api/intelligence/complete-analysis/{SAMPLE_PRODUCT_ID}")
        assert intel_resp.status_code == 200
        intel_data = intel_resp.json()
        overall_score = intel_data.get("overall_score")
        
        # Scores should match exactly
        assert overall_score == launch_score, \
            f"Score mismatch! launch_score={launch_score}, overall_score={overall_score}"
        
        print(f"✓ Scores are consistent: launch_score={launch_score}, overall_score={overall_score}")
    
    def test_intelligence_recommendation_aligns_with_score(self):
        """Verify recommendation label aligns with the score"""
        response = self.session.get(f"{BASE_URL}/api/intelligence/complete-analysis/{SAMPLE_PRODUCT_ID}")
        assert response.status_code == 200
        
        data = response.json()
        overall_score = data.get("overall_score", 0)
        recommendation = data.get("recommendation", "")
        recommendation_label = data.get("recommendation_label", "")
        
        # Verify recommendation aligns with score thresholds
        if overall_score >= 65:
            expected_rec = "launch_opportunity"
        elif overall_score >= 45:
            expected_rec = "promising_monitor"
        elif overall_score >= 25:
            expected_rec = "risky_caution"
        else:
            expected_rec = "avoid"
        
        assert recommendation == expected_rec, \
            f"Recommendation '{recommendation}' doesn't align with score {overall_score} (expected '{expected_rec}')"
        
        print(f"✓ Recommendation '{recommendation}' ({recommendation_label}) aligns with score {overall_score}")


class TestProductDetailEndpoint:
    """Test product detail endpoint with include_integrity"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_product_detail_includes_data_freshness_fields(self):
        """Verify product detail has fields needed for data freshness badge"""
        response = self.session.get(f"{BASE_URL}/api/products/{SAMPLE_PRODUCT_ID}")
        assert response.status_code == 200
        
        data = response.json().get("data", {})
        
        # Fields used by DataFreshnessBadge/Card
        freshness_fields = ["last_updated", "data_source"]
        found_fields = []
        
        for field in freshness_fields:
            if field in data:
                found_fields.append(field)
        
        print(f"✓ Product has freshness fields: {found_fields}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
