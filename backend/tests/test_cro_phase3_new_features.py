"""
Test suite for Phase 3 CRO new features (iteration 102):
- Exit-intent popup (frontend component)
- Social proof toast notifications (frontend component)
- Product quiz page (frontend + backend lead capture)
- Weekly email digest endpoint
- Tool recommender widget (frontend component)
- Shareable calculator results
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestShareResultEndpoint:
    """Tests for GET /api/leads/share-result endpoint"""
    
    def test_share_result_basic(self):
        """Test basic share result with tool and result params"""
        response = requests.get(
            f"{BASE_URL}/api/leads/share-result",
            params={"tool": "Margin", "result": "34%"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "share" in data
        assert data["share"]["title"] == "My UK Margin result — TrendScout"
        assert "34%" in data["share"]["text"]
        assert "url" in data["share"]
        assert data["share"]["hashtags"] == "ecommerce,UK,productresearch"
    
    def test_share_result_with_detail(self):
        """Test share result with detail parameter"""
        response = requests.get(
            f"{BASE_URL}/api/leads/share-result",
            params={
                "tool": "Profit Margin",
                "result": "36.7%",
                "detail": "Net profit £11.00"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "36.7%" in data["share"]["text"]
        assert "Net profit £11.00" in data["share"]["text"]
    
    def test_share_result_different_tools(self):
        """Test share result for different calculator tools"""
        tools = ["ROAS", "UK VAT", "Product Pricing"]
        for tool in tools:
            response = requests.get(
                f"{BASE_URL}/api/leads/share-result",
                params={"tool": tool, "result": "test result"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert tool in data["share"]["title"]
    
    def test_share_result_url_contains_tools_path(self):
        """Test that share URL points to /tools page"""
        response = requests.get(
            f"{BASE_URL}/api/leads/share-result",
            params={"tool": "Test", "result": "100"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "/tools" in data["share"]["url"]


class TestWeeklyDigestEndpoint:
    """Tests for POST /api/leads/send-digest endpoint"""
    
    def test_digest_unauthorized_without_key(self):
        """Test digest endpoint rejects requests without admin_key"""
        response = requests.post(
            f"{BASE_URL}/api/leads/send-digest",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] == "Unauthorized"
    
    def test_digest_unauthorized_with_wrong_key(self):
        """Test digest endpoint rejects requests with wrong admin_key"""
        response = requests.post(
            f"{BASE_URL}/api/leads/send-digest",
            json={"admin_key": "wrong_key_12345"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] == "Unauthorized"
    
    def test_digest_endpoint_exists(self):
        """Test that digest endpoint exists and responds"""
        response = requests.post(
            f"{BASE_URL}/api/leads/send-digest",
            json={"admin_key": "test"}
        )
        # Should return 200 with error message, not 404
        assert response.status_code == 200


class TestLeadCaptureFromQuiz:
    """Tests for POST /api/leads/capture with quiz source"""
    
    def test_capture_from_product_quiz(self):
        """Test lead capture from product quiz source"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "test-quiz-capture@example.com",
                "source": "product_quiz",
                "context": '{"channel":"shopify","stage":"scaling","challenge":"margins","budget":"mid"}'
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_capture_from_exit_intent(self):
        """Test lead capture from exit intent popup source"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "test-exit-intent@example.com",
                "source": "exit_intent",
                "context": "/pricing"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_capture_invalid_email_returns_error(self):
        """Test that invalid email returns error"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "invalid-email",
                "source": "product_quiz"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Invalid email" in data["message"]
    
    def test_capture_empty_email_returns_error(self):
        """Test that empty email returns error"""
        response = requests.post(
            f"{BASE_URL}/api/leads/capture",
            json={
                "email": "",
                "source": "product_quiz"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"


class TestFrontendPagesLoad:
    """Tests that new frontend pages load correctly"""
    
    def test_product_quiz_page_loads(self):
        """Test /product-quiz page returns 200 (React SPA - content rendered client-side)"""
        response = requests.get(f"{BASE_URL}/product-quiz")
        assert response.status_code == 200
        # React SPA returns index.html shell - actual content rendered client-side
        assert "<!doctype html>" in response.text.lower()
    
    def test_tools_page_loads(self):
        """Test /tools page returns 200"""
        response = requests.get(f"{BASE_URL}/tools")
        assert response.status_code == 200
    
    def test_comparison_page_loads(self):
        """Test comparison page with ToolRecommender loads"""
        response = requests.get(f"{BASE_URL}/compare/jungle-scout-vs-trendscout")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
