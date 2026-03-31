"""
Ad Creative Generation Service

Generates marketing creatives for products using LLM.
Supports provider abstraction for OpenAI, Anthropic, Gemini via Emergent LLM Key.
"""

import os
import uuid
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Provider abstraction config
PROVIDERS = {
    "openai": {"model": "gpt-4.1-mini", "provider": "openai"},
    "anthropic": {"model": "claude-sonnet-4-5-20250929", "provider": "anthropic"},
    "gemini": {"model": "gemini-2.5-flash", "provider": "gemini"},
}

DEFAULT_PROVIDER = "openai"


def _get_api_key() -> str:
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_LLM_KEY", "")


SYSTEM_PROMPT = """You are the world's #1 e-commerce direct-response copywriter. You've generated over £50M in revenue for dropshipping and DTC brands.

Your ad copy follows proven frameworks:
- AIDA (Attention → Interest → Desire → Action)
- PAS (Problem → Agitate → Solution)
- Before/After/Bridge

Rules for EVERY piece of copy you write:
1. Open with a pattern-interrupt hook that stops the scroll within 1 second
2. Call out the target buyer specifically (not "everyone")
3. Focus on outcomes and transformations, NOT features
4. Create urgency without being sleazy
5. Every CTA must tell them exactly what happens when they click
6. TikTok scripts must feel native — NOT like ads — conversational, trending format
7. Facebook ads must be long-form story-driven with emotional triggers
8. Instagram captions must be punchy, visual, and hashtag-optimised for reach
9. Use UK English (£ not $, colour not color)
10. Include specific numbers, social proof angles, and scarcity elements

Always return valid JSON. No markdown, no code blocks, just raw JSON."""


async def generate_ad_creatives(product: Dict[str, Any], provider: str = None) -> Dict[str, Any]:
    """
    Generate a premium suite of ad creatives for a product.
    """
    session_id = f"ad-gen-{uuid.uuid4().hex[:8]}"
    
    product_name = product.get('product_name', 'Unknown Product')
    category = product.get('category', 'General')
    price = product.get('estimated_retail_price', 0)
    cost = product.get('supplier_cost', 0)
    margin = price - cost if price and cost else 0
    description = product.get('short_description', product.get('description', product_name))
    trend_score = product.get('trend_score', 0)
    tiktok_views = product.get('tiktok_views', 0)
    competition = product.get('competition_level', 'unknown')
    
    product_context = f"""Product: {product_name}
Category: {category}
Retail Price: £{price:.2f}
Supplier Cost: £{cost:.2f}  
Profit Margin: £{margin:.2f}
Trend Score: {trend_score}/100 (how viral it is right now)
TikTok Views: {tiktok_views:,}
Competition Level: {competition}
Description: {description}"""
    
    prompt = f"""{product_context}

Generate a PREMIUM ad creative package that will outperform competitors. This must be the kind of copy that a top agency would charge £5,000+ for. Return a JSON object:

{{
  "product_angles": [
    {{
      "angle": "specific unique selling angle",
      "target_audience": "precise buyer persona with age, interests, pain points",
      "hook": "pattern-interrupt opening line that stops the scroll",
      "emotional_trigger": "fear/desire/curiosity/belonging/status"
    }}
  ],
  "headlines": [
    "headline using power words and numbers — max 10 words each"
  ],
  "tiktok_scripts": [
    {{
      "title": "script title",
      "format": "trending TikTok format name (e.g., 'POV', 'Things I wish I knew', 'Wait for it')",
      "hook": "first 3 seconds — must create curiosity or shock",
      "script": "full 30-45 second native TikTok script with [ACTIONS] and [TRANSITIONS]. Must feel like a real person talking, NOT an ad. Include trending audio suggestion.",
      "cta": "soft CTA that feels organic (link in bio style)",
      "trending_sound": "suggest a trending sound or audio style"
    }}
  ],
  "facebook_ads": [
    {{
      "headline": "attention-grabbing headline with benefit",
      "primary_text": "long-form story-driven ad (3-4 paragraphs). Start with a relatable problem, build tension, introduce product as the solution, close with social proof and urgency. Use line breaks for readability.",
      "description": "one-line benefit under the image",
      "cta_button": "Shop Now",
      "targeting_suggestion": "who to target and why"
    }}
  ],
  "instagram_captions": [
    {{
      "caption": "engaging caption that drives saves and shares. Start with a hook, tell a micro-story, end with a question to drive comments.",
      "hashtags": ["30 relevant hashtags mixing broad and niche"],
      "best_time_to_post": "day and time recommendation"
    }}
  ],
  "video_storyboard": [
    {{
      "scene": 1,
      "duration": "0-3s",
      "visual": "exactly what to film/show",
      "text_overlay": "large bold text on screen",
      "audio": "specific audio/music direction",
      "purpose": "why this scene converts"
    }}
  ],
  "shot_list": [
    {{
      "shot": 1,
      "type": "close-up/wide/medium/overhead/POV",
      "description": "exactly what to capture",
      "lighting": "lighting direction",
      "purpose": "what this shot achieves psychologically"
    }}
  ],
  "voiceover_script": "full voiceover with [PAUSE] markers, emphasis in CAPS, and emotional direction in (parentheses)",
  "email_sequence": [
    {{
      "subject_line": "email subject (max 50 chars, create curiosity)",
      "preview_text": "preview text that complements subject",
      "body": "short punchy email body with CTA"
    }}
  ],
  "ad_budget_recommendation": {{
    "daily_budget_gbp": "recommended daily spend",
    "test_duration_days": "how long to test",
    "scaling_strategy": "when and how to scale"
  }}
}}

Generate 3 product angles, 5 power headlines, 3 TikTok scripts (different formats), 2 Facebook long-form ads, 3 Instagram captions, 6 storyboard scenes, 5 shots, 1 voiceover, 2 emails, and budget advice. Make EVERY line specific to {product_name} — zero generic filler."""

    try:
        from openai import AsyncOpenAI
        _ac_client = AsyncOpenAI(api_key=_get_api_key())
        _ac_completion = await _ac_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )
        response = _ac_completion.choices[0].message.content
        
        # Parse JSON from response
        response_text = response.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1] if '\n' in response_text else response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        if response_text.startswith('json'):
            response_text = response_text[4:]
        
        creatives = json.loads(response_text.strip())
        
        return {
            "id": str(uuid.uuid4()),
            "product_id": product.get('id'),
            "product_name": product_name,
            "provider": provider or DEFAULT_PROVIDER,
            "creatives": creatives,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "success": True,
        }
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.debug(f"Raw response: {response_text[:500]}")
        return {
            "id": str(uuid.uuid4()),
            "product_id": product.get('id'),
            "product_name": product_name,
            "provider": provider or DEFAULT_PROVIDER,
            "creatives": {"raw_response": response},
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": "Failed to parse structured response",
        }
    except Exception as e:
        logger.error(f"Ad creative generation failed: {e}")
        return {
            "id": str(uuid.uuid4()),
            "product_id": product.get('id'),
            "product_name": product_name,
            "provider": provider or DEFAULT_PROVIDER,
            "creatives": {},
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": str(e),
        }
