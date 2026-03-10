"""
Tests for Product of the Week (POTW) feature.
Tests the new email digest enhancement for weekly product highlights.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestProductOfTheWeekEndpoint:
    """GET /api/email/product-of-the-week tests"""

    def test_potw_endpoint_returns_200(self):
        """POTW endpoint should return 200 for public access"""
        response = requests.get(f"{BASE_URL}/api/email/product-of-the-week")
        print(f"POTW GET status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: POTW endpoint returns 200")

    def test_potw_has_featured_product(self):
        """POTW response should have a featured product object"""
        response = requests.get(f"{BASE_URL}/api/email/product-of-the-week")
        assert response.status_code == 200
        data = response.json()
        
        assert "product" in data, "Response must have 'product' field"
        product = data["product"]
        assert isinstance(product, dict), "Product must be a dict"
        print(f"Featured product: {product.get('product_name')}")
        print("PASS: POTW has featured product object")

    def test_potw_product_has_launch_score(self):
        """Featured product must have launch_score field"""
        response = requests.get(f"{BASE_URL}/api/email/product-of-the-week")
        assert response.status_code == 200
        data = response.json()
        product = data.get("product", {})
        
        assert "launch_score" in product, "Product must have 'launch_score' field"
        assert isinstance(product["launch_score"], (int, float)), "launch_score must be numeric"
        print(f"Launch score: {product['launch_score']}")
        print("PASS: Featured product has launch_score")

    def test_potw_product_has_required_fields(self):
        """Featured product must have all required fields"""
        response = requests.get(f"{BASE_URL}/api/email/product-of-the-week")
        assert response.status_code == 200
        data = response.json()
        product = data.get("product", {})
        
        required_fields = ["id", "product_name", "category", "launch_score", "trend_stage"]
        for field in required_fields:
            assert field in product, f"Product missing required field: {field}"
        
        print(f"Product fields present: {list(product.keys())}")
        print("PASS: Featured product has all required fields")

    def test_potw_has_runners_up_array(self):
        """POTW response should have runners_up array"""
        response = requests.get(f"{BASE_URL}/api/email/product-of-the-week")
        assert response.status_code == 200
        data = response.json()
        
        assert "runners_up" in data, "Response must have 'runners_up' field"
        assert isinstance(data["runners_up"], list), "runners_up must be a list"
        print(f"Runners up count: {len(data['runners_up'])}")
        
        # Verify runner-up structure if any exist
        for idx, runner in enumerate(data["runners_up"]):
            assert "id" in runner, f"Runner {idx} missing 'id'"
            assert "product_name" in runner, f"Runner {idx} missing 'product_name'"
            assert "launch_score" in runner, f"Runner {idx} missing 'launch_score'"
            print(f"  Runner #{idx+2}: {runner.get('product_name')} (score: {runner.get('launch_score')})")
        
        print("PASS: POTW has runners_up array with valid structure")

    def test_potw_has_week_of_field(self):
        """POTW response should have week_of date string"""
        response = requests.get(f"{BASE_URL}/api/email/product-of-the-week")
        assert response.status_code == 200
        data = response.json()
        
        assert "week_of" in data, "Response must have 'week_of' field"
        assert isinstance(data["week_of"], str), "week_of must be a string"
        print(f"Week of: {data['week_of']}")
        print("PASS: POTW has week_of field")


class TestSendProductOfTheWeekEndpoint:
    """POST /api/email/send-product-of-the-week tests"""

    def test_send_potw_requires_api_key(self):
        """Send POTW endpoint should require X-API-Key header"""
        response = requests.post(f"{BASE_URL}/api/email/send-product-of-the-week")
        print(f"Send POTW without key status: {response.status_code}")
        assert response.status_code == 401, f"Expected 401 without API key, got {response.status_code}"
        print("PASS: Send POTW requires API key")

    def test_send_potw_rejects_invalid_api_key(self):
        """Send POTW endpoint should reject invalid API key"""
        headers = {"X-API-Key": "invalid_key_12345"}
        response = requests.post(f"{BASE_URL}/api/email/send-product-of-the-week", headers=headers)
        print(f"Send POTW with invalid key status: {response.status_code}")
        assert response.status_code == 401, f"Expected 401 with invalid key, got {response.status_code}"
        print("PASS: Send POTW rejects invalid API key")

    def test_send_potw_accepts_valid_api_key(self):
        """Send POTW endpoint should accept valid API key"""
        headers = {"X-API-Key": "vs_automation_key_2024"}
        response = requests.post(f"{BASE_URL}/api/email/send-product-of-the-week", headers=headers)
        print(f"Send POTW with valid key status: {response.status_code}")
        # Should return 200 regardless of whether emails are sent
        assert response.status_code == 200, f"Expected 200 with valid key, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Response should have status field
        assert "status" in data, "Response must have 'status' field"
        print(f"Send POTW result: {data}")
        print("PASS: Send POTW accepts valid API key")


class TestEmailBranding:
    """Tests to verify email templates use TrendScout branding"""

    def test_email_service_uses_trendscout_branding(self):
        """Email service should use TrendScout in templates (code inspection)"""
        # Read email_service.py and check for TrendScout branding
        import os
        email_service_path = "/app/backend/services/email_service.py"
        
        with open(email_service_path, 'r') as f:
            content = f.read()
        
        # Check for TrendScout branding
        assert "TrendScout" in content, "Email service should mention 'TrendScout'"
        
        # Verify NOT using old ViralScout branding in templates
        # Note: We look for "ViralScout" in the HTML templates section
        # The class name ViralScout in comments/docstrings is OK
        
        # Check in the HTML template sections specifically
        lines = content.split('\n')
        in_html = False
        viralscout_in_html = False
        
        for line in lines:
            if 'html = f"""' in line or "html_content = f'''" in line:
                in_html = True
            if in_html and 'ViralScout' in line:
                viralscout_in_html = True
                print(f"Found ViralScout in HTML: {line.strip()[:80]}")
            if in_html and '"""' in line and 'f"""' not in line:
                in_html = False
        
        assert not viralscout_in_html, "Email HTML templates should use TrendScout, not ViralScout"
        print("PASS: Email service uses TrendScout branding")

    def test_weekly_digest_branding(self):
        """Weekly digest email should use TrendScout branding"""
        email_service_path = "/app/backend/services/email_service.py"
        
        with open(email_service_path, 'r') as f:
            content = f.read()
        
        # Check for TrendScout in the weekly digest subject
        assert "TrendScout Weekly Digest" in content, "Weekly digest should have TrendScout in subject"
        print("PASS: Weekly digest uses TrendScout branding")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
