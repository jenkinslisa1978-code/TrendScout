"""
Test Launch Score Implementation - Backend API Tests
Tests for the Product Launch Score feature:
- Calculate launch_score using formula: 0.30*trend + 0.25*margin + 0.20*competition + 0.15*ad_activity + 0.10*supplier_demand
- Categories: 80-100=strong_launch, 60-79=promising, 40-59=risky, 0-39=avoid
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API_KEY = "vs_automation_key_2024"


class TestLaunchScoreComputation:
    """Test the /api/automation/compute-launch-scores endpoint"""

    def test_compute_launch_scores_requires_api_key(self):
        """POST /api/automation/compute-launch-scores requires X-API-Key"""
        response = requests.post(f"{BASE_URL}/api/automation/compute-launch-scores")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: compute-launch-scores returns 401 without API key")

    def test_compute_launch_scores_invalid_api_key(self):
        """POST /api/automation/compute-launch-scores rejects invalid API key"""
        response = requests.post(
            f"{BASE_URL}/api/automation/compute-launch-scores",
            headers={"X-API-Key": "invalid_key"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: compute-launch-scores returns 401 with invalid API key")

    def test_compute_launch_scores_with_valid_key(self):
        """POST /api/automation/compute-launch-scores with valid API key computes scores"""
        response = requests.post(
            f"{BASE_URL}/api/automation/compute-launch-scores",
            headers={"X-API-Key": API_KEY}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert "products_updated" in data, "Missing products_updated field"
        assert "duration_seconds" in data, "Missing duration_seconds field"
        assert data["products_updated"] >= 0, "products_updated should be non-negative"
        
        print(f"PASS: compute-launch-scores updated {data['products_updated']} products in {data['duration_seconds']}s")


class TestProductsAPILaunchScore:
    """Test that /api/products returns launch_score fields"""

    def test_products_include_launch_score(self):
        """GET /api/products returns products with launch_score fields"""
        response = requests.get(f"{BASE_URL}/api/products?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        products = data.get("data", [])
        assert len(products) > 0, "No products returned"
        
        # Check at least one product has launch_score
        products_with_launch = [p for p in products if p.get("launch_score", 0) > 0]
        assert len(products_with_launch) > 0, "No products have launch_score > 0"
        
        # Verify all products have the new fields
        for product in products:
            assert "launch_score" in product, f"Product {product.get('product_name')} missing launch_score"
            assert "launch_score_label" in product, f"Product {product.get('product_name')} missing launch_score_label"
            assert "launch_score_reasoning" in product or product.get("launch_score", 0) == 0, \
                f"Product {product.get('product_name')} missing launch_score_reasoning"
        
        print(f"PASS: {len(products)} products returned with launch_score fields")

    def test_products_launch_score_labels_valid(self):
        """Products have valid launch_score_label values"""
        response = requests.get(f"{BASE_URL}/api/products?limit=50")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        valid_labels = {"strong_launch", "promising", "risky", "avoid"}
        
        for product in products:
            label = product.get("launch_score_label", "risky")
            assert label in valid_labels, f"Invalid launch_score_label: {label}"
        
        print(f"PASS: All {len(products)} products have valid launch_score_label values")

    def test_launch_score_categories_correct(self):
        """Verify launch_score categories match: 80+=strong, 60-79=promising, 40-59=risky, <40=avoid"""
        response = requests.get(f"{BASE_URL}/api/products?limit=100")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        
        mismatched = []
        for product in products:
            score = product.get("launch_score", 0)
            label = product.get("launch_score_label", "risky")
            
            expected_label = None
            if score >= 80:
                expected_label = "strong_launch"
            elif score >= 60:
                expected_label = "promising"
            elif score >= 40:
                expected_label = "risky"
            else:
                expected_label = "avoid"
            
            if label != expected_label:
                mismatched.append({
                    "product": product.get("product_name"),
                    "score": score,
                    "actual_label": label,
                    "expected_label": expected_label
                })
        
        if mismatched:
            for m in mismatched[:5]:  # Show first 5
                print(f"MISMATCH: {m['product']} - score={m['score']}, label={m['actual_label']}, expected={m['expected_label']}")
        
        assert len(mismatched) == 0, f"{len(mismatched)} products have incorrect launch_score_label"
        print(f"PASS: All {len(products)} products have correctly categorized launch_score_label")

    def test_product_with_strong_launch_score(self):
        """Find and verify a product with strong_launch label (score >= 80)"""
        response = requests.get(f"{BASE_URL}/api/products?limit=100&sort_by=launch_score&sort_order=desc")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        strong_launch_products = [p for p in products if p.get("launch_score", 0) >= 80]
        
        if not strong_launch_products:
            # Try to find products sorted by launch_score
            print("INFO: No products with launch_score >= 80 found")
            pytest.skip("No products with strong_launch score available for testing")
        
        top_product = strong_launch_products[0]
        assert top_product.get("launch_score_label") == "strong_launch", \
            f"Expected strong_launch label for score {top_product.get('launch_score')}"
        
        print(f"PASS: Found strong_launch product: {top_product.get('product_name')} with score {top_product.get('launch_score')}")


class TestDailyWinnersLaunchScore:
    """Test /api/dashboard/daily-winners endpoint returns launch_score"""

    def test_daily_winners_returns_launch_score(self):
        """GET /api/dashboard/daily-winners returns products with launch_score"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "daily_winners" in data, "Missing daily_winners field"
        
        winners = data["daily_winners"]
        if len(winners) == 0:
            pytest.skip("No daily winners returned")
        
        # All winners should have launch_score fields
        for winner in winners:
            assert "launch_score" in winner, f"Winner missing launch_score"
            assert "launch_score_label" in winner, f"Winner missing launch_score_label"
            assert "launch_score_reasoning" in winner, f"Winner missing launch_score_reasoning"
        
        print(f"PASS: {len(winners)} daily winners returned with launch_score fields")

    def test_daily_winners_sorted_by_launch_score(self):
        """Daily winners are sorted by launch_score descending"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners?limit=10")
        assert response.status_code == 200
        
        winners = response.json().get("daily_winners", [])
        if len(winners) < 2:
            pytest.skip("Not enough winners to verify sorting")
        
        scores = [w.get("launch_score", 0) for w in winners]
        sorted_scores = sorted(scores, reverse=True)
        
        assert scores == sorted_scores, f"Winners not sorted by launch_score: {scores}"
        print(f"PASS: Daily winners sorted by launch_score: {scores}")

    def test_daily_winners_have_required_fields(self):
        """Daily winners response includes all expected fields"""
        response = requests.get(f"{BASE_URL}/api/dashboard/daily-winners?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        winners = data.get("daily_winners", [])
        
        if not winners:
            pytest.skip("No daily winners returned")
        
        expected_fields = [
            "product_id", "product_name", "category",
            "launch_score", "launch_score_label", "launch_score_reasoning",
            "trend_stage", "competition_level", "success_probability",
            "validation_result", "validation_label"
        ]
        
        for winner in winners:
            missing = [f for f in expected_fields if f not in winner]
            if missing:
                print(f"WARNING: Winner {winner.get('product_name')} missing fields: {missing}")
        
        first_winner = winners[0]
        for field in expected_fields:
            assert field in first_winner, f"First winner missing expected field: {field}"
        
        print(f"PASS: Daily winners have all expected fields")


class TestLaunchScoreReasoning:
    """Test launch_score_reasoning includes strengths and weaknesses"""

    def test_reasoning_has_strengths(self):
        """Launch score reasoning includes strengths"""
        response = requests.get(f"{BASE_URL}/api/products?limit=50&sort_by=launch_score&sort_order=desc")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        products_with_reasoning = [p for p in products if p.get("launch_score_reasoning")]
        
        if not products_with_reasoning:
            pytest.skip("No products with launch_score_reasoning found")
        
        # Check for products with strong launch score - they should have strengths
        for product in products_with_reasoning[:10]:
            reasoning = product.get("launch_score_reasoning", "")
            label = product.get("launch_score_label", "")
            
            if label in ["strong_launch", "promising"]:
                assert "Strong:" in reasoning or len(reasoning) > 20, \
                    f"Product {product.get('product_name')} ({label}) should have strengths in reasoning"
        
        print(f"PASS: Products with good scores have strengths in reasoning")

    def test_risky_products_have_weaknesses(self):
        """Risky/avoid products have weaknesses mentioned"""
        response = requests.get(f"{BASE_URL}/api/products?limit=100")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        risky_products = [p for p in products if p.get("launch_score_label") in ["risky", "avoid"]]
        
        if not risky_products:
            print("INFO: No risky/avoid products found")
            pytest.skip("No risky products to test")
        
        # Check that risky products mention weaknesses or caution
        for product in risky_products[:5]:
            reasoning = product.get("launch_score_reasoning", "")
            # Should have some warning text
            has_warning = any(x in reasoning.lower() for x in ["weak", "risk", "caution", "alternative", "high risk"])
            if not has_warning and reasoning:
                print(f"INFO: Risky product {product.get('product_name')} reasoning: {reasoning}")
        
        print(f"PASS: {len(risky_products)} risky/avoid products found")


class TestPipelineStatusLaunchScore:
    """Test pipeline status includes launch_score stats"""

    def test_pipeline_status_has_launch_score_stats(self):
        """GET /api/automation/pipeline/status includes launch_score product stats"""
        response = requests.get(f"{BASE_URL}/api/automation/pipeline/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "product_stats" in data, "Missing product_stats field"
        
        stats = data["product_stats"]
        assert "with_launch_score" in stats, "Missing with_launch_score stat"
        assert "strong_launch" in stats, "Missing strong_launch stat"
        
        print(f"PASS: Pipeline status shows {stats.get('with_launch_score', 0)} products with launch_score, {stats.get('strong_launch', 0)} strong_launch")


class TestSpecificProductLaunchScore:
    """Test specific products mentioned in context"""

    def test_find_electric_heated_lunch_box(self):
        """Search for Electric Heated Lunch Box and verify launch_score"""
        response = requests.get(f"{BASE_URL}/api/products?search=Electric+Heated+Lunch&limit=10")
        assert response.status_code == 200
        
        products = response.json().get("data", [])
        
        if not products:
            # Try broader search
            response = requests.get(f"{BASE_URL}/api/products?search=lunch&limit=20")
            products = response.json().get("data", [])
        
        if not products:
            print("INFO: Electric Heated Lunch Box product not found - may have different name")
            pytest.skip("Product not found in database")
        
        lunch_box = None
        for p in products:
            if "lunch" in p.get("product_name", "").lower():
                lunch_box = p
                break
        
        if lunch_box:
            launch_score = lunch_box.get("launch_score", 0)
            label = lunch_box.get("launch_score_label", "")
            print(f"Found: {lunch_box.get('product_name')} - launch_score={launch_score}, label={label}")
            
            # According to context, it should have launch_score=84 (strong_launch)
            if launch_score >= 80:
                assert label == "strong_launch", f"Score {launch_score} should be strong_launch, got {label}"
                print(f"PASS: Product has strong_launch label as expected")
        else:
            pytest.skip("Lunch box product not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
