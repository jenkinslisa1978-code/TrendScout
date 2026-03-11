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
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

# Provider abstraction config
PROVIDERS = {
    "openai": {"model": "gpt-4.1-mini", "provider": "openai"},
    "anthropic": {"model": "claude-sonnet-4-5-20250929", "provider": "anthropic"},
    "gemini": {"model": "gemini-2.5-flash", "provider": "gemini"},
}

DEFAULT_PROVIDER = "openai"


def _get_api_key() -> str:
    return os.environ.get('EMERGENT_LLM_KEY', '')


def _create_chat(session_id: str, system_message: str, provider: str = None) -> LlmChat:
    """Create an LlmChat instance with the specified provider."""
    provider = provider or DEFAULT_PROVIDER
    config = PROVIDERS.get(provider, PROVIDERS[DEFAULT_PROVIDER])
    
    chat = LlmChat(
        api_key=_get_api_key(),
        session_id=session_id,
        system_message=system_message,
    ).with_model(config["provider"], config["model"])
    
    return chat


SYSTEM_PROMPT = """You are an expert e-commerce marketing copywriter specializing in dropshipping and direct-to-consumer products. 

You create high-converting ad creatives for TikTok, Facebook, Instagram, and other platforms.

Your outputs are always practical, specific to the product, and optimized for conversions.
Always return valid JSON when asked for JSON output. No markdown, no code blocks, just raw JSON."""


async def generate_ad_creatives(product: Dict[str, Any], provider: str = None) -> Dict[str, Any]:
    """
    Generate a full suite of ad creatives for a product.
    
    Returns: tiktok_scripts, facebook_ads, instagram_captions,
             product_angles, headlines, video_storyboard, shot_list, voiceover_script
    """
    session_id = f"ad-gen-{uuid.uuid4().hex[:8]}"
    chat = _create_chat(session_id, SYSTEM_PROMPT, provider)
    
    product_name = product.get('product_name', 'Unknown Product')
    category = product.get('category', 'General')
    price = product.get('estimated_retail_price', 0)
    cost = product.get('supplier_cost', 0)
    description = product.get('short_description', product_name)
    trend_score = product.get('trend_score', 0)
    
    product_context = f"""Product: {product_name}
Category: {category}
Retail Price: £{price:.2f}
Trend Score: {trend_score}/100
Description: {description}"""
    
    # Generate all creatives in one comprehensive prompt
    prompt = f"""{product_context}

Generate a complete ad creative package for this product. Return a JSON object with these exact keys:

{{
  "product_angles": [
    {{"angle": "...", "target_audience": "...", "hook": "..."}}
  ],
  "headlines": [
    "headline 1", "headline 2", "headline 3", "headline 4", "headline 5"
  ],
  "tiktok_scripts": [
    {{
      "title": "...",
      "hook": "opening 3-second hook text",
      "script": "full 30-second script with [ACTIONS] in brackets",
      "cta": "call to action"
    }}
  ],
  "facebook_ads": [
    {{
      "headline": "...",
      "primary_text": "ad body text (2-3 paragraphs)",
      "description": "link description",
      "cta_button": "Shop Now"
    }}
  ],
  "instagram_captions": [
    {{
      "caption": "engaging caption with emojis and hashtags",
      "hashtags": ["tag1", "tag2"]
    }}
  ],
  "video_storyboard": [
    {{
      "scene": 1,
      "duration": "0-3s",
      "visual": "what to show",
      "text_overlay": "on-screen text",
      "audio": "what audio/music"
    }}
  ],
  "shot_list": [
    {{
      "shot": 1,
      "type": "close-up/wide/medium/overhead",
      "description": "what to capture",
      "purpose": "why this shot matters"
    }}
  ],
  "voiceover_script": "full voiceover script for a 30-second video"
}}

Generate 3 product angles, 5 headlines, 2 TikTok scripts, 2 Facebook ads, 2 Instagram captions, 6 storyboard scenes, 5 shots, and 1 voiceover script. Make them specific to this product, not generic."""

    try:
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse JSON from response
        response_text = response.strip()
        # Remove potential markdown code blocks
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
        # Return the raw text as fallback
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
