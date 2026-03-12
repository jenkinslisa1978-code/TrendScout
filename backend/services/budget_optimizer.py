"""
Smart Budget Optimizer V1 — Rule-Based Recommendation Engine

Analyzes ad test variation results and generates actionable recommendations:
  - increase_budget / maintain / pause / kill / needs_more_data
  - confidence score based on data volume and signal agreement
  - recommended next budget with scaling logic
  - reasoning and warning flags
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# ── Benchmarks ──
BENCHMARKS = {
    "ctr_excellent": 2.5,
    "ctr_good": 1.8,
    "ctr_poor": 1.0,
    "cpc_good": 0.50,
    "cpc_poor": 1.50,
    "atc_good": 8.0,
    "atc_poor": 3.0,
    "min_spend": 10,
    "min_clicks": 30,
}

# ── Budget scaling tiers (conservative 20-40% increments) ──
SCALE_MAP = {
    10: 15, 15: 20, 20: 25, 25: 35, 35: 50,
    50: 70, 70: 100, 100: 140,
}


def _next_budget(current: float, aggressive: bool = False) -> float:
    """Conservative budget scaling — 20-40% increments."""
    for threshold, target in sorted(SCALE_MAP.items()):
        if current <= threshold:
            return target if not aggressive else round(target * 1.2)
    # Default: +30%
    return round(current * 1.3, 2)


def _compute_confidence(metrics: Dict[str, float]) -> float:
    """
    Confidence depends on: spend volume, click volume, purchase volume,
    and whether signals agree with each other.
    """
    spend = metrics.get("spend", 0)
    clicks = metrics.get("clicks", 0)
    purchases = metrics.get("purchases", 0)
    ctr = metrics.get("ctr", 0)

    score = 0.0

    # Spend volume (more spend = more confidence)
    if spend >= 30:
        score += 0.25
    elif spend >= 15:
        score += 0.15
    elif spend >= 10:
        score += 0.08

    # Click volume
    if clicks >= 100:
        score += 0.25
    elif clicks >= 50:
        score += 0.18
    elif clicks >= 30:
        score += 0.10

    # Purchase volume
    if purchases >= 5:
        score += 0.20
    elif purchases >= 2:
        score += 0.12
    elif purchases >= 1:
        score += 0.06

    # Signal agreement bonus
    signals_positive = 0
    signals_negative = 0

    if ctr >= BENCHMARKS["ctr_good"]:
        signals_positive += 1
    elif ctr < BENCHMARKS["ctr_poor"]:
        signals_negative += 1

    cpc = metrics.get("cpc", 0)
    if cpc > 0:
        if cpc <= BENCHMARKS["cpc_good"]:
            signals_positive += 1
        elif cpc >= BENCHMARKS["cpc_poor"]:
            signals_negative += 1

    atc_rate = metrics.get("atc_rate", 0)
    if atc_rate >= BENCHMARKS["atc_good"]:
        signals_positive += 1
    elif atc_rate < BENCHMARKS["atc_poor"] and atc_rate > 0:
        signals_negative += 1

    if purchases > 0:
        signals_positive += 1

    # Agreement bonus: all signals pointing same direction
    total_signals = signals_positive + signals_negative
    if total_signals >= 3:
        agreement = max(signals_positive, signals_negative) / total_signals
        score += agreement * 0.30
    elif total_signals >= 2:
        agreement = max(signals_positive, signals_negative) / total_signals
        score += agreement * 0.15

    return round(min(score, 0.99), 2)


def recommend_for_variation(
    variation: Dict[str, Any],
    target_cpa: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Generate a recommendation for a single ad variation.

    Returns:
        action: increase_budget | maintain | pause | kill | needs_more_data
        confidence: 0-1
        recommended_budget: float
        reasoning: list of strings
        flags: list of warning strings
    """
    r = variation.get("results", {})
    spend = r.get("spend", 0)
    clicks = r.get("clicks", 0)
    ctr = r.get("ctr", 0)
    add_to_cart = r.get("add_to_cart", 0)
    purchases = r.get("purchases", 0)

    # Derived metrics
    cpc = round(spend / max(clicks, 1), 2) if clicks > 0 else 0
    atc_rate = round(add_to_cart / max(clicks, 1) * 100, 2) if clicks > 0 else 0
    cpa = round(spend / max(purchases, 1), 2) if purchases > 0 else 0

    metrics = {"spend": spend, "clicks": clicks, "ctr": ctr, "cpc": cpc,
               "atc_rate": atc_rate, "purchases": purchases, "cpa": cpa}

    confidence = _compute_confidence(metrics)
    reasoning = []
    flags = []
    current_budget = spend  # approximate current budget from spend

    # ── Rule 1: Minimum data threshold ──
    if spend < BENCHMARKS["min_spend"] or clicks < BENCHMARKS["min_clicks"]:
        return {
            "variation_id": variation.get("variation_id", ""),
            "label": variation.get("label", ""),
            "hook_type": variation.get("hook_type", ""),
            "action": "needs_more_data",
            "confidence": round(min(confidence, 0.30), 2),
            "current_budget": current_budget,
            "recommended_budget": current_budget,
            "reasoning": [
                f"Spend £{spend} (need £{BENCHMARKS['min_spend']}+)",
                f"{clicks} clicks (need {BENCHMARKS['min_clicks']}+)",
                "Keep running to collect enough data",
            ],
            "flags": ["Insufficient data for reliable recommendation"],
            "metrics": metrics,
        }

    # ── Rule 2: KILL ──
    kill = False
    if ctr < BENCHMARKS["ctr_poor"] and spend >= BENCHMARKS["min_spend"]:
        reasoning.append(f"CTR {ctr}% is below {BENCHMARKS['ctr_poor']}% threshold")
        kill = True
    if cpc > 0 and cpc >= BENCHMARKS["cpc_poor"] and add_to_cart == 0:
        reasoning.append(f"CPC £{cpc} too high with zero add-to-carts")
        kill = True
    if add_to_cart > 0 and purchases == 0 and spend >= 20:
        reasoning.append(f"{add_to_cart} add-to-carts but 0 purchases after £{spend} spend")
        kill = True

    if kill and len(reasoning) >= 2:
        return {
            "variation_id": variation.get("variation_id", ""),
            "label": variation.get("label", ""),
            "hook_type": variation.get("hook_type", ""),
            "action": "kill",
            "confidence": confidence,
            "current_budget": current_budget,
            "recommended_budget": 0,
            "reasoning": reasoning,
            "flags": ["Recommend stopping this ad to save budget"],
            "metrics": metrics,
        }

    # ── Rule 3: PAUSE ──
    pause = False
    pause_reasons = []
    if BENCHMARKS["ctr_poor"] <= ctr < BENCHMARKS["ctr_good"]:
        pause_reasons.append(f"CTR {ctr}% is below good benchmark ({BENCHMARKS['ctr_good']}%)")
        pause = True
    if 0 < atc_rate < BENCHMARKS["atc_poor"]:
        pause_reasons.append(f"ATC rate {atc_rate}% is weak (below {BENCHMARKS['atc_poor']}%)")
        pause = True
    if target_cpa and cpa > target_cpa and cpa < target_cpa * 2:
        pause_reasons.append(f"CPA £{cpa} above target £{target_cpa} but not disastrous")
        pause = True

    if pause and not kill:
        return {
            "variation_id": variation.get("variation_id", ""),
            "label": variation.get("label", ""),
            "hook_type": variation.get("hook_type", ""),
            "action": "pause",
            "confidence": confidence,
            "current_budget": current_budget,
            "recommended_budget": 0,
            "reasoning": pause_reasons,
            "flags": ["Consider pausing to reallocate budget to better performers"],
            "metrics": metrics,
        }

    # ── Rule 4: INCREASE BUDGET ──
    increase = False
    increase_reasons = []
    if ctr >= BENCHMARKS["ctr_excellent"]:
        increase_reasons.append(f"CTR {ctr}% is excellent (above {BENCHMARKS['ctr_excellent']}%)")
        increase = True
    if target_cpa and cpa > 0 and cpa < target_cpa:
        increase_reasons.append(f"CPA £{cpa} is below target £{target_cpa}")
        increase = True
    if purchases >= 2:
        increase_reasons.append(f"{purchases} purchases — conversion is proven")
        increase = True

    if increase and len(increase_reasons) >= 2:
        aggressive = ctr >= 3.5 and purchases >= 3
        next_budget = _next_budget(current_budget, aggressive=aggressive)
        return {
            "variation_id": variation.get("variation_id", ""),
            "label": variation.get("label", ""),
            "hook_type": variation.get("hook_type", ""),
            "action": "increase_budget",
            "confidence": confidence,
            "current_budget": current_budget,
            "recommended_budget": next_budget,
            "reasoning": increase_reasons,
            "flags": [],
            "metrics": metrics,
        }

    # ── Rule 5: MAINTAIN ──
    maintain_reasons = []
    if ctr >= BENCHMARKS["ctr_good"]:
        maintain_reasons.append(f"CTR {ctr}% is decent")
    if cpc <= BENCHMARKS["cpc_good"]:
        maintain_reasons.append(f"CPC £{cpc} is within range")
    if purchases > 0:
        maintain_reasons.append(f"{purchases} purchase(s) — signal is present but not strong enough to scale")
    if not maintain_reasons:
        maintain_reasons.append("Mixed signals — not enough clarity to act")

    return {
        "variation_id": variation.get("variation_id", ""),
        "label": variation.get("label", ""),
        "hook_type": variation.get("hook_type", ""),
        "action": "maintain",
        "confidence": confidence,
        "current_budget": current_budget,
        "recommended_budget": current_budget,
        "reasoning": maintain_reasons,
        "flags": ["Keep running and monitor for clearer signals"],
        "metrics": metrics,
    }


def recommend_for_test(test: Dict[str, Any], target_cpa: Optional[float] = None) -> Dict[str, Any]:
    """Generate recommendations for all variations in an ad test."""
    recommendations = []
    for v in test.get("variations", []):
        rec = recommend_for_variation(v, target_cpa)
        recommendations.append(rec)

    # Summary
    actions = [r["action"] for r in recommendations]
    to_scale = [r for r in recommendations if r["action"] == "increase_budget"]
    to_pause = [r for r in recommendations if r["action"] in ("pause", "kill")]
    waiting = [r for r in recommendations if r["action"] == "needs_more_data"]

    summary = {
        "test_id": test.get("id", ""),
        "total_variations": len(recommendations),
        "to_scale": len(to_scale),
        "to_pause": len(to_pause),
        "to_maintain": len([r for r in recommendations if r["action"] == "maintain"]),
        "waiting_data": len(waiting),
        "top_performer": None,
        "overall_status": "collecting_data",
    }

    # Find top performer
    with_data = [r for r in recommendations if r["action"] != "needs_more_data"]
    if with_data:
        best = max(with_data, key=lambda x: x["metrics"].get("ctr", 0))
        summary["top_performer"] = {"label": best["label"], "hook_type": best["hook_type"],
                                     "ctr": best["metrics"]["ctr"], "action": best["action"]}

    if to_scale:
        summary["overall_status"] = "scaling"
    elif to_pause and not to_scale:
        summary["overall_status"] = "struggling"
    elif waiting and len(waiting) == len(recommendations):
        summary["overall_status"] = "collecting_data"
    else:
        summary["overall_status"] = "monitoring"

    return {
        "recommendations": recommendations,
        "summary": summary,
        "benchmarks": BENCHMARKS,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_dashboard_summary(tests: List[Dict[str, Any]], target_cpa: Optional[float] = None) -> Dict[str, Any]:
    """Generate optimization summary across all active tests."""
    needs_action = []
    candidates_to_scale = []
    losers_to_pause = []
    waiting_data = []

    for test in tests:
        result = recommend_for_test(test, target_cpa)
        for rec in result["recommendations"]:
            entry = {
                "test_id": test.get("id", ""),
                "product_name": test.get("product_name", ""),
                "image_url": test.get("image_url", ""),
                **rec,
            }
            if rec["action"] == "increase_budget":
                candidates_to_scale.append(entry)
            elif rec["action"] in ("pause", "kill"):
                losers_to_pause.append(entry)
            elif rec["action"] == "needs_more_data":
                waiting_data.append(entry)
            else:
                needs_action.append(entry)

    return {
        "candidates_to_scale": candidates_to_scale,
        "losers_to_pause": losers_to_pause,
        "needs_action": needs_action,
        "waiting_data": waiting_data,
        "total_active_tests": len(tests),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
