"""
Ad A/B Test Service + Product Launch Simulator

Generates multiple ad variations for testing, tracks performance,
feeds results back into learning system, and simulates launch outcomes.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Hook definitions for variation generation
HOOKS = [
    {"id": "transformation", "name": "Transformation", "opening": "Watch this completely change...", "structure": "Problem → Product → Result", "effectiveness": 85},
    {"id": "problem_solution", "name": "Problem / Solution", "opening": "Tired of dealing with [pain point]?", "structure": "Pain → Agitate → Solution", "effectiveness": 82},
    {"id": "curiosity", "name": "Curiosity", "opening": "I can't believe what happened when I tried this...", "structure": "Tease → Build tension → Reveal", "effectiveness": 80},
    {"id": "social_proof", "name": "Social Proof", "opening": "10,000+ people already switched to this...", "structure": "Proof → Demo → Join", "effectiveness": 78},
    {"id": "unboxing", "name": "Unboxing", "opening": "Let's see what's inside this viral product...", "structure": "Unbox → React → Demo", "effectiveness": 75},
    {"id": "pov_story", "name": "POV / Story", "opening": "POV: You finally find the solution...", "structure": "Setup → Discovery → Life changed", "effectiveness": 74},
]

CTA_OPTIONS = [
    {"style": "urgency", "text": "Only {n} left — grab yours now!", "alt": "Limited stock — order today!"},
    {"style": "discount", "text": "{pct}% off for the next 24 hours!", "alt": "Today only — save big!"},
    {"style": "social", "text": "Join {n}+ happy customers", "alt": "See why everyone's talking about this"},
    {"style": "direct", "text": "Shop now — free shipping today", "alt": "Tap the link — free delivery"},
]


def generate_ad_variations(product: Dict[str, Any], count: int = 3) -> List[Dict[str, Any]]:
    """Generate multiple ad variations with different hook styles."""
    name = product.get("product_name", "Product")
    category = product.get("category", "General")
    seed = int(hashlib.md5(product.get("id", "").encode()).hexdigest()[:8], 16)

    # Select hooks for variations (pick best non-overlapping hooks)
    indices = []
    for i in range(count):
        idx = (seed + i * 2) % len(HOOKS)
        while idx in indices:
            idx = (idx + 1) % len(HOOKS)
        indices.append(idx)

    variations = []
    labels = ["A", "B", "C", "D", "E"]

    for i, idx in enumerate(indices):
        hook = HOOKS[idx]
        cta = CTA_OPTIONS[(seed + i) % len(CTA_OPTIONS)]

        # Build script tailored to hook style
        script = _build_script(hook, name, category, cta)

        variations.append({
            "variation_id": f"var_{labels[i].lower()}_{product.get('id', '')[:8]}",
            "label": f"Variation {labels[i]}",
            "hook_type": hook["name"],
            "hook_id": hook["id"],
            "hook_line": hook["opening"].replace("[pain point]", f"issues with {category.lower()}"),
            "video_structure": hook["structure"],
            "script": script,
            "cta": cta["text"].replace("{n}", str(seed % 500 + 100)).replace("{pct}", str(30 + (seed + i) % 40)),
            "cta_alt": cta["alt"],
            "recommended_length": "7-15s" if hook["effectiveness"] > 80 else "15-30s",
            "effectiveness_estimate": hook["effectiveness"],
        })

    return variations


def _build_script(hook: Dict, name: str, category: str, cta: Dict) -> List[Dict[str, str]]:
    """Build a scene-by-scene script for an ad variation."""
    scripts = {
        "transformation": [
            {"time": "0-2s", "action": f"Show the common problem in {category.lower()}", "audio": "Frustrated sigh or trending sound"},
            {"time": "2-5s", "action": f"Quick cut — introduce {name}", "audio": "Music drop or 'Wait...'"},
            {"time": "5-8s", "action": "Show product in use — the transformation happening", "audio": "Upbeat music builds"},
            {"time": "8-10s", "action": "Reveal the amazing result — before/after split", "audio": "Music peaks"},
            {"time": "10-12s", "action": f"Product beauty shot + CTA: {cta['alt']}", "audio": "Voiceover or text overlay"},
        ],
        "problem_solution": [
            {"time": "0-2s", "action": f"Show relatable pain point in {category.lower()}", "audio": "'Are you tired of...' voiceover"},
            {"time": "2-4s", "action": "Emphasize the frustration — zoom in on the problem", "audio": "Dramatic pause"},
            {"time": "4-7s", "action": f"Introduce {name} as the solution", "audio": "Uplifting music starts"},
            {"time": "7-10s", "action": "Quick demo showing how it solves the problem", "audio": "Continue music"},
            {"time": "10-12s", "action": f"Satisfied reaction + CTA: {cta['alt']}", "audio": "Music resolves"},
        ],
        "curiosity": [
            {"time": "0-2s", "action": "Unexpected or shocking visual — create intrigue", "audio": "'Wait for this...' or trending sound"},
            {"time": "2-4s", "action": "Build tension — 'I didn't believe it either...'", "audio": "Suspenseful music"},
            {"time": "4-7s", "action": f"Reveal {name} — the big payoff", "audio": "Music drop / reveal sound"},
            {"time": "7-10s", "action": "Quick demo showing the product is legit", "audio": "Energetic music"},
            {"time": "10-12s", "action": f"CTA with urgency: {cta['alt']}", "audio": "Voiceover close"},
        ],
        "social_proof": [
            {"time": "0-2s", "action": "'I was skeptical too...' — show honest reaction", "audio": "Talking to camera (UGC style)"},
            {"time": "2-5s", "action": f"Show reviews/screenshots proving {name} works", "audio": "Continue talking"},
            {"time": "5-8s", "action": "Personal demo — 'Here's what happened when I tried it'", "audio": "Natural voiceover"},
            {"time": "8-10s", "action": "Show the result — genuine happy reaction", "audio": "Upbeat background music"},
            {"time": "10-12s", "action": f"CTA: {cta['alt']}", "audio": "Voiceover or text overlay"},
        ],
        "unboxing": [
            {"time": "0-2s", "action": "Hands on package — clean, satisfying opening", "audio": "ASMR sounds or trending audio"},
            {"time": "2-4s", "action": f"Slow reveal of {name} — build anticipation", "audio": "Continue ambient sound"},
            {"time": "4-7s", "action": "First reaction — 'Okay this is actually nice...'", "audio": "Genuine reaction"},
            {"time": "7-10s", "action": "Quick demo or close-up of key features", "audio": "Soft music builds"},
            {"time": "10-12s", "action": f"Beauty shot + CTA: {cta['alt']}", "audio": "Music resolves"},
        ],
        "pov_story": [
            {"time": "0-2s", "action": "'POV: You finally discover the solution' — first person", "audio": "Trending POV sound"},
            {"time": "2-5s", "action": "Walk through the frustrating daily routine", "audio": "Relatable voiceover"},
            {"time": "5-8s", "action": f"Discover {name} — life changes moment", "audio": "Music shifts to positive"},
            {"time": "8-10s", "action": "Show the new and improved routine with product", "audio": "Upbeat resolution"},
            {"time": "10-12s", "action": f"CTA: {cta['alt']}", "audio": "Final voiceover"},
        ],
    }
    return scripts.get(hook["id"], scripts["transformation"])


def generate_test_plan(product: Dict[str, Any], variations: List[Dict]) -> Dict[str, Any]:
    """Generate a step-by-step ad testing plan."""
    return {
        "title": "Ad A/B Test Plan",
        "budget_per_variation": "£10–£20",
        "total_budget": f"£{len(variations) * 15}–£{len(variations) * 20}",
        "duration": "24–48 hours",
        "targeting": "Same audience for all variations",
        "steps": [
            {"step": 1, "title": "Set Up Ads", "description": f"Create {len(variations)} ad campaigns using the variations above. Use the same targeting, budget, and audience for each."},
            {"step": 2, "title": "Set Budget", "description": f"Allocate £10–£20 per variation (£{len(variations) * 10}–£{len(variations) * 20} total). Start with daily budgets."},
            {"step": 3, "title": "Launch & Wait", "description": "Run all ads simultaneously for 24–48 hours. Don't change anything during this period."},
            {"step": 4, "title": "Evaluate Results", "description": "Compare: CTR (click-through rate), CPC (cost per click), ATC (add to cart rate), and purchases."},
            {"step": 5, "title": "Pick Winner", "description": "The variation with the best CTR + lowest CPC wins. Scale that ad and pause the others."},
            {"step": 6, "title": "Scale Winner", "description": "Increase budget on the winning ad by 20-30% every 2-3 days. Monitor ROAS."},
        ],
        "metrics_to_track": [
            {"metric": "CTR", "description": "Click-through rate — how many people click your ad", "good": "> 2%", "average": "1-2%", "poor": "< 1%"},
            {"metric": "CPC", "description": "Cost per click — how much each click costs", "good": "< £0.50", "average": "£0.50-£1.50", "poor": "> £1.50"},
            {"metric": "ATC Rate", "description": "Add-to-cart rate — visitors who add product to cart", "good": "> 8%", "average": "3-8%", "poor": "< 3%"},
            {"metric": "Purchases", "description": "Number of actual purchases from the ad", "good": "Positive ROAS", "average": "Break even", "poor": "Negative ROAS"},
        ],
    }


def simulate_launch(product: Dict[str, Any], outcomes_history: List[Dict] = None) -> Dict[str, Any]:
    """
    Simulate a product launch to estimate potential outcomes.
    Uses launch_score, trend_stage, competition, supplier cost, ad activity,
    and historical outcome data to project realistic ranges.
    """
    launch_score = product.get("launch_score", 50) or 50
    trend_stage = product.get("trend_stage", "Stable")
    competition = product.get("competition_level", "medium")
    ad_count = product.get("ad_count", 0) or 0
    supplier_cost = product.get("supplier_cost") or product.get("cost_price", 0) or 8
    sell_price = product.get("sell_price", 0) or product.get("estimated_profit", 0) * 2 + supplier_cost or 25

    profit_per_sale = round(sell_price - supplier_cost, 2)
    if profit_per_sale <= 0:
        profit_per_sale = round(sell_price * 0.35, 2)

    # Base conversion rate from launch score
    base_cvr = 0.8 + (launch_score / 100) * 3.5  # 0.8% to 4.3%

    # Adjust for trend stage
    stage_mult = {"Exploding": 1.6, "Emerging": 1.3, "Rising": 1.1, "Stable": 1.0, "Declining": 0.7}
    base_cvr *= stage_mult.get(trend_stage, 1.0)

    # Adjust for competition
    comp_mult = {"low": 1.3, "medium": 1.0, "high": 0.7}
    base_cvr *= comp_mult.get(competition, 1.0)

    # Historical adjustment
    hist_mult = 1.0
    if outcomes_history:
        successes = [o for o in outcomes_history if o.get("outcome_status") == "success"]
        if len(successes) >= 2:
            hist_mult = 1.1
        failures = [o for o in outcomes_history if o.get("outcome_status") == "failed"]
        if len(failures) > len(successes) and len(failures) >= 2:
            hist_mult = 0.85

    cvr = round(base_cvr * hist_mult, 2)
    cvr = max(0.5, min(cvr, 6.0))  # clamp between 0.5% and 6%

    # Ad cost estimates
    cpc_base = 0.30 + (ad_count * 0.005)  # more ads = higher CPC
    if competition == "high":
        cpc_base *= 1.5
    elif competition == "low":
        cpc_base *= 0.7
    cpc = round(max(0.15, min(cpc_base, 2.5)), 2)

    # Cost per acquisition
    cpa = round(cpc / (cvr / 100), 2) if cvr > 0 else 99
    breakeven_ad_cost = round(profit_per_sale, 2)

    # Daily sales potential (with ad spend of ~£50/day)
    daily_budget = 50
    daily_clicks = round(daily_budget / cpc)
    daily_sales_low = max(1, round(daily_clicks * (cvr * 0.6 / 100)))
    daily_sales_high = max(daily_sales_low + 1, round(daily_clicks * (cvr * 1.4 / 100)))

    # Profitability
    daily_profit_low = round(daily_sales_low * profit_per_sale - daily_budget, 2)
    daily_profit_high = round(daily_sales_high * profit_per_sale - daily_budget, 2)

    # Break-even days
    if daily_profit_high > 0:
        breakeven_days = max(1, round(daily_budget / max(daily_profit_high, 1)))
    else:
        breakeven_days = None

    # Potential level
    if launch_score >= 65 and cvr >= 2.5 and daily_profit_high > 20:
        potential = "High"
        potential_desc = "Strong signals — this product has good launch potential."
    elif launch_score >= 40 and cvr >= 1.5 and daily_profit_high > 0:
        potential = "Moderate"
        potential_desc = "Decent signals — test with a small budget before scaling."
    else:
        potential = "Risky"
        potential_desc = "Weaker signals — proceed with caution and tight budgets."

    # Risk factors
    risks = []
    if competition == "high":
        risks.append("High competition may increase ad costs")
    if ad_count > 50:
        risks.append("Many advertisers already active — differentiation needed")
    if trend_stage == "Declining":
        risks.append("Product trend is declining — timing risk")
    if profit_per_sale < 10:
        risks.append("Low profit margin — ad costs must stay very low")
    if cvr < 1.5:
        risks.append("Low estimated conversion — test product-market fit first")

    # Beginner guidance
    if potential == "High":
        guidance = f"If ads perform at average levels for similar products, you may reach profitability within {breakeven_days or '3-5'} days. Start with £{round(daily_budget * 0.6)} daily budget."
    elif potential == "Moderate":
        guidance = f"Start small with £15-20 daily budget. If your CTR is above 2% after 48 hours, gradually scale up. Expected break-even in {breakeven_days or '5-10'} days."
    else:
        guidance = "Consider testing with minimal budget (£10/day) first. If results aren't promising after 3 days, pivot to a different product."

    return {
        "product_id": product.get("id"),
        "product_name": product.get("product_name", ""),
        "simulation": {
            "profit_per_sale": profit_per_sale,
            "estimated_cvr": cvr,
            "estimated_cpc": cpc,
            "estimated_cpa": cpa,
            "breakeven_ad_cost": breakeven_ad_cost,
            "daily_sales_range": {"low": daily_sales_low, "high": daily_sales_high},
            "daily_profit_range": {"low": daily_profit_low, "high": daily_profit_high},
            "breakeven_days": breakeven_days,
            "assumed_daily_budget": daily_budget,
        },
        "potential": potential,
        "potential_description": potential_desc,
        "risks": risks,
        "guidance": guidance,
        "inputs_used": {
            "launch_score": launch_score,
            "trend_stage": trend_stage,
            "competition": competition,
            "supplier_cost": supplier_cost,
            "sell_price": sell_price,
            "ad_count": ad_count,
        },
        "simulated_at": datetime.now(timezone.utc).isoformat(),
    }
