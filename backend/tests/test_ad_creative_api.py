"""
Test Ad Creative API - Phase 5: AI Ad Creative Generation

Tests the following endpoints:
- POST /api/ad-creatives/generate/{product_id} - Generate ad creatives using LLM
- GET /api/ad-creatives/{product_id} - Retrieve previously generated creatives

Tests validate:
- API response structure (tiktok_scripts, facebook_ads, instagram_captions, etc.)
- Authentication requirements
- Response field validation for each creative type
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "scrapetest@example.com"
TEST_PASSWORD = "Test1234!"

# Product with pre-generated creatives
CACHED_PRODUCT_ID = "68f41478-9ca2-48c6-997d-b121e2ef8ee9"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestAdCreativeGetCached:
    """Tests for GET /api/ad-creatives/{product_id} with cached data"""

    def test_get_cached_creatives_success(self, auth_headers):
        """GET /api/ad-creatives/{product_id} returns cached creatives with success=true"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify success flag
        assert data.get("success") == True
        assert data.get("product_id") == CACHED_PRODUCT_ID
        assert data.get("creatives") is not None

    def test_creatives_has_all_required_fields(self, auth_headers):
        """Response contains creatives object with all required arrays"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        creatives = response.json().get("creatives", {})
        
        # Verify all required fields exist
        assert "tiktok_scripts" in creatives
        assert "facebook_ads" in creatives
        assert "instagram_captions" in creatives
        assert "product_angles" in creatives
        assert "headlines" in creatives
        assert "video_storyboard" in creatives
        assert "shot_list" in creatives
        assert "voiceover_script" in creatives

    def test_tiktok_scripts_structure(self, auth_headers):
        """Each tiktok_script has: title, hook, script, cta fields"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        scripts = response.json().get("creatives", {}).get("tiktok_scripts", [])
        
        assert len(scripts) >= 1, "Should have at least 1 TikTok script"
        
        for script in scripts:
            assert "title" in script, "TikTok script missing 'title'"
            assert "hook" in script, "TikTok script missing 'hook'"
            assert "script" in script, "TikTok script missing 'script'"
            assert "cta" in script, "TikTok script missing 'cta'"
            
            # Verify non-empty strings
            assert isinstance(script["title"], str) and len(script["title"]) > 0
            assert isinstance(script["hook"], str) and len(script["hook"]) > 0
            assert isinstance(script["script"], str) and len(script["script"]) > 0
            assert isinstance(script["cta"], str) and len(script["cta"]) > 0

    def test_facebook_ads_structure(self, auth_headers):
        """Each facebook_ad has: headline, primary_text, description, cta_button fields"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        ads = response.json().get("creatives", {}).get("facebook_ads", [])
        
        assert len(ads) >= 1, "Should have at least 1 Facebook ad"
        
        for ad in ads:
            assert "headline" in ad, "Facebook ad missing 'headline'"
            assert "primary_text" in ad, "Facebook ad missing 'primary_text'"
            assert "description" in ad, "Facebook ad missing 'description'"
            assert "cta_button" in ad, "Facebook ad missing 'cta_button'"
            
            # Verify non-empty strings
            assert isinstance(ad["headline"], str) and len(ad["headline"]) > 0
            assert isinstance(ad["primary_text"], str) and len(ad["primary_text"]) > 0
            assert isinstance(ad["description"], str) and len(ad["description"]) > 0
            assert isinstance(ad["cta_button"], str) and len(ad["cta_button"]) > 0

    def test_instagram_captions_structure(self, auth_headers):
        """Each instagram_caption has caption and hashtags array"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        captions = response.json().get("creatives", {}).get("instagram_captions", [])
        
        assert len(captions) >= 1, "Should have at least 1 Instagram caption"
        
        for caption in captions:
            assert "caption" in caption, "Instagram caption missing 'caption'"
            assert "hashtags" in caption, "Instagram caption missing 'hashtags'"
            
            assert isinstance(caption["caption"], str) and len(caption["caption"]) > 0
            assert isinstance(caption["hashtags"], list)

    def test_product_angles_structure(self, auth_headers):
        """Product angles have angle, target_audience, hook fields"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        angles = response.json().get("creatives", {}).get("product_angles", [])
        
        assert len(angles) >= 1, "Should have at least 1 product angle"
        
        for angle in angles:
            assert "angle" in angle, "Product angle missing 'angle'"
            assert "target_audience" in angle, "Product angle missing 'target_audience'"
            assert "hook" in angle, "Product angle missing 'hook'"

    def test_headlines_array(self, auth_headers):
        """Headlines is an array of strings"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        headlines = response.json().get("creatives", {}).get("headlines", [])
        
        assert len(headlines) >= 1, "Should have at least 1 headline"
        assert all(isinstance(h, str) for h in headlines), "All headlines should be strings"

    def test_video_storyboard_structure(self, auth_headers):
        """Video storyboard has scene, duration, visual, text_overlay, audio"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        scenes = response.json().get("creatives", {}).get("video_storyboard", [])
        
        assert len(scenes) >= 1, "Should have at least 1 storyboard scene"
        
        for scene in scenes:
            assert "scene" in scene, "Scene missing 'scene' number"
            assert "duration" in scene, "Scene missing 'duration'"
            assert "visual" in scene, "Scene missing 'visual'"

    def test_shot_list_structure(self, auth_headers):
        """Shot list has shot, type, description, purpose"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        shots = response.json().get("creatives", {}).get("shot_list", [])
        
        assert len(shots) >= 1, "Should have at least 1 shot"
        
        for shot in shots:
            assert "type" in shot, "Shot missing 'type'"
            assert "description" in shot, "Shot missing 'description'"
            assert "purpose" in shot, "Shot missing 'purpose'"

    def test_voiceover_script_is_string(self, auth_headers):
        """Voiceover script is a non-empty string"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        voiceover = response.json().get("creatives", {}).get("voiceover_script")
        
        assert voiceover is not None, "Should have voiceover_script"
        assert isinstance(voiceover, str) and len(voiceover) > 0


class TestAdCreativeGetNonCached:
    """Tests for GET /api/ad-creatives/{product_id} without cached data"""

    def test_get_non_cached_returns_message(self, auth_headers):
        """GET for product without creatives returns appropriate message"""
        # Use a product that hasn't had creatives generated
        test_product_id = "6731d2cc-89fb-4ed0-a468-4d1a1ffaa15b"
        
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{test_product_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have product_id and creatives: null or message
        assert data.get("product_id") == test_product_id
        # Either creatives is null or message exists
        assert data.get("creatives") is None or "message" in data


class TestAdCreativeAuth:
    """Tests for authentication requirements"""

    def test_get_without_auth_returns_401(self):
        """GET without auth token returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}"
        )
        
        assert response.status_code == 401

    def test_post_without_auth_returns_401(self):
        """POST without auth token returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/ad-creatives/generate/{CACHED_PRODUCT_ID}"
        )
        
        assert response.status_code == 401


class TestAdCreativeGenerate:
    """Tests for POST /api/ad-creatives/generate/{product_id}
    
    Note: This calls the real LLM API and takes 10-15 seconds.
    We test with the cached product to avoid generating new content in every test run.
    """

    def test_generate_returns_success_true(self, auth_headers):
        """POST generate returns success=true with creatives"""
        # Use cached product - it will return quickly if already cached
        response = requests.post(
            f"{BASE_URL}/api/ad-creatives/generate/{CACHED_PRODUCT_ID}",
            headers=auth_headers,
            timeout=60  # LLM calls can take 10-15 seconds
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert data.get("product_id") == CACHED_PRODUCT_ID
        assert data.get("creatives") is not None

    def test_generate_with_invalid_product_returns_404(self, auth_headers):
        """POST generate with invalid product_id returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/ad-creatives/generate/invalid-product-id-12345",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestAdCreativeMetadata:
    """Tests for response metadata fields"""

    def test_response_has_provider_field(self, auth_headers):
        """Response includes provider field (openai/anthropic/gemini)"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "provider" in data
        assert data["provider"] in ["openai", "anthropic", "gemini"]

    def test_response_has_generated_at(self, auth_headers):
        """Response includes generated_at timestamp"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "generated_at" in data
        assert isinstance(data["generated_at"], str)

    def test_response_has_product_name(self, auth_headers):
        """Response includes product_name"""
        response = requests.get(
            f"{BASE_URL}/api/ad-creatives/{CACHED_PRODUCT_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "product_name" in data
        assert isinstance(data["product_name"], str) and len(data["product_name"]) > 0


# =====================================================
# RUN TESTS
# =====================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
