"""
Test Launch Score Breakdown API - Backend API Tests
Tests for the GET /api/products/{id}/launch-score-breakdown endpoint
Features tested:
- Returns correct structure with 5 components (trend, margin, competition, ad_activity, supplier_demand)
- Each component has raw_score, weight, weight_percent, contribution, level, impact, explanation
- Returns formula breakdown with description and calculation
- Returns summary with rating_explanation, strengths, weaknesses, improvements
- Component weights sum to 100% (30+25+20+15+10)
- Contributions sum to launch_score
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestLaunchScoreBreakdownEndpoint:
    """Test the /api/products/{product_id}/launch-score-breakdown endpoint"""

    def get_product_id(self):
        """Helper to get a valid product ID for testing"""
        response = requests.get(f"{BASE_URL}/api/products?limit=10")
        if response.status_code != 200:
            pytest.skip("Cannot fetch products")
        products = response.json().get("data", [])
        if not products:
            pytest.skip("No products available")
        # Prefer product with launch_score > 0
        for p in products:
            if p.get("launch_score", 0) > 0:
                return p["id"]
        return products[0]["id"]

    def test_breakdown_endpoint_returns_200(self):
        """GET /api/products/{id}/launch-score-breakdown returns 200"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"PASS: Breakdown endpoint returns 200 for product {product_id}")

    def test_breakdown_returns_correct_structure(self):
        """Breakdown response has all required top-level fields"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check top-level fields
        required_fields = ["product_id", "product_name", "launch_score", "launch_label", "components", "formula", "summary"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        assert data["product_id"] == product_id, "product_id mismatch"
        assert isinstance(data["launch_score"], int), "launch_score should be int"
        assert data["launch_label"] in ["strong_launch", "promising", "risky", "avoid"], f"Invalid launch_label: {data['launch_label']}"
        
        print(f"PASS: Breakdown has all required top-level fields")

    def test_breakdown_has_five_components(self):
        """Breakdown contains exactly 5 components (trend, margin, competition, ad_activity, supplier_demand)"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        components = data.get("components", [])
        
        assert len(components) == 5, f"Expected 5 components, got {len(components)}"
        
        # Check all expected component keys are present
        expected_keys = {"trend", "margin", "competition", "ad_activity", "supplier_demand"}
        actual_keys = {c["key"] for c in components}
        assert expected_keys == actual_keys, f"Missing component keys. Expected: {expected_keys}, Got: {actual_keys}"
        
        print(f"PASS: Breakdown has all 5 required components: {actual_keys}")

    def test_component_has_all_required_fields(self):
        """Each component has raw_score, weight, weight_percent, contribution, level, impact, explanation"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        components = data.get("components", [])
        
        required_component_fields = ["name", "key", "raw_score", "weight", "weight_percent", "contribution", "level", "impact", "explanation"]
        
        for component in components:
            for field in required_component_fields:
                assert field in component, f"Component {component.get('key', 'unknown')} missing field: {field}"
            
            # Validate field types
            assert isinstance(component["raw_score"], int), f"raw_score should be int, got {type(component['raw_score'])}"
            assert isinstance(component["weight"], float), f"weight should be float, got {type(component['weight'])}"
            assert component["weight_percent"].endswith("%"), f"weight_percent should end with %, got {component['weight_percent']}"
            assert isinstance(component["contribution"], (int, float)), f"contribution should be numeric"
            assert component["level"] in ["high", "medium", "low"], f"Invalid level: {component['level']}"
            assert component["impact"] in ["positive", "neutral", "negative"], f"Invalid impact: {component['impact']}"
            assert len(component["explanation"]) > 10, f"Explanation too short for {component['key']}"
        
        print(f"PASS: All components have required fields with valid types")

    def test_component_weights_sum_to_100(self):
        """Component weights sum to 100% (30+25+20+15+10)"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        components = data.get("components", [])
        
        # Check weight sum
        total_weight = sum(c["weight"] for c in components)
        assert abs(total_weight - 1.0) < 0.001, f"Weights should sum to 1.0 (100%), got {total_weight}"
        
        # Verify specific weights
        weight_map = {c["key"]: c["weight"] for c in components}
        expected_weights = {
            "trend": 0.30,
            "margin": 0.25,
            "competition": 0.20,
            "ad_activity": 0.15,
            "supplier_demand": 0.10
        }
        
        for key, expected in expected_weights.items():
            actual = weight_map.get(key, 0)
            assert abs(actual - expected) < 0.001, f"Weight for {key} should be {expected}, got {actual}"
        
        print(f"PASS: Weights sum to 100% with correct distribution: {weight_map}")

    def test_contributions_sum_to_launch_score(self):
        """Contributions approximately sum to launch_score"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        components = data.get("components", [])
        launch_score = data.get("launch_score", 0)
        
        # Sum contributions
        contribution_sum = sum(c["contribution"] for c in components)
        
        # Allow for rounding differences (within 2 points)
        diff = abs(contribution_sum - launch_score)
        assert diff <= 2, f"Contributions sum ({contribution_sum}) should equal launch_score ({launch_score}), diff={diff}"
        
        print(f"PASS: Contributions sum ({contribution_sum}) ≈ launch_score ({launch_score})")

    def test_formula_breakdown_present(self):
        """Formula breakdown with description and calculation is present"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        formula = data.get("formula", {})
        
        assert "description" in formula, "Missing formula description"
        assert "breakdown" in formula, "Missing formula breakdown"
        
        # Check description contains the formula explanation
        desc = formula["description"]
        assert "Trend" in desc and "Margin" in desc and "30%" in desc, f"Description should explain formula: {desc}"
        
        # Check breakdown shows the calculation
        breakdown = formula["breakdown"]
        assert "=" in breakdown, f"Breakdown should show calculation: {breakdown}"
        assert "+" in breakdown, f"Breakdown should show additions: {breakdown}"
        
        print(f"PASS: Formula description: {desc}")
        print(f"PASS: Formula breakdown: {breakdown}")

    def test_summary_has_required_sections(self):
        """Summary contains rating_explanation, strengths, weaknesses, improvements"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        summary = data.get("summary", {})
        
        required_summary_fields = ["rating_explanation", "strengths", "weaknesses", "improvements"]
        for field in required_summary_fields:
            assert field in summary, f"Summary missing field: {field}"
        
        # rating_explanation should be a meaningful string
        assert len(summary["rating_explanation"]) > 20, "rating_explanation too short"
        assert isinstance(summary["strengths"], list), "strengths should be a list"
        assert isinstance(summary["weaknesses"], list), "weaknesses should be a list"
        assert isinstance(summary["improvements"], list), "improvements should be a list"
        
        print(f"PASS: Summary has all required sections")
        print(f"  - Rating: {summary['rating_explanation'][:100]}...")
        print(f"  - Strengths: {len(summary['strengths'])} items")
        print(f"  - Weaknesses: {len(summary['weaknesses'])} items")
        print(f"  - Improvements: {len(summary['improvements'])} items")

    def test_strengths_structure(self):
        """Strengths list items have name, score, explanation"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        strengths = data.get("summary", {}).get("strengths", [])
        
        if not strengths:
            print("INFO: No strengths found - may be a low-scoring product")
            return
        
        for strength in strengths:
            assert "name" in strength, "Strength missing 'name'"
            assert "score" in strength, "Strength missing 'score'"
            assert "explanation" in strength, "Strength missing 'explanation'"
            assert strength["score"] >= 70, f"Strength score should be >= 70, got {strength['score']}"
        
        print(f"PASS: {len(strengths)} strengths with valid structure")

    def test_weaknesses_structure(self):
        """Weaknesses list items have name, score, explanation"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        weaknesses = data.get("summary", {}).get("weaknesses", [])
        
        if not weaknesses:
            print("INFO: No weaknesses found - may be a high-scoring product")
            return
        
        for weakness in weaknesses:
            assert "name" in weakness, "Weakness missing 'name'"
            assert "score" in weakness, "Weakness missing 'score'"
            assert "explanation" in weakness, "Weakness missing 'explanation'"
            assert weakness["score"] < 50, f"Weakness score should be < 50, got {weakness['score']}"
        
        print(f"PASS: {len(weaknesses)} weaknesses with valid structure")

    def test_improvements_structure(self):
        """Improvements list items have component, current_score, suggestion"""
        product_id = self.get_product_id()
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        improvements = data.get("summary", {}).get("improvements", [])
        
        if not improvements:
            print("INFO: No improvements found - may be a high-scoring product")
            return
        
        for improvement in improvements:
            assert "component" in improvement, "Improvement missing 'component'"
            assert "current_score" in improvement, "Improvement missing 'current_score'"
            assert "suggestion" in improvement, "Improvement missing 'suggestion'"
            assert len(improvement["suggestion"]) > 10, "Suggestion too short"
        
        print(f"PASS: {len(improvements)} improvements with valid structure")

    def test_404_for_nonexistent_product(self):
        """Returns 404 for non-existent product"""
        response = requests.get(f"{BASE_URL}/api/products/nonexistent-id-12345/launch-score-breakdown")
        assert response.status_code == 404, f"Expected 404 for non-existent product, got {response.status_code}"
        print("PASS: Returns 404 for non-existent product")


class TestLaunchScoreBreakdownLogic:
    """Test the breakdown calculation logic"""

    def get_product_with_score(self, min_score=50):
        """Helper to get a product with minimum score for testing"""
        response = requests.get(f"{BASE_URL}/api/products?limit=50&sort_by=launch_score&sort_order=desc")
        if response.status_code != 200:
            pytest.skip("Cannot fetch products")
        products = response.json().get("data", [])
        for p in products:
            if p.get("launch_score", 0) >= min_score:
                return p["id"]
        pytest.skip(f"No products with score >= {min_score}")

    def test_component_level_correct(self):
        """Component level (high/medium/low) matches score thresholds"""
        product_id = self.get_product_with_score(0)
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        components = data.get("components", [])
        
        for c in components:
            score = c["raw_score"]
            level = c["level"]
            
            expected_level = "high" if score >= 70 else ("medium" if score >= 40 else "low")
            assert level == expected_level, f"Component {c['key']} with score {score} should be {expected_level}, got {level}"
        
        print(f"PASS: Component levels correctly match score thresholds")

    def test_component_impact_correct(self):
        """Component impact (positive/neutral/negative) matches score thresholds"""
        product_id = self.get_product_with_score(0)
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        components = data.get("components", [])
        
        for c in components:
            score = c["raw_score"]
            impact = c["impact"]
            
            expected_impact = "positive" if score >= 60 else ("neutral" if score >= 40 else "negative")
            assert impact == expected_impact, f"Component {c['key']} with score {score} should be {expected_impact} impact, got {impact}"
        
        print(f"PASS: Component impacts correctly match score thresholds")

    def test_components_sorted_by_contribution(self):
        """Components are sorted by contribution (highest first)"""
        product_id = self.get_product_with_score(0)
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        components = data.get("components", [])
        
        contributions = [c["contribution"] for c in components]
        sorted_contributions = sorted(contributions, reverse=True)
        
        assert contributions == sorted_contributions, f"Components not sorted by contribution: {contributions}"
        print(f"PASS: Components sorted by contribution: {contributions}")

    def test_strong_launch_product_has_strengths(self):
        """Product with score >= 80 should have strengths identified"""
        product_id = self.get_product_with_score(80)
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        strengths = data.get("summary", {}).get("strengths", [])
        
        assert len(strengths) >= 1, f"Strong launch product should have at least 1 strength, got {len(strengths)}"
        print(f"PASS: Strong launch product has {len(strengths)} strengths")

    def test_rating_explanation_matches_label(self):
        """Rating explanation text matches the launch_label"""
        product_id = self.get_product_with_score(0)
        response = requests.get(f"{BASE_URL}/api/products/{product_id}/launch-score-breakdown")
        assert response.status_code == 200
        
        data = response.json()
        label = data.get("launch_label")
        explanation = data.get("summary", {}).get("rating_explanation", "")
        
        # Check explanation mentions the score
        score = data.get("launch_score")
        assert str(score) in explanation, f"Explanation should mention score {score}"
        
        # Check label-specific language
        if label == "strong_launch":
            assert "excellent" in explanation.lower() or "well-positioned" in explanation.lower(), \
                f"strong_launch explanation should be positive: {explanation}"
        elif label == "avoid":
            assert "risk" in explanation.lower() or "alternative" in explanation.lower(), \
                f"avoid explanation should warn: {explanation}"
        
        print(f"PASS: Rating explanation matches label '{label}'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
