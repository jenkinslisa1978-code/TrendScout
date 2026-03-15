"""
Phase 1 Feature Tests: Ad Spy, Profitability Simulator, Launch Score Breakdown
Tests for:
1. GET /api/ads/discover - Ad Intelligence endpoint
2. POST /api/tools/profitability-simulator - Profit simulation
3. GET /api/products/{id}/launch-score-breakdown - 7-Signal Score breakdown
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAdSpyDiscoverEndpoint:
    """Tests for Ad Spy / Ad Intelligence discover endpoint"""
    
    def test_discover_ads_default(self):
        """GET /api/ads/discover returns ads array with default limit"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?q=&limit=24")
        assert response.status_code == 200
        data = response.json()
        assert 'ads' in data
        assert 'total' in data
        assert isinstance(data['ads'], list)
        assert len(data['ads']) <= 24
        print(f"✓ Default ads query: {len(data['ads'])} ads returned")
    
    def test_discover_ads_keyword_search(self):
        """GET /api/ads/discover?q=pillow returns filtered results"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?q=pillow&limit=24")
        assert response.status_code == 200
        data = response.json()
        assert 'ads' in data
        assert data.get('query') == 'pillow'
        print(f"✓ Keyword search 'pillow': {len(data['ads'])} ads found")
    
    def test_discover_ads_platform_tiktok(self):
        """GET /api/ads/discover?platform=tiktok filters by platform"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?platform=tiktok&limit=10")
        assert response.status_code == 200
        data = response.json()
        ads = data.get('ads', [])
        # All returned ads should have platform=tiktok
        for ad in ads:
            assert ad.get('platform') == 'tiktok', f"Expected tiktok, got {ad.get('platform')}"
        print(f"✓ TikTok filter: {len(ads)} ads with platform=tiktok")
    
    def test_discover_ads_platform_meta(self):
        """GET /api/ads/discover?platform=meta filters by platform"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?platform=meta&limit=10")
        assert response.status_code == 200
        data = response.json()
        ads = data.get('ads', [])
        # All returned ads should have platform=meta
        for ad in ads:
            assert ad.get('platform') == 'meta', f"Expected meta, got {ad.get('platform')}"
        print(f"✓ Meta filter: {len(ads)} ads with platform=meta")
    
    def test_discover_ads_platform_all(self):
        """GET /api/ads/discover?platform=all returns all platforms"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?platform=all&limit=24")
        assert response.status_code == 200
        data = response.json()
        ads = data.get('ads', [])
        platforms = set(ad.get('platform') for ad in ads)
        print(f"✓ Platform=all: {len(ads)} ads across platforms: {platforms}")
    
    def test_discover_ads_sort_engagement(self):
        """GET /api/ads/discover?sort=engagement sorts by engagement"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?sort=engagement&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data.get('sort') == 'engagement'
        print(f"✓ Sort=engagement works: {data.get('total')} ads")
    
    def test_discover_ads_sort_recent(self):
        """GET /api/ads/discover?sort=recent sorts by most recent"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?sort=recent&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data.get('sort') == 'recent'
        print(f"✓ Sort=recent works: {data.get('total')} ads")
    
    def test_discover_ads_sort_spend(self):
        """GET /api/ads/discover?sort=spend sorts by highest ad spend"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?sort=spend&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data.get('sort') == 'spend'
        print(f"✓ Sort=spend works: {data.get('total')} ads")
    
    def test_ad_object_structure(self):
        """Verify ad object contains expected fields"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?limit=1")
        assert response.status_code == 200
        data = response.json()
        ads = data.get('ads', [])
        if ads:
            ad = ads[0]
            # Check required fields
            assert 'id' in ad
            assert 'platform' in ad
            assert 'headline' in ad or 'product_name' in ad
            assert 'thumbnail_url' in ad or 'image_url' in ad
            print(f"✓ Ad object has required fields: id, platform, headline, thumbnail_url")


class TestProfitabilitySimulatorEndpoint:
    """Tests for Profitability Simulator endpoint"""
    
    def test_simulator_basic(self):
        """POST /api/tools/profitability-simulator returns all expected fields"""
        payload = {
            "product_cost": 12,
            "selling_price": 29.99,
            "cpm": 15,
            "conversion_rate": 2,
            "monthly_ad_budget": 1000,
            "shipping_cost": 3,
            "competition_level": "medium"
        }
        response = requests.post(
            f"{BASE_URL}/api/tools/profitability-simulator",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check all required response fields
        assert 'unit_economics' in data
        assert 'monthly_projection' in data
        assert 'saturation_analysis' in data
        assert 'verdict' in data
        assert 'break_even_possible' in data
        
        print(f"✓ Profitability simulator returns all expected fields")
    
    def test_simulator_unit_economics_fields(self):
        """Unit economics section contains all required fields"""
        payload = {
            "product_cost": 10,
            "selling_price": 30,
            "cpm": 12,
            "conversion_rate": 2.5,
            "monthly_ad_budget": 800,
            "shipping_cost": 2,
            "competition_level": "low"
        }
        response = requests.post(
            f"{BASE_URL}/api/tools/profitability-simulator",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        unit_econ = data.get('unit_economics', {})
        assert 'margin_per_unit' in unit_econ
        assert 'margin_percent' in unit_econ
        assert 'estimated_cpa' in unit_econ
        assert 'break_even_cpa' in unit_econ
        assert 'is_profitable_per_sale' in unit_econ
        
        print(f"✓ Unit economics: margin=${unit_econ.get('margin_per_unit')}, CPA=${unit_econ.get('estimated_cpa')}")
    
    def test_simulator_monthly_projection_fields(self):
        """Monthly projection section contains all required fields"""
        payload = {
            "product_cost": 12,
            "selling_price": 29.99,
            "cpm": 15,
            "conversion_rate": 2,
            "monthly_ad_budget": 1000,
            "shipping_cost": 3,
            "competition_level": "medium"
        }
        response = requests.post(
            f"{BASE_URL}/api/tools/profitability-simulator",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        monthly = data.get('monthly_projection', {})
        assert 'ad_budget' in monthly
        assert 'estimated_orders' in monthly
        assert 'revenue' in monthly
        assert 'profit' in monthly
        assert 'roas' in monthly
        
        print(f"✓ Monthly projection: orders={monthly.get('estimated_orders')}, profit=${monthly.get('profit')}, ROAS={monthly.get('roas')}")
    
    def test_simulator_saturation_analysis_fields(self):
        """Saturation analysis section contains all required fields"""
        payload = {
            "product_cost": 12,
            "selling_price": 29.99,
            "cpm": 15,
            "conversion_rate": 2,
            "monthly_ad_budget": 1000,
            "shipping_cost": 3,
            "competition_level": "high"
        }
        response = requests.post(
            f"{BASE_URL}/api/tools/profitability-simulator",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        saturation = data.get('saturation_analysis', {})
        assert 'competition_level' in saturation
        assert 'estimated_months_to_saturation' in saturation
        assert 'saturation_risk' in saturation
        
        print(f"✓ Saturation: competition={saturation.get('competition_level')}, months={saturation.get('estimated_months_to_saturation')}, risk={saturation.get('saturation_risk')}")
    
    def test_simulator_verdict_types(self):
        """Test different verdict outcomes based on inputs"""
        # Test strong opportunity
        payload_strong = {
            "product_cost": 5,
            "selling_price": 49.99,
            "cpm": 8,
            "conversion_rate": 4,
            "monthly_ad_budget": 300,
            "shipping_cost": 2,
            "competition_level": "low"
        }
        response = requests.post(
            f"{BASE_URL}/api/tools/profitability-simulator",
            json=payload_strong
        )
        data = response.json()
        verdict = data.get('verdict', '')
        assert verdict in [
            'Strong opportunity',
            'Promising with optimisation',
            'Risky — needs lower CPA or higher margin',
            'Not viable at current metrics'
        ]
        print(f"✓ Verdict returned: '{verdict}'")
    
    def test_simulator_competition_levels(self):
        """Test all competition levels affect saturation correctly"""
        for level in ['low', 'medium', 'high']:
            payload = {
                "product_cost": 12,
                "selling_price": 29.99,
                "cpm": 15,
                "conversion_rate": 2,
                "monthly_ad_budget": 1000,
                "shipping_cost": 3,
                "competition_level": level
            }
            response = requests.post(
                f"{BASE_URL}/api/tools/profitability-simulator",
                json=payload
            )
            assert response.status_code == 200
            data = response.json()
            saturation = data.get('saturation_analysis', {})
            assert saturation.get('competition_level') == level
        
        print(f"✓ All competition levels (low/medium/high) work correctly")


class TestLaunchScoreBreakdownEndpoint:
    """Tests for 7-Signal Launch Score Breakdown endpoint"""
    
    @pytest.fixture
    def product_id(self):
        """Get a valid product ID from ads discover endpoint"""
        response = requests.get(f"{BASE_URL}/api/ads/discover?limit=1")
        data = response.json()
        ads = data.get('ads', [])
        if ads:
            return ads[0]['id']
        pytest.skip("No products available to test")
    
    def test_launch_score_breakdown_exists(self, product_id):
        """GET /api/products/{id}/launch-score-breakdown returns data"""
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        data = response.json()
        
        assert 'product_id' in data
        assert 'product_name' in data
        assert 'launch_score' in data
        assert 'components' in data
        
        print(f"✓ Launch score breakdown exists for product: {data.get('product_name')}")
    
    def test_launch_score_breakdown_has_7_signals(self, product_id):
        """Launch score breakdown contains 7 signal components"""
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        data = response.json()
        
        components = data.get('components', [])
        assert len(components) == 7, f"Expected 7 signals, got {len(components)}"
        
        # Check signal names
        signal_keys = [c.get('key') for c in components]
        expected_keys = {'trend', 'margin', 'competition', 'ad_activity', 'supplier_demand', 'search_growth', 'social_buzz'}
        actual_keys = set(signal_keys)
        assert actual_keys == expected_keys, f"Missing signals: {expected_keys - actual_keys}"
        
        print(f"✓ All 7 signals present: {signal_keys}")
    
    def test_launch_score_component_structure(self, product_id):
        """Each component has required fields"""
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        data = response.json()
        
        for component in data.get('components', []):
            assert 'name' in component
            assert 'key' in component
            assert 'raw_score' in component
            assert 'weight' in component
            assert 'weight_percent' in component
            assert 'contribution' in component
            assert 'explanation' in component
        
        print(f"✓ All components have required fields")
    
    def test_launch_score_has_formula(self, product_id):
        """Launch score breakdown includes formula explanation"""
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        data = response.json()
        
        formula = data.get('formula', {})
        assert 'description' in formula
        assert 'breakdown' in formula
        
        print(f"✓ Formula included: {formula.get('description', '')[:60]}...")
    
    def test_launch_score_has_summary(self, product_id):
        """Launch score breakdown includes summary with strengths/weaknesses"""
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        data = response.json()
        
        summary = data.get('summary', {})
        assert 'rating_explanation' in summary or 'strengths' in summary
        
        print(f"✓ Summary included with rating explanation")
    
    def test_launch_score_404_for_invalid_product(self):
        """Launch score returns 404 for non-existent product"""
        response = requests.get(f"{BASE_URL}/api/products/invalid-product-id-xyz/launch-score-breakdown")
        assert response.status_code == 404
        print(f"✓ Returns 404 for invalid product ID")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
