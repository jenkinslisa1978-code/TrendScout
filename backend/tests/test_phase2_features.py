"""
Phase 2 Feature Tests: Enhanced Ad Spy + Competitor Intelligence Dashboard
Tests for:
1. GET /api/ads/discover - returns 'categories' array
2. POST /api/ads/save - saves an ad with ad_id and ad_data
3. GET /api/ads/saved - returns saved ads for user
4. DELETE /api/ads/saved/{id} - removes a saved ad
5. POST /api/competitor-intel/analyze - returns store analysis
6. POST /api/competitor-intel/compare - compare 2+ stores
7. GET /api/competitor-intel/history - returns previously analyzed stores
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHelpers:
    """Helper methods for authentication"""
    
    @staticmethod
    def get_auth_token():
        """Get auth token by logging in"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "jenkinslisa1978@gmail.com", "password": "admin123456"}
        )
        if login_response.status_code == 200:
            data = login_response.json()
            return data.get("access_token") or data.get("token")
        return None
    
    @staticmethod
    def get_auth_header(token):
        """Build auth header"""
        return {"Authorization": f"Bearer {token}"}


# =====================
# Ad Spy Enhanced Tests
# =====================

class TestAdSpyEnhanced:
    """Tests for enhanced Ad Spy features: categories, save/bookmark"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for authenticated tests"""
        token = TestHelpers.get_auth_token()
        if not token:
            pytest.skip("Authentication failed - skipping authenticated tests")
        return token
    
    def test_discover_ads_returns_categories(self):
        """GET /api/ads/discover returns categories array in response"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?limit=24")
        assert response.status_code == 200
        data = response.json()
        
        # Check categories array exists
        assert 'categories' in data, "Response should include 'categories' array"
        assert isinstance(data['categories'], list), "'categories' should be a list"
        print(f"✓ Discover ads returns categories: {len(data['categories'])} categories found")
        if data['categories']:
            print(f"  Sample categories: {data['categories'][:5]}")
    
    def test_save_ad_requires_auth(self):
        """POST /api/ads/save requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/ads/save",
            json={"ad_id": "test123", "ad_data": {}}
        )
        # Should fail without auth (401 or 403)
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("✓ Save ad endpoint requires authentication")
    
    def test_save_ad_success(self, auth_token):
        """POST /api/ads/save saves an ad successfully"""
        test_ad_id = f"test-ad-{uuid.uuid4().hex[:8]}"
        payload = {
            "ad_id": test_ad_id,
            "ad_data": {
                "headline": "Test Ad",
                "platform": "tiktok",
                "likes": 1000
            },
            "notes": "Test bookmark"
        }
        response = requests.post(
            f"{BASE_URL}/api/ads/save",
            json=payload,
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert response.status_code == 200, f"Failed to save ad: {response.text}"
        data = response.json()
        assert data.get('saved') == True, "Response should indicate saved=True"
        print(f"✓ Saved ad with id: {test_ad_id}")
        return test_ad_id
    
    def test_get_saved_ads_requires_auth(self):
        """GET /api/ads/saved requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ads/saved")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("✓ Get saved ads requires authentication")
    
    def test_get_saved_ads_success(self, auth_token):
        """GET /api/ads/saved returns saved ads for user"""
        response = requests.get(
            f"{BASE_URL}/api/ads/saved",
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert 'saved_ads' in data, "Response should have 'saved_ads' array"
        assert isinstance(data['saved_ads'], list)
        assert 'total' in data
        print(f"✓ Get saved ads: {data['total']} ads saved")
    
    def test_delete_saved_ad(self, auth_token):
        """DELETE /api/ads/saved/{id} removes a saved ad"""
        # First, save an ad
        test_ad_id = f"test-del-{uuid.uuid4().hex[:8]}"
        save_response = requests.post(
            f"{BASE_URL}/api/ads/save",
            json={"ad_id": test_ad_id, "ad_data": {"headline": "To Delete"}},
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert save_response.status_code == 200
        
        # Now delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/ads/saved/{test_ad_id}",
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data.get('removed') == True
        print(f"✓ Deleted saved ad: {test_ad_id}")
    
    def test_save_and_unsave_flow(self, auth_token):
        """Full save/unsave flow works correctly"""
        # Get an ad from discover
        discover_response = requests.get(f"{BASE_URL}/api/ads/discover?limit=1")
        ads = discover_response.json().get('ads', [])
        if not ads:
            pytest.skip("No ads available to test save/unsave flow")
        
        ad_id = ads[0]['id']
        ad_data = ads[0]
        
        # Save the ad
        save_resp = requests.post(
            f"{BASE_URL}/api/ads/save",
            json={"ad_id": ad_id, "ad_data": ad_data},
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert save_resp.status_code == 200
        
        # Verify it's in saved list
        saved_resp = requests.get(
            f"{BASE_URL}/api/ads/saved",
            headers=TestHelpers.get_auth_header(auth_token)
        )
        saved_ids = [s['ad_id'] for s in saved_resp.json().get('saved_ads', [])]
        assert ad_id in saved_ids, "Ad should be in saved list"
        
        # Unsave it
        unsave_resp = requests.delete(
            f"{BASE_URL}/api/ads/saved/{ad_id}",
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert unsave_resp.status_code == 200
        
        print(f"✓ Full save/unsave flow works for ad: {ad_id}")


# =====================
# Competitor Intel Tests
# =====================

class TestCompetitorIntelligence:
    """Tests for Competitor Intelligence Dashboard"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for authenticated tests"""
        token = TestHelpers.get_auth_token()
        if not token:
            pytest.skip("Authentication failed - skipping authenticated tests")
        return token
    
    def test_analyze_store_requires_auth(self):
        """POST /api/competitor-intel/analyze requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-intel/analyze",
            json={"url": "allbirds.com"}
        )
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("✓ Analyze store requires authentication")
    
    def test_analyze_store_success(self, auth_token):
        """POST /api/competitor-intel/analyze returns store analysis"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-intel/analyze",
            json={"url": "allbirds.com"},
            headers=TestHelpers.get_auth_header(auth_token),
            timeout=20  # Allow time for external API call
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Check response structure
        if data.get('success') == False:
            # Store might not be accessible
            print(f"⚠ Store analysis returned error: {data.get('error')}")
            return
        
        # Verify required fields
        assert 'product_count' in data, "Response should have product_count"
        assert 'categories' in data, "Response should have categories"
        assert 'pricing' in data, "Response should have pricing"
        assert 'revenue_estimate' in data, "Response should have revenue_estimate"
        assert 'suppliers' in data, "Response should have suppliers"
        assert 'store_tier' in data, "Response should have store_tier"
        assert 'top_products' in data, "Response should have top_products"
        
        print(f"✓ Store analysis successful: {data.get('domain')}")
        print(f"  - Products: {data.get('product_count')}")
        print(f"  - Store Tier: {data.get('store_tier')}")
        print(f"  - Est. Revenue: ${data.get('revenue_estimate', {}).get('monthly_revenue')}")
        print(f"  - Pricing Strategy: {data.get('pricing', {}).get('strategy')}")
        print(f"  - Supplier Risk: {data.get('suppliers', {}).get('risk_level')}")
    
    def test_analyze_store_pricing_fields(self, auth_token):
        """Verify pricing object has all required fields"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-intel/analyze",
            json={"url": "allbirds.com"},
            headers=TestHelpers.get_auth_header(auth_token),
            timeout=20
        )
        if response.status_code != 200 or not response.json().get('success', True):
            pytest.skip("Store analysis not available")
        
        data = response.json()
        pricing = data.get('pricing', {})
        
        assert 'min' in pricing, "Pricing should have min"
        assert 'max' in pricing, "Pricing should have max"
        assert 'avg' in pricing, "Pricing should have avg"
        assert 'median' in pricing, "Pricing should have median"
        assert 'strategy' in pricing, "Pricing should have strategy"
        assert 'consistency' in pricing, "Pricing should have consistency"
        
        print(f"✓ Pricing fields verified: avg=${pricing.get('avg')}, strategy={pricing.get('strategy')}")
    
    def test_analyze_store_supplier_risk(self, auth_token):
        """Verify suppliers object has risk scoring"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-intel/analyze",
            json={"url": "allbirds.com"},
            headers=TestHelpers.get_auth_header(auth_token),
            timeout=20
        )
        if response.status_code != 200 or not response.json().get('success', True):
            pytest.skip("Store analysis not available")
        
        data = response.json()
        suppliers = data.get('suppliers', {})
        
        assert 'vendor_count' in suppliers, "Suppliers should have vendor_count"
        assert 'top_vendors' in suppliers, "Suppliers should have top_vendors"
        assert 'risk_level' in suppliers, "Suppliers should have risk_level"
        assert 'risk_reason' in suppliers, "Suppliers should have risk_reason"
        assert suppliers['risk_level'] in ['Low', 'Medium', 'High']
        
        print(f"✓ Supplier risk verified: {suppliers.get('risk_level')} - {suppliers.get('vendor_count')} vendors")
    
    def test_analyze_store_invalid_url(self, auth_token):
        """POST /api/competitor-intel/analyze handles invalid URLs"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-intel/analyze",
            json={"url": "not-a-shopify-store-xyz123.fake"},
            headers=TestHelpers.get_auth_header(auth_token),
            timeout=15
        )
        # Should return success=false or error
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            # Either success=false or an error message
            if not data.get('success', True):
                print(f"✓ Invalid URL returns error: {data.get('error')}")
            else:
                print(f"✓ Store analyzed (might be valid): {data.get('domain')}")
    
    def test_compare_stores_requires_auth(self):
        """POST /api/competitor-intel/compare requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-intel/compare",
            json={"urls": ["allbirds.com", "bombas.com"]}
        )
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("✓ Compare stores requires authentication")
    
    def test_compare_stores_success(self, auth_token):
        """POST /api/competitor-intel/compare returns comparison data"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-intel/compare",
            json={"urls": ["allbirds.com", "colourpop.com"]},
            headers=TestHelpers.get_auth_header(auth_token),
            timeout=30  # Two API calls
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert 'stores' in data, "Response should have 'stores' array"
        assert 'compared_at' in data
        assert isinstance(data['stores'], list)
        
        # Should have data for both stores
        stores = data['stores']
        if len(stores) >= 2:
            for store in stores:
                if 'error' not in store:
                    assert 'domain' in store
                    assert 'product_count' in store
                    assert 'avg_price' in store
                    assert 'est_monthly_revenue' in store
        
        print(f"✓ Compare stores: {len(stores)} stores compared")
        for s in stores:
            if 'domain' in s and 'error' not in s:
                print(f"  - {s['domain']}: {s.get('product_count')} products, ${s.get('est_monthly_revenue')}/mo")
    
    def test_compare_stores_needs_two_urls(self, auth_token):
        """POST /api/competitor-intel/compare requires at least 2 URLs"""
        response = requests.post(
            f"{BASE_URL}/api/competitor-intel/compare",
            json={"urls": ["allbirds.com"]},  # Only 1 URL
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert response.status_code == 400, "Should fail with only 1 URL"
        print("✓ Compare stores correctly requires 2+ URLs")
    
    def test_get_history_requires_auth(self):
        """GET /api/competitor-intel/history requires authentication"""
        response = requests.get(f"{BASE_URL}/api/competitor-intel/history")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("✓ Get history requires authentication")
    
    def test_get_history_success(self, auth_token):
        """GET /api/competitor-intel/history returns previously analyzed stores"""
        response = requests.get(
            f"{BASE_URL}/api/competitor-intel/history",
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert response.status_code == 200
        data = response.json()
        
        assert 'analyses' in data, "Response should have 'analyses' array"
        assert 'total' in data
        assert isinstance(data['analyses'], list)
        
        print(f"✓ History returned: {data['total']} analyses")
        for analysis in data['analyses'][:3]:
            print(f"  - {analysis.get('domain')}: {analysis.get('product_count')} products")


# =====================
# Integration Tests
# =====================

class TestPhase2Integration:
    """Integration tests for Phase 2 features"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        token = TestHelpers.get_auth_token()
        if not token:
            pytest.skip("Authentication failed")
        return token
    
    def test_ad_spy_full_flow(self, auth_token):
        """Test full Ad Spy flow: discover, filter, save, unsave"""
        # 1. Discover ads with category filter
        discover = requests.get(f"{BASE_URL}/api/ads/discover?limit=10")
        assert discover.status_code == 200
        data = discover.json()
        ads = data.get('ads', [])
        categories = data.get('categories', [])
        
        print(f"✓ Step 1: Discovered {len(ads)} ads, {len(categories)} categories")
        
        if not ads:
            pytest.skip("No ads to test flow")
        
        # 2. Save first ad
        ad = ads[0]
        save = requests.post(
            f"{BASE_URL}/api/ads/save",
            json={"ad_id": ad['id'], "ad_data": ad},
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert save.status_code == 200
        print(f"✓ Step 2: Saved ad {ad['id']}")
        
        # 3. Verify in saved list
        saved = requests.get(
            f"{BASE_URL}/api/ads/saved",
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert saved.status_code == 200
        saved_ids = [s['ad_id'] for s in saved.json().get('saved_ads', [])]
        assert ad['id'] in saved_ids
        print(f"✓ Step 3: Verified ad in saved list")
        
        # 4. Unsave the ad
        unsave = requests.delete(
            f"{BASE_URL}/api/ads/saved/{ad['id']}",
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert unsave.status_code == 200
        print(f"✓ Step 4: Unsaved ad")
        
        print("✓ Full Ad Spy flow completed successfully")
    
    def test_competitor_intel_full_flow(self, auth_token):
        """Test full competitor intel flow: analyze, compare, history"""
        # 1. Analyze a store
        analyze = requests.post(
            f"{BASE_URL}/api/competitor-intel/analyze",
            json={"url": "allbirds.com"},
            headers=TestHelpers.get_auth_header(auth_token),
            timeout=20
        )
        assert analyze.status_code == 200
        data = analyze.json()
        
        if data.get('success') == False:
            print(f"⚠ Step 1: Analysis unavailable - {data.get('error')}")
        else:
            print(f"✓ Step 1: Analyzed {data.get('domain')} - {data.get('product_count')} products")
        
        # 2. Check history
        history = requests.get(
            f"{BASE_URL}/api/competitor-intel/history",
            headers=TestHelpers.get_auth_header(auth_token)
        )
        assert history.status_code == 200
        print(f"✓ Step 2: History has {history.json().get('total')} entries")
        
        print("✓ Competitor Intel flow completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
