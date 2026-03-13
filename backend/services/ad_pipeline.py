"""
Multi-Step Ad Creative Generation Pipeline

Breaks ad generation into focused steps for higher quality output:
  Step 1: Product angles & target audiences
  Step 2: Headlines & hooks
  Step 3: TikTok scripts
  Step 4: Facebook ads
  Step 5: Instagram captions
  Step 6: Video storyboard + shot list + voiceover
  Step 7: Email sequence + budget advice

Each step gets its own focused prompt and can be retried independently.
"""

import os
import uuid
import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

PROVIDERS = {
    "openai": {"model": "gpt-4.1-mini", "provider": "openai"},
    "anthropic": {"model": "claude-sonnet-4-5-20250929", "provider": "anthropic"},
    "gemini": {"model": "gemini-2.5-flash", "provider": "gemini"},
}
DEFAULT_PROVIDER = "openai"


def _get_api_key() -> str:
    return os.environ.get("EMERGENT_LLM_KEY", "")


def _create_chat(session_id: str, system_message: str, provider: str = None) -> LlmChat:
    provider = provider or DEFAULT_PROVIDER
    config = PROVIDERS.get(provider, PROVIDERS[DEFAULT_PROVIDER])
    return LlmChat(
        api_key=_get_api_key(),
        session_id=session_id,
        system_message=system_message,
    ).with_model(config["provider"], config["model"])


def _build_product_context(product: Dict[str, Any]) -> str:
    name = product.get("product_name", "Unknown Product")
    category = product.get("category", "General")
    price = product.get("estimated_retail_price", 0)
    cost = product.get("supplier_cost", 0)
    margin = price - cost if price and cost else 0
    desc = product.get("short_description", product.get("description", name))
    return (
        f"Product: {name}\n"
        f"Category: {category}\n"
        f"Retail Price: £{price:.2f}\n"
        f"Supplier Cost: £{cost:.2f}\n"
        f"Profit Margin: £{margin:.2f}\n"
        f"Trend Score: {product.get('trend_score', 0)}/100\n"
        f"TikTok Views: {product.get('tiktok_views', 0):,}\n"
        f"Competition: {product.get('competition_level', 'unknown')}\n"
        f"Description: {desc}"
    )


async def _llm_step(session_prefix: str, system: str, prompt: str, provider: str = None) -> Dict:
    """Execute a single LLM step and parse JSON response."""
    sid = f"{session_prefix}-{uuid.uuid4().hex[:6]}"
    chat = _create_chat(sid, system, provider)
    raw = await chat.send_message(UserMessage(text=prompt))
    text = raw.strip()
    # Strip markdown code blocks
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    if text.startswith("json"):
        text = text[4:]
    return json.loads(text.strip())


COPYWRITER_SYSTEM = (
    "You are the world's #1 e-commerce direct-response copywriter. "
    "You've generated over £50M in revenue for dropshipping and DTC brands. "
    "Use UK English (£, colour). Always return ONLY valid JSON."
)


async def step_1_angles(product: Dict[str, Any], provider: str = None) -> List[Dict]:
    """Generate 3 unique product angles with target audiences."""
    ctx = _build_product_context(product)
    prompt = f"""{ctx}

Generate 3 unique selling angles. Return JSON array:
[{{"angle":"specific angle","target_audience":"precise persona with age, interests, pain points","hook":"pattern-interrupt opening line","emotional_trigger":"fear/desire/curiosity/belonging/status"}}]"""
    return await _llm_step("angles", COPYWRITER_SYSTEM, prompt, provider)


async def step_2_headlines(product: Dict[str, Any], angles: List[Dict], provider: str = None) -> List[str]:
    """Generate 5 power headlines based on angles."""
    ctx = _build_product_context(product)
    angles_str = json.dumps(angles[:3], indent=2)
    prompt = f"""{ctx}

Using these angles:
{angles_str}

Generate 5 power headlines (max 10 words each) that stop the scroll. Return JSON array of strings:
["headline 1","headline 2","headline 3","headline 4","headline 5"]"""
    return await _llm_step("headlines", COPYWRITER_SYSTEM, prompt, provider)


async def step_3_tiktok(product: Dict[str, Any], angles: List[Dict], provider: str = None) -> List[Dict]:
    """Generate 3 TikTok scripts in different formats."""
    ctx = _build_product_context(product)
    prompt = f"""{ctx}

Generate 3 native TikTok scripts in different trending formats. They must feel like real people talking, NOT ads. Return JSON array:
[{{"title":"script title","format":"trending format name","hook":"first 3 seconds","script":"full 30-45 second script with [ACTIONS] and [TRANSITIONS]","cta":"soft organic CTA","trending_sound":"audio suggestion"}}]"""
    return await _llm_step("tiktok", COPYWRITER_SYSTEM, prompt, provider)


async def step_4_facebook(product: Dict[str, Any], angles: List[Dict], provider: str = None) -> List[Dict]:
    """Generate 2 long-form Facebook ads."""
    ctx = _build_product_context(product)
    prompt = f"""{ctx}

Generate 2 story-driven Facebook ads. Each must start with a relatable problem, build tension, introduce product as the solution, close with social proof and urgency. Return JSON array:
[{{"headline":"attention-grabbing headline","primary_text":"3-4 paragraph story-driven ad with line breaks","description":"one-line benefit","cta_button":"Shop Now","targeting_suggestion":"who to target and why"}}]"""
    return await _llm_step("facebook", COPYWRITER_SYSTEM, prompt, provider)


async def step_5_instagram(product: Dict[str, Any], angles: List[Dict], provider: str = None) -> List[Dict]:
    """Generate 3 Instagram captions."""
    ctx = _build_product_context(product)
    prompt = f"""{ctx}

Generate 3 Instagram captions that drive saves and shares. Return JSON array:
[{{"caption":"engaging caption with hook, micro-story, question","hashtags":["30 relevant hashtags"],"best_time_to_post":"day and time"}}]"""
    return await _llm_step("instagram", COPYWRITER_SYSTEM, prompt, provider)


async def step_6_video(product: Dict[str, Any], provider: str = None) -> Dict:
    """Generate video storyboard, shot list, and voiceover script."""
    ctx = _build_product_context(product)
    prompt = f"""{ctx}

Generate a complete video production package. Return JSON object:
{{
  "storyboard": [{{"scene":1,"duration":"0-3s","visual":"what to film","text_overlay":"bold text","audio":"audio direction","purpose":"why this converts"}}],
  "shot_list": [{{"shot":1,"type":"close-up/wide/medium","description":"what to capture","lighting":"lighting","purpose":"psychological effect"}}],
  "voiceover_script": "full voiceover with [PAUSE] markers and emphasis in CAPS"
}}
Generate 6 storyboard scenes and 5 shots."""
    return await _llm_step("video", COPYWRITER_SYSTEM, prompt, provider)


async def step_7_email_budget(product: Dict[str, Any], provider: str = None) -> Dict:
    """Generate email sequence and budget advice."""
    ctx = _build_product_context(product)
    prompt = f"""{ctx}

Generate email marketing and budget advice. Return JSON object:
{{
  "email_sequence": [{{"subject_line":"max 50 chars","preview_text":"complements subject","body":"short punchy email with CTA"}}],
  "ad_budget_recommendation": {{"daily_budget_gbp":"recommended daily spend","test_duration_days":"how long to test","scaling_strategy":"when and how to scale"}}
}}
Generate 2 emails."""
    return await _llm_step("email", COPYWRITER_SYSTEM, prompt, provider)


async def generate_ad_creatives_pipeline(
    product: Dict[str, Any],
    provider: str = None,
    on_step_complete=None,
) -> Dict[str, Any]:
    """
    Full multi-step ad creative pipeline.
    Each step builds on previous results for higher quality.
    Optional callback on_step_complete(step_name, result) for progress tracking.
    """
    product_name = product.get("product_name", "Unknown Product")
    results = {}
    steps_completed = []

    try:
        # Step 1: Angles
        angles = await step_1_angles(product, provider)
        results["product_angles"] = angles
        steps_completed.append("angles")
        if on_step_complete:
            on_step_complete("angles", angles)

        # Step 2: Headlines (uses angles)
        headlines = await step_2_headlines(product, angles, provider)
        results["headlines"] = headlines
        steps_completed.append("headlines")
        if on_step_complete:
            on_step_complete("headlines", headlines)

        # Step 3: TikTok scripts
        tiktok = await step_3_tiktok(product, angles, provider)
        results["tiktok_scripts"] = tiktok
        steps_completed.append("tiktok")
        if on_step_complete:
            on_step_complete("tiktok", tiktok)

        # Step 4: Facebook ads
        facebook = await step_4_facebook(product, angles, provider)
        results["facebook_ads"] = facebook
        steps_completed.append("facebook")
        if on_step_complete:
            on_step_complete("facebook", facebook)

        # Step 5: Instagram captions
        instagram = await step_5_instagram(product, angles, provider)
        results["instagram_captions"] = instagram
        steps_completed.append("instagram")
        if on_step_complete:
            on_step_complete("instagram", instagram)

        # Step 6: Video production
        video = await step_6_video(product, provider)
        results["video_storyboard"] = video.get("storyboard", [])
        results["shot_list"] = video.get("shot_list", [])
        results["voiceover_script"] = video.get("voiceover_script", "")
        steps_completed.append("video")
        if on_step_complete:
            on_step_complete("video", video)

        # Step 7: Email + Budget
        email_budget = await step_7_email_budget(product, provider)
        results["email_sequence"] = email_budget.get("email_sequence", [])
        results["ad_budget_recommendation"] = email_budget.get("ad_budget_recommendation", {})
        steps_completed.append("email_budget")
        if on_step_complete:
            on_step_complete("email_budget", email_budget)

        return {
            "id": str(uuid.uuid4()),
            "product_id": product.get("id"),
            "product_name": product_name,
            "provider": provider or DEFAULT_PROVIDER,
            "pipeline": True,
            "steps_completed": steps_completed,
            "creatives": results,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "success": True,
        }

    except Exception as e:
        logger.error(f"Pipeline failed at step {len(steps_completed) + 1}: {e}")
        return {
            "id": str(uuid.uuid4()),
            "product_id": product.get("id"),
            "product_name": product_name,
            "provider": provider or DEFAULT_PROVIDER,
            "pipeline": True,
            "steps_completed": steps_completed,
            "creatives": results,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": str(e),
            "partial": len(steps_completed) > 0,
        }
