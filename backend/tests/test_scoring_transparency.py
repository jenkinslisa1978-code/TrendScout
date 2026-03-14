"""
Test Suite for Scoring Transparency Features (Iteration 69)
Tests: /api/scoring/methodology endpoint and related transparency features
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ecommerce-guide-11.preview.emergentagent.com').rstrip('/')


class TestScoringMethodologyEndpoint:
    """Tests for /api/scoring/methodology endpoint - PUBLIC, no auth required"""

    def test_scoring_methodology_returns_200(self):
        """Verify endpoint is accessible and returns 200"""
        response = requests.get(f"{BASE_URL}/api/scoring/methodology")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: /api/scoring/methodology returns 200")

    def test_scoring_methodology_returns_7_signals(self):
        """Verify endpoint returns exactly 7 scoring signals"""
        response = requests.get(f"{BASE_URL}/api/scoring/methodology")
        data = response.json()
        assert 'signals' in data, "Response should have 'signals' key"
        assert len(data['signals']) == 7, f"Expected 7 signals, got {len(data['signals'])}"
        
        expected_signals = [
            'Trend Score', 'Margin Score', 'Competition Score', 
            'Ad Activity Score', 'Supplier Demand Score', 
            'Search Growth Score', 'Order Velocity Score'
        ]
        actual_signals = [s['name'] for s in data['signals']]
        for sig in expected_signals:
            assert sig in actual_signals, f"Missing signal: {sig}"
        print(f"PASS: Returns 7 signals: {actual_signals}")

    def test_scoring_methodology_returns_6_data_sources(self):
        """Verify endpoint returns exactly 6 data sources"""
        response = requests.get(f"{BASE_URL}/api/scoring/methodology")
        data = response.json()
        assert 'data_sources' in data, "Response should have 'data_sources' key"
        assert len(data['data_sources']) == 6, f"Expected 6 data sources, got {len(data['data_sources'])}"
        
        expected_sources = ['Amazon', 'Google Trends', 'TikTok', 'AliExpress', 'CJ Dropshipping', 'Meta Ad Library']
        actual_sources = [s['name'] for s in data['data_sources']]
        for src in expected_sources:
            assert src in actual_sources, f"Missing data source: {src}"
        print(f"PASS: Returns 6 data sources: {actual_sources}")

    def test_scoring_methodology_has_formula(self):
        """Verify endpoint returns formula string"""
        response = requests.get(f"{BASE_URL}/api/scoring/methodology")
        data = response.json()
        assert 'formula' in data, "Response should have 'formula' key"
        assert 'Launch Score' in data['formula'], "Formula should mention Launch Score"
        assert 'Trend' in data['formula'], "Formula should mention Trend"
        print(f"PASS: Has formula: {data['formula'][:60]}...")

    def test_scoring_methodology_has_honest_limitations(self):
        """Verify endpoint returns honest_limitations array"""
        response = requests.get(f"{BASE_URL}/api/scoring/methodology")
        data = response.json()
        assert 'honest_limitations' in data, "Response should have 'honest_limitations' key"
        assert isinstance(data['honest_limitations'], list), "honest_limitations should be a list"
        assert len(data['honest_limitations']) >= 3, f"Expected at least 3 limitations, got {len(data['honest_limitations'])}"
        print(f"PASS: Has {len(data['honest_limitations'])} honest limitations")

    def test_scoring_methodology_signals_have_high_low_explanations(self):
        """Verify each signal has what_high_means and what_low_means"""
        response = requests.get(f"{BASE_URL}/api/scoring/methodology")
        data = response.json()
        
        for signal in data['signals']:
            assert 'what_high_means' in signal, f"Signal '{signal['name']}' missing what_high_means"
            assert 'what_low_means' in signal, f"Signal '{signal['name']}' missing what_low_means"
            assert len(signal['what_high_means']) > 10, f"Signal '{signal['name']}' has short what_high_means"
            assert len(signal['what_low_means']) > 10, f"Signal '{signal['name']}' has short what_low_means"
        print("PASS: All 7 signals have what_high_means and what_low_means explanations")

    def test_scoring_methodology_signals_have_weight_and_description(self):
        """Verify each signal has weight and description"""
        response = requests.get(f"{BASE_URL}/api/scoring/methodology")
        data = response.json()
        
        for signal in data['signals']:
            assert 'weight' in signal, f"Signal '{signal['name']}' missing weight"
            assert 'description' in signal, f"Signal '{signal['name']}' missing description"
            assert '%' in signal['weight'], f"Signal '{signal['name']}' weight should have %"
        print("PASS: All signals have weight and description")

    def test_scoring_methodology_data_sources_have_update_frequency(self):
        """Verify each data source has update frequency"""
        response = requests.get(f"{BASE_URL}/api/scoring/methodology")
        data = response.json()
        
        for source in data['data_sources']:
            assert 'update_frequency' in source, f"Source '{source['name']}' missing update_frequency"
            assert 'type' in source, f"Source '{source['name']}' missing type"
            assert 'method' in source, f"Source '{source['name']}' missing method"
        print("PASS: All data sources have update_frequency, type, method")


class TestPlatformConnectionsAutomationBadges:
    """Tests for Platform Connections automation level badges"""

    def test_connections_platforms_endpoint(self):
        """Verify /api/connections/platforms returns store and ad platforms"""
        response = requests.get(f"{BASE_URL}/api/connections/platforms")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert 'stores' in data, "Response should have 'stores' key"
        assert 'ads' in data, "Response should have 'ads' key"
        
        # Check store platforms
        store_keys = list(data['stores'].keys())
        assert 'shopify' in store_keys, "Missing shopify in store platforms"
        assert 'etsy' in store_keys, "Missing etsy in store platforms"
        
        # Check ad platforms  
        ad_keys = list(data['ads'].keys())
        assert 'google' in ad_keys, "Missing google in ad platforms"
        
        print(f"PASS: Store platforms: {store_keys}, Ad platforms: {ad_keys}")


class TestProductsEndpointForScoringMethodology:
    """Verify products work with scoring methodology data"""

    def test_products_endpoint_returns_data(self):
        """Verify products endpoint returns products"""
        response = requests.get(f"{BASE_URL}/api/products?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'data' in data, "Response should have 'data' key"
        assert len(data['data']) > 0, "Should return at least one product"
        print(f"PASS: Products endpoint returns {len(data['data'])} products")

    def test_products_have_scoring_data(self):
        """Verify products have the scoring fields used by methodology"""
        response = requests.get(f"{BASE_URL}/api/products?limit=1")
        data = response.json()
        product = data['data'][0]
        
        # Check for scoring-related fields
        assert 'trend_score' in product, "Product missing trend_score"
        assert 'estimated_margin' in product, "Product missing estimated_margin"
        assert 'competition_level' in product, "Product missing competition_level"
        
        print(f"PASS: Product has scoring fields - trend_score: {product.get('trend_score')}, margin: {product.get('estimated_margin')}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
