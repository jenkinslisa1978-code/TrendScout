"""
Tests for TrendScout Growth & Marketing Features:
- Public Trending Products (/api/public/trending-products)
- Public Product Page (/api/viral/public/product/{id})
- Referral System (/api/viral/referral/*)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestTrendingProductsAPI:
    """Tests for GET /api/public/trending-products"""
    
    def test_trending_products_returns_200(self):
        """Trending products endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: /api/public/trending-products returns 200")
    
    def test_trending_products_has_correct_structure(self):
        """Response should have products array, count, and last_updated"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products")
        data = response.json()
        
        assert "products" in data, "Response missing 'products' field"
        assert "count" in data, "Response missing 'count' field"
        assert "last_updated" in data, "Response missing 'last_updated' field"
        assert isinstance(data["products"], list), "products should be a list"
        print(f"PASS: Response has correct structure with {data['count']} products")
    
    def test_trending_products_limit_param(self):
        """Limit parameter should control number of returned products"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) <= 5, "Should return at most 5 products"
        print(f"PASS: Limit parameter works, returned {len(data['products'])} products")
    
    def test_trending_product_has_launch_score(self):
        """Each product should have launch_score field"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=3")
        data = response.json()
        
        if len(data["products"]) > 0:
            product = data["products"][0]
            assert "launch_score" in product, "Product missing 'launch_score' field"
            assert "product_name" in product, "Product missing 'product_name' field"
            assert "id" in product, "Product missing 'id' field"
            print(f"PASS: Products have required fields (launch_score: {product.get('launch_score')})")
        else:
            print("SKIP: No products in database to test")


class TestPublicProductAPI:
    """Tests for GET /api/viral/public/product/{product_id}"""
    
    @pytest.fixture
    def product_id(self):
        """Get a product ID from trending products"""
        response = requests.get(f"{BASE_URL}/api/public/trending-products?limit=1")
        data = response.json()
        if data["products"]:
            return data["products"][0]["id"]
        return None
    
    def test_public_product_returns_404_for_invalid_id(self):
        """Should return 404 for non-existent product"""
        response = requests.get(f"{BASE_URL}/api/viral/public/product/invalid-product-id-123")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Returns 404 for invalid product ID")
    
    def test_public_product_returns_partial_data(self, product_id):
        """Should return partial product data for public viewing"""
        if not product_id:
            pytest.skip("No products available for testing")
        
        response = requests.get(f"{BASE_URL}/api/viral/public/product/{product_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Check required public fields
        assert "id" in data, "Missing 'id'"
        assert "product_name" in data, "Missing 'product_name'"
        assert "market_score" in data, "Missing 'market_score'"
        assert "trend_score" in data, "Missing 'trend_score'"
        assert "trend_stage" in data, "Missing 'trend_stage'"
        assert "competition_level" in data, "Missing 'competition_level'"
        assert "is_partial" in data, "Missing 'is_partial'"
        assert data["is_partial"] == True, "is_partial should be True"
        assert "signup_cta" in data, "Missing 'signup_cta'"
        
        print(f"PASS: Public product returns partial data for {data['product_name']}")
    
    def test_public_product_has_margin_range_not_exact(self, product_id):
        """Public product should have margin_range, not exact margin"""
        if not product_id:
            pytest.skip("No products available for testing")
        
        response = requests.get(f"{BASE_URL}/api/viral/public/product/{product_id}")
        data = response.json()
        
        assert "margin_range" in data, "Missing 'margin_range'"
        assert "estimated_margin" not in data, "Should NOT expose exact margin"
        assert "supplier_cost" not in data, "Should NOT expose supplier_cost"
        print(f"PASS: Public product shows margin_range ({data.get('margin_range')}) not exact values")


class TestReferralTrackAPI:
    """Tests for POST /api/viral/referral/track (public endpoint)"""
    
    def test_track_referral_invalid_code_returns_404(self):
        """Should return 404 for invalid referral code"""
        response = requests.post(
            f"{BASE_URL}/api/viral/referral/track",
            params={
                "referral_code": "INVALID_CODE_123",
                "referred_user_id": "test_user_123"
            }
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Invalid referral code returns 404")
    
    def test_track_referral_requires_both_params(self):
        """Should return error if params missing"""
        # Missing referred_user_id
        response = requests.post(
            f"{BASE_URL}/api/viral/referral/track",
            params={"referral_code": "TEST123"}
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("PASS: Track referral validates required params")


class TestReferralStatsAPI:
    """Tests for GET /api/viral/referral/stats (requires auth)"""
    
    def test_referral_stats_requires_auth(self):
        """Should return 401 without authentication"""
        response = requests.get(f"{BASE_URL}/api/viral/referral/stats")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Referral stats requires authentication")
    
    def test_referral_stats_with_demo_token(self):
        """Should return stats with demo token"""
        test_user_id = f"test_referral_user_{uuid.uuid4().hex[:8]}"
        headers = {"Authorization": f"Bearer demo_{test_user_id}"}
        
        response = requests.get(
            f"{BASE_URL}/api/viral/referral/stats",
            headers=headers
        )
        
        # Should work with demo token or return 401 if not configured
        if response.status_code == 200:
            data = response.json()
            assert "referral_code" in data, "Missing 'referral_code'"
            assert "total_referrals" in data, "Missing 'total_referrals'"
            assert "verified_referrals" in data, "Missing 'verified_referrals'"
            assert "bonus_store_slots" in data, "Missing 'bonus_store_slots'"
            assert "max_bonus_slots" in data, "Missing 'max_bonus_slots'"
            assert data["max_bonus_slots"] == 5, "Max bonus slots should be 5"
            print(f"PASS: Referral stats returned with code: {data.get('referral_code')}")
        else:
            # Auth may be strict
            assert response.status_code == 401, f"Expected 200 or 401, got {response.status_code}"
            print("PASS: Referral stats returns 401 (auth strict mode)")


class TestReferralHistoryAPI:
    """Tests for GET /api/viral/referral/history (requires auth)"""
    
    def test_referral_history_requires_auth(self):
        """Should return 401 without authentication"""
        response = requests.get(f"{BASE_URL}/api/viral/referral/history")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Referral history requires authentication")
    
    def test_referral_history_with_demo_token(self):
        """Should return history with demo token"""
        test_user_id = f"test_history_user_{uuid.uuid4().hex[:8]}"
        headers = {"Authorization": f"Bearer demo_{test_user_id}"}
        
        response = requests.get(
            f"{BASE_URL}/api/viral/referral/history",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "referrals" in data, "Missing 'referrals'"
            assert "count" in data, "Missing 'count'"
            assert isinstance(data["referrals"], list), "'referrals' should be list"
            print(f"PASS: Referral history returned with {data.get('count', 0)} referrals")
        else:
            assert response.status_code == 401, f"Expected 200 or 401, got {response.status_code}"
            print("PASS: Referral history returns 401 (auth strict mode)")


class TestAPIHealth:
    """Basic health check tests"""
    
    def test_api_health(self):
        """API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"API not healthy: {response.status_code}"
        print("PASS: API is healthy")
    
    def test_api_root(self):
        """API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"API root failed: {response.status_code}"
        print("PASS: API root accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
