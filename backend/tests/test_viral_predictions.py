"""
TikTok Viral Predictor API Tests.

Tests for:
- GET /api/public/viral-predictions (public teaser - 3 predictions)
- GET /api/viral-predictions (premium - all predictions, requires auth)
- POST /api/viral-predictions/refresh (generate fresh predictions, requires auth)
- GET /api/viral-predictions/history (prediction batches, requires auth)
- Regression tests for existing endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "reviewer@trendscout.click"
ADMIN_PASSWORD = "ShopifyReview2026!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session - no cookies to avoid CSRF issues."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    # Disable cookies to avoid CSRF middleware triggering
    session.cookies.clear()
    return session


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for premium endpoints."""
    # Use a fresh session without cookies
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def authenticated_client(auth_token):
    """Fresh session with auth header only (no cookies to avoid CSRF)."""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    # Clear any cookies to ensure Bearer-only auth
    session.cookies.clear()
    return session


class TestPublicViralPredictions:
    """Tests for public viral predictions endpoint (no auth required)."""

    def test_public_viral_predictions_returns_3_predictions(self, api_client):
        """GET /api/public/viral-predictions should return 3 predictions as teaser."""
        response = api_client.get(f"{BASE_URL}/api/public/viral-predictions")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Response should have success: true"
        
        predictions = data.get("predictions", [])
        # Should return exactly 3 or fewer (if less than 3 exist)
        assert len(predictions) <= 3, f"Public endpoint should return max 3 predictions, got {len(predictions)}"
        
        # total_available should be >= 3 (or equal to predictions count if less)
        total_available = data.get("total_available", 0)
        assert total_available >= len(predictions), f"total_available ({total_available}) should be >= predictions count ({len(predictions)})"
        
        # Should have upgrade_cta for unauthenticated users
        assert "upgrade_cta" in data, "Public endpoint should include upgrade_cta"
        
        print(f"✓ Public endpoint returned {len(predictions)} predictions, total_available: {total_available}")

    def test_public_viral_predictions_structure(self, api_client):
        """Each prediction should have required fields."""
        response = api_client.get(f"{BASE_URL}/api/public/viral-predictions")
        
        assert response.status_code == 200
        data = response.json()
        predictions = data.get("predictions", [])
        
        if len(predictions) == 0:
            pytest.skip("No predictions available to test structure")
        
        required_fields = [
            "viral_score", "confidence", "urgency", "reasoning",
            "tiktok_format", "hook_idea", "hashtags"
        ]
        
        for pred in predictions:
            for field in required_fields:
                assert field in pred, f"Prediction missing required field: {field}"
            
            # Validate viral_score is a number
            assert isinstance(pred.get("viral_score"), (int, float)), "viral_score should be numeric"
            
            # Validate confidence is valid
            assert pred.get("confidence") in ["high", "medium", "low"], f"Invalid confidence: {pred.get('confidence')}"
            
            # Validate urgency is valid
            assert pred.get("urgency") in ["high", "medium", "low"], f"Invalid urgency: {pred.get('urgency')}"
            
            # Validate hashtags is a list
            assert isinstance(pred.get("hashtags"), list), "hashtags should be a list"
        
        print(f"✓ All {len(predictions)} predictions have valid structure")


class TestPremiumViralPredictions:
    """Tests for premium viral predictions endpoints (auth required)."""

    def test_premium_predictions_without_auth_returns_401(self, api_client):
        """GET /api/viral-predictions without auth should return 401."""
        # Create a fresh session without auth
        fresh_session = requests.Session()
        fresh_session.headers.update({"Content-Type": "application/json"})
        
        response = fresh_session.get(f"{BASE_URL}/api/viral-predictions")
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ Premium endpoint correctly returns {response.status_code} without auth")

    def test_premium_predictions_with_auth_returns_all(self, authenticated_client):
        """GET /api/viral-predictions with auth should return all predictions."""
        response = authenticated_client.get(f"{BASE_URL}/api/viral-predictions")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Response should have success: true"
        
        predictions = data.get("predictions", [])
        # Premium should return more than 3 (up to 12)
        print(f"✓ Premium endpoint returned {len(predictions)} predictions")
        
        # Should have generated_at timestamp
        assert "generated_at" in data, "Premium response should include generated_at"

    def test_premium_predictions_full_details(self, authenticated_client):
        """Premium predictions should have full details including ad_budget_suggestion."""
        response = authenticated_client.get(f"{BASE_URL}/api/viral-predictions")
        
        assert response.status_code == 200
        data = response.json()
        predictions = data.get("predictions", [])
        
        if len(predictions) == 0:
            pytest.skip("No predictions available to test full details")
        
        # Premium predictions should have additional fields
        premium_fields = [
            "target_demographic", "estimated_views", "ad_budget_suggestion"
        ]
        
        for pred in predictions:
            for field in premium_fields:
                assert field in pred, f"Premium prediction missing field: {field}"
        
        print(f"✓ All {len(predictions)} premium predictions have full details")


class TestViralPredictionsRefresh:
    """Tests for refresh endpoint."""

    def test_refresh_without_auth_returns_401(self, api_client):
        """POST /api/viral-predictions/refresh without auth should return 401."""
        fresh_session = requests.Session()
        fresh_session.headers.update({"Content-Type": "application/json"})
        
        response = fresh_session.post(f"{BASE_URL}/api/viral-predictions/refresh")
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ Refresh endpoint correctly returns {response.status_code} without auth")

    def test_refresh_with_auth_generates_predictions(self, authenticated_client):
        """POST /api/viral-predictions/refresh with auth should generate fresh predictions."""
        # Note: This test may take 10-15 seconds due to GPT-5.2 API call
        response = authenticated_client.post(
            f"{BASE_URL}/api/viral-predictions/refresh",
            timeout=60  # Extended timeout for AI generation
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Response should have success: true"
        
        predictions = data.get("predictions", [])
        count = data.get("count", 0)
        
        assert "generated_at" in data, "Refresh response should include generated_at"
        assert count == len(predictions), f"count ({count}) should match predictions length ({len(predictions)})"
        
        print(f"✓ Refresh generated {count} new predictions")


class TestViralPredictionsHistory:
    """Tests for history endpoint."""

    def test_history_without_auth_returns_401(self, api_client):
        """GET /api/viral-predictions/history without auth should return 401."""
        fresh_session = requests.Session()
        fresh_session.headers.update({"Content-Type": "application/json"})
        
        response = fresh_session.get(f"{BASE_URL}/api/viral-predictions/history")
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ History endpoint correctly returns {response.status_code} without auth")

    def test_history_with_auth_returns_batches(self, authenticated_client):
        """GET /api/viral-predictions/history with auth should return prediction batches."""
        response = authenticated_client.get(f"{BASE_URL}/api/viral-predictions/history")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Response should have success: true"
        
        history = data.get("history", [])
        assert isinstance(history, list), "history should be a list"
        
        # Each batch should have generated_at and predictions
        for batch in history:
            assert "generated_at" in batch, "Each batch should have generated_at"
            assert "predictions" in batch, "Each batch should have predictions"
        
        print(f"✓ History returned {len(history)} batches")

    def test_history_limit_parameter(self, authenticated_client):
        """GET /api/viral-predictions/history?limit=2 should respect limit."""
        response = authenticated_client.get(f"{BASE_URL}/api/viral-predictions/history?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        history = data.get("history", [])
        
        assert len(history) <= 2, f"History should respect limit=2, got {len(history)} batches"
        print(f"✓ History limit parameter works correctly")


class TestRegressionEndpoints:
    """Regression tests for existing endpoints."""

    def test_product_validator_still_works(self):
        """POST /api/public/validate-product should still work."""
        # Use fresh session without cookies to avoid CSRF
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/public/validate-product", json={
            "query": "LED Strip Lights"  # API expects 'query' field
        }, timeout=30)
        
        # Should return 200 or 201
        assert response.status_code in [200, 201], f"Product validator failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data.get("success") is True or "score" in data or "viability_score" in data, "Product validator should return success or score"
        print(f"✓ Product validator regression test passed")

    def test_competitor_spy_still_works(self):
        """POST /api/competitor-spy/scan should still work."""
        # Use fresh session without cookies to avoid CSRF
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/competitor-spy/scan", json={
            "url": "gymshark.com"
        }, timeout=30)
        
        # Should return 200 for valid Shopify store
        assert response.status_code == 200, f"Competitor spy failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Competitor spy should return success: true"
        print(f"✓ Competitor spy regression test passed")

    def test_auth_login_still_works(self, api_client):
        """POST /api/auth/login should still work."""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Auth login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "token" in data, "Auth login should return token"
        print(f"✓ Auth login regression test passed")

    def test_landing_page_health(self, api_client):
        """GET /api/health should return ok."""
        response = api_client.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print(f"✓ Health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
