"""
Test Ad Winning Engine API endpoints

Tests for:
- GET /api/ad-engine/patterns/{product_id}
- GET /api/ad-engine/blueprint/{product_id}
- GET /api/ad-engine/performance/{product_id}
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_PRODUCT_ID = "68f41478-9ca2-48c6-997d-b121e2ef8ee9"
NON_EXISTENT_PRODUCT_ID = "00000000-0000-0000-0000-000000000000"


class TestAdEnginePatterns:
    """Test GET /api/ad-engine/patterns/{product_id}"""
    
    def test_patterns_returns_200_for_valid_product(self):
        """Test patterns endpoint returns 200 for existing product."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/patterns/{TEST_PRODUCT_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Patterns endpoint returns 200 for valid product")
    
    def test_patterns_response_structure(self):
        """Test patterns response contains all required fields."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/patterns/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level fields
        assert "product_id" in data, "Missing product_id"
        assert "patterns" in data, "Missing patterns"
        assert "platforms" in data, "Missing platforms"
        assert "total_ads_analyzed" in data, "Missing total_ads_analyzed"
        assert "overall_confidence" in data, "Missing overall_confidence"
        assert "overall_confidence_level" in data, "Missing overall_confidence_level"
        print(f"✓ Patterns response has all required top-level fields")
    
    def test_patterns_hook_type_structure(self):
        """Test hook_type has primary and secondary with correct fields."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/patterns/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        patterns = response.json()["patterns"]
        
        hook_type = patterns.get("hook_type", {})
        
        # Primary hook
        primary = hook_type.get("primary", {})
        assert "name" in primary, "Missing primary hook name"
        assert "description" in primary, "Missing primary hook description"
        assert "pattern_frequency" in primary, "Missing primary pattern_frequency"
        assert "pattern_strength" in primary, "Missing primary pattern_strength"
        assert "confidence_score" in primary, "Missing primary confidence_score"
        assert "confidence_level" in primary, "Missing primary confidence_level"
        
        # Secondary hook
        secondary = hook_type.get("secondary", {})
        assert "name" in secondary, "Missing secondary hook name"
        assert "description" in secondary, "Missing secondary hook description"
        assert "pattern_frequency" in secondary, "Missing secondary pattern_frequency"
        assert "confidence_level" in secondary, "Missing secondary confidence_level"
        
        print(f"✓ Hook type has primary and secondary with all required fields")
        print(f"  Primary: {primary['name']} ({primary['confidence_level']} confidence)")
        print(f"  Secondary: {secondary['name']} ({secondary['confidence_level']} confidence)")
    
    def test_patterns_video_length(self):
        """Test video_length has required fields."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/patterns/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        patterns = response.json()["patterns"]
        
        video_length = patterns.get("video_length", {})
        assert "dominant_range" in video_length, "Missing dominant_range"
        assert "platform" in video_length, "Missing platform"
        assert "best_for" in video_length, "Missing best_for"
        print(f"✓ Video length: {video_length['dominant_range']} for {video_length['platform']}")
    
    def test_patterns_content_format(self):
        """Test content_format has ugc_ratio, studio_ratio, dominant."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/patterns/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        patterns = response.json()["patterns"]
        
        content = patterns.get("content_format", {})
        assert "ugc_ratio" in content, "Missing ugc_ratio"
        assert "studio_ratio" in content, "Missing studio_ratio"
        assert "dominant" in content, "Missing dominant"
        assert content["ugc_ratio"] + content["studio_ratio"] == 100, "UGC + Studio should equal 100"
        print(f"✓ Content format: {content['dominant']} (UGC: {content['ugc_ratio']}%)")
    
    def test_patterns_cta_style(self):
        """Test cta_style has name, example, pattern_strength."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/patterns/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        patterns = response.json()["patterns"]
        
        cta = patterns.get("cta_style", {})
        assert "name" in cta, "Missing CTA name"
        assert "example" in cta, "Missing CTA example"
        assert "pattern_strength" in cta, "Missing pattern_strength"
        print(f"✓ CTA style: {cta['name']} - '{cta['example']}'")
    
    def test_patterns_music_sound(self):
        """Test music_sound has dominant_type."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/patterns/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        patterns = response.json()["patterns"]
        
        music = patterns.get("music_sound", {})
        assert "dominant_type" in music, "Missing dominant_type"
        print(f"✓ Music/Sound: {music['dominant_type']}")
    
    def test_patterns_engagement_indicators(self):
        """Test engagement_indicators has all required metrics."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/patterns/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        patterns = response.json()["patterns"]
        
        engagement = patterns.get("engagement_indicators", {})
        assert "avg_engagement_rate" in engagement, "Missing avg_engagement_rate"
        assert "comment_sentiment" in engagement, "Missing comment_sentiment"
        assert "save_rate" in engagement, "Missing save_rate"
        print(f"✓ Engagement: {engagement['avg_engagement_rate']}% engagement, {engagement['comment_sentiment']} sentiment")
    
    def test_patterns_returns_404_for_non_existent_product(self):
        """Test patterns returns 404 for non-existent product."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/patterns/{NON_EXISTENT_PRODUCT_ID}")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Patterns returns 404 for non-existent product")


class TestAdEngineBlueprint:
    """Test GET /api/ad-engine/blueprint/{product_id}"""
    
    def test_blueprint_returns_200_for_valid_product(self):
        """Test blueprint endpoint returns 200 for existing product."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/blueprint/{TEST_PRODUCT_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Blueprint endpoint returns 200 for valid product")
    
    def test_blueprint_response_structure(self):
        """Test blueprint response contains all required fields."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/blueprint/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level fields
        assert "product_id" in data, "Missing product_id"
        assert "scenes" in data, "Missing scenes"
        assert "hook_variations" in data, "Missing hook_variations"
        assert "filming_tips" in data, "Missing filming_tips"
        assert "target_platforms" in data, "Missing target_platforms"
        assert "optimal_length" in data, "Missing optimal_length"
        assert "content_style" in data, "Missing content_style"
        print(f"✓ Blueprint has all required top-level fields")
        print(f"  Optimal length: {data['optimal_length']}, Style: {data['content_style']}")
    
    def test_blueprint_has_5_scenes(self):
        """Test blueprint has exactly 5 scenes."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/blueprint/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        scenes = data.get("scenes", [])
        assert len(scenes) == 5, f"Expected 5 scenes, got {len(scenes)}"
        print(f"✓ Blueprint has exactly 5 scenes")
    
    def test_blueprint_scene_structure(self):
        """Test each scene has required fields."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/blueprint/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        scenes = response.json().get("scenes", [])
        
        expected_scenes = ["Hook", "Product Introduction", "Demonstration", "Result / Transformation", "CTA"]
        
        for i, scene in enumerate(scenes):
            assert "scene" in scene, f"Scene {i} missing scene name"
            assert "timing" in scene, f"Scene {i} missing timing"
            assert "visual" in scene, f"Scene {i} missing visual"
            assert "text_overlay" in scene or scene.get("text_overlay") == "", f"Scene {i} missing text_overlay"
            assert "audio" in scene, f"Scene {i} missing audio"
            assert "purpose" in scene, f"Scene {i} missing purpose"
            print(f"  Scene {i}: {scene['scene']} ({scene['timing']})")
        
        print(f"✓ All 5 scenes have required structure")
    
    def test_blueprint_has_3_hook_variations(self):
        """Test blueprint has 3 hook variations."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/blueprint/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        hook_variations = data.get("hook_variations", [])
        assert len(hook_variations) == 3, f"Expected 3 hook variations, got {len(hook_variations)}"
        
        for hv in hook_variations:
            assert "hook_type" in hv, "Hook variation missing hook_type"
            assert "opening_line" in hv, "Hook variation missing opening_line"
            assert "effectiveness" in hv, "Hook variation missing effectiveness"
        
        print(f"✓ Blueprint has 3 hook variations")
        for hv in hook_variations:
            print(f"  - {hv['hook_type']} ({hv['effectiveness']}% eff)")
    
    def test_blueprint_has_5_filming_tips(self):
        """Test blueprint has 5 filming tips."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/blueprint/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        tips = data.get("filming_tips", [])
        assert len(tips) == 5, f"Expected 5 filming tips, got {len(tips)}"
        print(f"✓ Blueprint has 5 filming tips")
        for tip in tips:
            print(f"  - {tip[:50]}...")
    
    def test_blueprint_returns_404_for_non_existent_product(self):
        """Test blueprint returns 404 for non-existent product."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/blueprint/{NON_EXISTENT_PRODUCT_ID}")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Blueprint returns 404 for non-existent product")


class TestAdEnginePerformance:
    """Test GET /api/ad-engine/performance/{product_id}"""
    
    def test_performance_returns_200_for_valid_product(self):
        """Test performance endpoint returns 200 for existing product."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/performance/{TEST_PRODUCT_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Performance endpoint returns 200 for valid product")
    
    def test_performance_response_structure(self):
        """Test performance response contains all required fields."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/performance/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "product_id" in data, "Missing product_id"
        assert "engagement_level" in data, "Missing engagement_level"
        assert "engagement_description" in data, "Missing engagement_description"
        assert "activity_trend" in data, "Missing activity_trend"
        assert "trend_icon" in data, "Missing trend_icon"
        assert "ad_saturation" in data, "Missing ad_saturation"
        assert "saturation_advice" in data, "Missing saturation_advice"
        assert "ads_detected" in data, "Missing ads_detected"
        assert "ads_discovered" in data, "Missing ads_discovered"
        assert "platforms_active" in data, "Missing platforms_active"
        
        print(f"✓ Performance response has all required fields")
        print(f"  Engagement: {data['engagement_level']}")
        print(f"  Trend: {data['activity_trend']}")
        print(f"  Saturation: {data['ad_saturation']}")
    
    def test_performance_engagement_level_values(self):
        """Test engagement_level is one of valid values."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/performance/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        valid_levels = ["Very High", "High", "Medium", "Low", "None"]
        assert data["engagement_level"] in valid_levels, f"Invalid engagement_level: {data['engagement_level']}"
        print(f"✓ Engagement level is valid: {data['engagement_level']}")
    
    def test_performance_activity_trend_values(self):
        """Test activity_trend is one of valid values."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/performance/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        valid_trends = ["Rapidly Growing", "Growing", "Stable", "Declining"]
        assert data["activity_trend"] in valid_trends, f"Invalid activity_trend: {data['activity_trend']}"
        print(f"✓ Activity trend is valid: {data['activity_trend']}")
    
    def test_performance_trend_icon_values(self):
        """Test trend_icon is one of valid values."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/performance/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        valid_icons = ["rocket", "trending-up", "trending-down", "minus"]
        assert data["trend_icon"] in valid_icons, f"Invalid trend_icon: {data['trend_icon']}"
        print(f"✓ Trend icon is valid: {data['trend_icon']}")
    
    def test_performance_saturation_values(self):
        """Test ad_saturation is one of valid values."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/performance/{TEST_PRODUCT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        valid_saturation = ["High", "Medium", "Low"]
        assert data["ad_saturation"] in valid_saturation, f"Invalid ad_saturation: {data['ad_saturation']}"
        print(f"✓ Ad saturation is valid: {data['ad_saturation']}")
    
    def test_performance_returns_404_for_non_existent_product(self):
        """Test performance returns 404 for non-existent product."""
        response = requests.get(f"{BASE_URL}/api/ad-engine/performance/{NON_EXISTENT_PRODUCT_ID}")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Performance returns 404 for non-existent product")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
