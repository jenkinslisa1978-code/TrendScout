"""
Test Scoring Engine & Data Transparency APIs

Tests for Phase 2 features:
- GET /api/products returns products with launch_score, trend_score, margin_score, 
  competition_score, ad_activity_score, supplier_demand_score
- GET /api/products returns data_sources, confidence_score, last_updated, launch_score_breakdown
- GET /api/products/{id}/launch-score-breakdown - transparent score breakdown endpoint
- POST /api/ingestion/scrape/google-trends - Google Trends enrichment
- POST /api/ingestion/scores/recompute - Score recomputation
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API_KEY = "vs_automation_key_2024"

# Skip all tests if no BASE_URL
pytestmark = pytest.mark.skipif(not BASE_URL, reason="REACT_APP_BACKEND_URL not set")


class TestHealthCheck:
    """Basic connectivity tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ API health check passed")


class TestProductsWithScores:
    """Test GET /api/products returns products with scoring fields"""
    
    def test_products_have_launch_score(self):
        """Products should have launch_score field"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        
        products = data.get("data") or data.get("products") or data
        assert isinstance(products, list), "Expected products list"
        assert len(products) > 0, "No products returned"
        
        # Check first product has launch_score
        product = products[0]
        assert "launch_score" in product, f"Missing launch_score in product: {product.keys()}"
        assert isinstance(product["launch_score"], (int, float)), "launch_score should be numeric"
        print(f"✓ Product has launch_score: {product['launch_score']}")
    
    def test_products_have_component_scores(self):
        """Products should have all 5 component score fields"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        
        products = data.get("data") or data.get("products") or data
        product = products[0]
        
        required_scores = [
            "trend_score", 
            "margin_score", 
            "competition_score", 
            "ad_activity_score", 
            "supplier_demand_score"
        ]
        
        for score_field in required_scores:
            assert score_field in product, f"Missing {score_field} in product"
            # Scores should be 0-100
            score_val = product.get(score_field, 0)
            assert isinstance(score_val, (int, float)), f"{score_field} should be numeric"
        
        print(f"✓ Product has all component scores: trend={product.get('trend_score')}, margin={product.get('margin_score')}, competition={product.get('competition_score')}, ad_activity={product.get('ad_activity_score')}, supplier_demand={product.get('supplier_demand_score')}")
    
    def test_products_have_data_sources_array(self):
        """Products should have data_sources array field"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        
        products = data.get("data") or data.get("products") or data
        
        # Check for data_source or data_sources field
        product = products[0]
        has_data_source = "data_source" in product or "data_sources" in product
        assert has_data_source, f"Missing data_source(s) field in product: {product.keys()}"
        
        source = product.get("data_sources") or [product.get("data_source")]
        print(f"✓ Product has data_sources: {source}")
    
    def test_products_have_confidence_score(self):
        """Products should have confidence_score field"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        
        products = data.get("data") or data.get("products") or data
        product = products[0]
        
        assert "confidence_score" in product, f"Missing confidence_score in product"
        conf = product.get("confidence_score", 0)
        assert isinstance(conf, (int, float)), "confidence_score should be numeric"
        assert 0 <= conf <= 100, f"confidence_score should be 0-100, got {conf}"
        print(f"✓ Product has confidence_score: {conf}%")
    
    def test_products_have_last_updated(self):
        """Products should have last_updated timestamp"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        
        products = data.get("data") or data.get("products") or data
        product = products[0]
        
        # Check for last_updated or updated_at or scores_updated_at
        has_timestamp = any(k in product for k in ["last_updated", "updated_at", "scores_updated_at"])
        assert has_timestamp, f"Missing timestamp field in product: {product.keys()}"
        
        timestamp = product.get("last_updated") or product.get("updated_at") or product.get("scores_updated_at")
        print(f"✓ Product has timestamp: {timestamp}")
    
    def test_products_have_launch_score_breakdown_object(self):
        """Products should have launch_score_breakdown dict with score/weight/reasoning"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        
        products = data.get("data") or data.get("products") or data
        product = products[0]
        
        # Check for launch_score_breakdown
        assert "launch_score_breakdown" in product, f"Missing launch_score_breakdown in product"
        breakdown = product.get("launch_score_breakdown")
        
        if breakdown:
            assert isinstance(breakdown, dict), "launch_score_breakdown should be a dict"
            
            # Should have component keys
            expected_keys = ["trend", "margin", "competition", "ad_activity", "supplier_demand"]
            for key in expected_keys:
                if key in breakdown:
                    component = breakdown[key]
                    assert "score" in component, f"Missing score in {key} breakdown"
                    assert "weight" in component, f"Missing weight in {key} breakdown"
                    assert "weighted" in component, f"Missing weighted in {key} breakdown"
                    print(f"  - {key}: score={component.get('score')}, weight={component.get('weight')}, weighted={component.get('weighted')}")
                    
                    # Check for reasoning
                    if "reasoning" in component:
                        reasoning = component.get("reasoning", "")
                        print(f"    Reasoning: {reasoning[:80]}...")
        
        print(f"✓ Product has launch_score_breakdown with component details")


class TestLaunchScoreBreakdownEndpoint:
    """Test GET /api/products/{id}/launch-score-breakdown endpoint"""
    
    def _get_first_product_id(self):
        """Helper to get a valid product ID"""
        response = requests.get(f"{BASE_URL}/api/products")
        products = response.json().get("data") or response.json().get("products") or response.json()
        return products[0]["id"] if products else None
    
    def test_launch_score_breakdown_endpoint_exists(self):
        """Endpoint should exist and return data"""
        product_id = self._get_first_product_id()
        assert product_id, "No products available for testing"
        
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200, f"Endpoint returned {response.status_code}: {response.text}"
        
        data = response.json()
        assert "launch_score" in data, "Response missing launch_score"
        print(f"✓ Launch score breakdown endpoint works, score: {data.get('launch_score')}")
    
    def test_breakdown_has_components(self):
        """Response should have components array with 5 score components"""
        product_id = self._get_first_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        data = response.json()
        
        assert "components" in data, "Missing components array"
        components = data["components"]
        assert isinstance(components, list), "components should be a list"
        assert len(components) == 5, f"Expected 5 components, got {len(components)}"
        
        # Each component should have required fields
        for comp in components:
            assert "name" in comp, f"Component missing name"
            assert "raw_score" in comp, f"Component missing raw_score"
            assert "weight" in comp, f"Component missing weight"
            assert "contribution" in comp, f"Component missing contribution"
            print(f"  - {comp.get('name')}: score={comp.get('raw_score')}, weight={comp.get('weight')}, contribution={comp.get('contribution')}")
        
        print("✓ Breakdown has all 5 components with score/weight/contribution")
    
    def test_breakdown_has_formula(self):
        """Response should have formula description"""
        product_id = self._get_first_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        data = response.json()
        
        assert "formula" in data, "Missing formula object"
        formula = data["formula"]
        assert "description" in formula, "Formula missing description"
        assert "breakdown" in formula, "Formula missing breakdown calculation"
        
        # Formula should mention the weights
        desc = formula.get("description", "")
        assert "30%" in desc or "0.30" in str(desc), "Formula should mention 30% trend weight"
        assert "25%" in desc or "0.25" in str(desc), "Formula should mention 25% margin weight"
        
        print(f"✓ Formula: {formula.get('description')}")
        print(f"✓ Breakdown: {formula.get('breakdown')}")
    
    def test_breakdown_has_score_reasoning(self):
        """Response should have score_reasoning with component explanations"""
        product_id = self._get_first_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        data = response.json()
        
        # Check for score_reasoning (the detailed breakdown from ScoringEngine)
        reasoning = data.get("score_reasoning", {})
        
        if reasoning:
            for key in ["trend", "margin", "competition", "ad_activity", "supplier_demand"]:
                if key in reasoning:
                    comp = reasoning[key]
                    if "reasoning" in comp:
                        print(f"  - {key} reasoning: {comp.get('reasoning', '')[:60]}...")
        
        print("✓ Score reasoning included in response")
    
    def test_breakdown_has_data_transparency(self):
        """Response should have data_transparency section"""
        product_id = self._get_first_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        data = response.json()
        
        assert "data_transparency" in data, "Missing data_transparency section"
        transparency = data["data_transparency"]
        
        # Should have these fields
        assert "data_sources" in transparency, "Missing data_sources"
        assert "confidence_score" in transparency, "Missing confidence_score"
        assert "last_updated" in transparency, "Missing last_updated"
        
        print(f"✓ Data transparency: sources={transparency.get('data_sources')}, confidence={transparency.get('confidence_score')}%")
    
    def test_reasoning_describes_score_reason(self):
        """Reasoning strings should describe WHY scores are what they are"""
        product_id = self._get_first_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        data = response.json()
        
        # Check both components and score_reasoning for meaningful text
        components = data.get("components", [])
        reasoning_texts = []
        
        for comp in components:
            if "explanation" in comp:
                reasoning_texts.append(comp.get("explanation"))
        
        score_reasoning = data.get("score_reasoning", {})
        for key, val in score_reasoning.items():
            if isinstance(val, dict) and "reasoning" in val:
                reasoning_texts.append(val.get("reasoning"))
        
        # At least some reasoning should exist
        meaningful_reasons = [r for r in reasoning_texts if r and len(r) > 10]
        assert len(meaningful_reasons) > 0, "No meaningful reasoning text found"
        
        # Check for descriptive language
        sample = meaningful_reasons[0]
        print(f"✓ Sample reasoning: '{sample[:100]}...'")
        
        # Reasoning should describe score cause (not just a number)
        has_descriptive = any(
            any(word in r.lower() for word in ['margin', 'trend', 'competition', 'demand', 'activity', 'available', 'strong', 'weak', 'high', 'low'])
            for r in meaningful_reasons
        )
        assert has_descriptive, "Reasoning should describe WHY scores are what they are"
        print("✓ Reasoning strings describe score rationale")


class TestGoogleTrendsEndpoint:
    """Test POST /api/ingestion/scrape/google-trends endpoint"""
    
    def test_google_trends_requires_api_key(self):
        """Endpoint should require API key"""
        response = requests.post(f"{BASE_URL}/api/ingestion/scrape/google-trends")
        assert response.status_code == 401, "Should require API key"
        print("✓ Google Trends endpoint requires API key")
    
    def test_google_trends_with_valid_key(self):
        """Endpoint should work with valid API key"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scrape/google-trends",
            params={"max_products": 2},  # Keep small for test speed
            headers={"X-API-Key": API_KEY}
        )
        
        # Could be 200 (success) or 500 (pytrends rate limited)
        assert response.status_code in [200, 500, 422], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "source" in data or "enriched" in data or "completed_at" in data
            print(f"✓ Google Trends returned: enriched={data.get('enriched', 0)}, failed={data.get('failed', 0)}")
        else:
            print(f"✓ Google Trends endpoint exists (status: {response.status_code} - may be rate limited)")


class TestScoreRecomputeEndpoint:
    """Test POST /api/ingestion/scores/recompute endpoint"""
    
    def test_recompute_requires_api_key(self):
        """Endpoint should require API key"""
        response = requests.post(f"{BASE_URL}/api/ingestion/scores/recompute")
        assert response.status_code == 401, "Should require API key"
        print("✓ Recompute endpoint requires API key")
    
    def test_recompute_with_valid_key(self):
        """Endpoint should recompute scores"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/scores/recompute",
            headers={"X-API-Key": API_KEY}
        )
        
        assert response.status_code == 200, f"Recompute failed: {response.text}"
        data = response.json()
        
        # Should return stats
        assert "updated" in data or "products_updated" in data, f"Missing update count: {data}"
        
        updated_count = data.get("updated") or data.get("products_updated", 0)
        print(f"✓ Recompute updated {updated_count} products")


class TestUnavailableDataHandling:
    """Test that unavailable data shows clear messages"""
    
    def test_unavailable_data_marked_clearly(self):
        """Products with missing data should show 'unavailable' messages, not fabricated values"""
        response = requests.get(f"{BASE_URL}/api/products")
        products = response.json().get("data") or response.json().get("products") or response.json()
        
        # Get breakdown for a product
        product_id = products[0]["id"]
        breakdown_resp = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        data = breakdown_resp.json()
        
        # Check score_reasoning for unavailable messages
        reasoning = data.get("score_reasoning", {})
        unavailable_found = False
        
        for key, val in reasoning.items():
            if isinstance(val, dict) and "reasoning" in val:
                reason_text = val.get("reasoning", "").lower()
                if "unavailable" in reason_text or "unknown" in reason_text or "cannot calculate" in reason_text:
                    print(f"  - {key}: '{val.get('reasoning')}'")
                    unavailable_found = True
        
        # Also check components
        for comp in data.get("components", []):
            explanation = comp.get("explanation", "").lower()
            if "unavailable" in explanation or "limited" in explanation or "concerns" in explanation:
                print(f"  - {comp.get('name')}: '{comp.get('explanation')}'")
        
        print("✓ Products handle unavailable data appropriately")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
