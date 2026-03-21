"""
All product scoring/calculation pure functions.
"""
import uuid
import random
from datetime import datetime, timezone
from typing import Optional


def calculate_trend_score(product: dict) -> int:
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    supplier_cost = product.get('supplier_cost', 0)
    retail_price = product.get('estimated_retail_price', 0)
    margin = retail_price - supplier_cost
    if tiktok_views >= 50000000:
        tiktok_score = 100
    elif tiktok_views >= 10000000:
        tiktok_score = 80
    elif tiktok_views >= 1000000:
        tiktok_score = 60
    elif tiktok_views >= 100000:
        tiktok_score = 40
    else:
        tiktok_score = min(40, (tiktok_views / 100000) * 40)
    if ad_count == 0:
        ad_score = 30
    elif ad_count < 50:
        ad_score = 60
    elif ad_count < 200:
        ad_score = 100
    elif ad_count < 500:
        ad_score = 70
    else:
        ad_score = 40
    competition_scores = {'low': 100, 'medium': 60, 'high': 30}
    competition_score = competition_scores.get(competition_level, 50)
    if margin >= 50:
        margin_score = 100
    elif margin >= 25:
        margin_score = 80
    elif margin >= 10:
        margin_score = 60
    elif margin > 0:
        margin_score = 40
    else:
        margin_score = 0
    weighted_score = (
        tiktok_score * 0.35 +
        ad_score * 0.20 +
        competition_score * 0.20 +
        margin_score * 0.25
    )
    return min(100, max(0, round(weighted_score)))


def calculate_trend_stage(product: dict) -> str:
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    signals = {'early': 0, 'rising': 0, 'peak': 0, 'saturated': 0}
    if tiktok_views >= 30000000:
        signals['peak'] += 40
    elif tiktok_views >= 5000000:
        signals['rising'] += 40
    elif tiktok_views >= 500000:
        signals['rising'] += 40
    else:
        signals['early'] += 40
    if ad_count >= 400:
        signals['saturated'] += 35
    elif ad_count >= 200:
        signals['peak'] += 35
    elif ad_count >= 50:
        signals['rising'] += 35
    else:
        signals['early'] += 35
    if competition_level == 'high':
        signals['saturated'] += 25
    elif competition_level == 'medium':
        signals['rising'] += 25
    else:
        signals['early'] += 25
    return max(signals, key=signals.get)


def calculate_opportunity_rating(product: dict) -> str:
    trend_score = product.get('trend_score', 0)
    supplier_cost = product.get('supplier_cost', 0)
    retail_price = product.get('estimated_retail_price', 0)
    competition_level = product.get('competition_level', 'medium')
    trend_stage = product.get('trend_stage', 'rising')
    margin = retail_price - supplier_cost
    margin_percent = (margin / retail_price * 100) if retail_price > 0 else 0
    score = 0
    score += (trend_score / 100) * 40
    margin_score = 0
    if margin >= 50:
        margin_score += 50
    elif margin >= 25:
        margin_score += 40
    elif margin >= 15:
        margin_score += 30
    else:
        margin_score += 20
    if margin_percent >= 70:
        margin_score += 50
    elif margin_percent >= 50:
        margin_score += 40
    elif margin_percent >= 30:
        margin_score += 30
    else:
        margin_score += 20
    score += (margin_score / 100) * 25
    comp_scores = {'low': 100, 'medium': 60, 'high': 25}
    score += (comp_scores.get(competition_level, 50) / 100) * 20
    stage_scores = {'early': 100, 'rising': 85, 'peak': 50, 'saturated': 15}
    score += (stage_scores.get(trend_stage, 50) / 100) * 15
    if trend_score >= 80 and competition_level == 'low' and trend_stage == 'early':
        score += 10
    if trend_stage == 'rising' and margin_percent >= 50:
        score += 5
    if trend_stage == 'saturated' and competition_level == 'high':
        score -= 10
    score = min(100, max(0, score))
    if score >= 85:
        return 'very high'
    elif score >= 70:
        return 'high'
    elif score >= 50:
        return 'medium'
    return 'low'


def generate_ai_summary(product: dict) -> str:
    opportunity = product.get('opportunity_rating', 'medium')
    trend_score = product.get('trend_score', 50)
    competition = product.get('competition_level', 'medium')
    category = product.get('category', 'General')
    margin = product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)
    early_trend_label = product.get('early_trend_label', 'stable')
    early_trend_context = ""
    if early_trend_label == 'exploding':
        early_trend_context = "EXPLODING - Extremely rapid growth detected. "
    elif early_trend_label == 'rising':
        early_trend_context = "Rising fast with strong momentum. "
    elif early_trend_label == 'early_trend':
        early_trend_context = "Early trend indicators detected. "
    templates = {
        'very high': f"{early_trend_context}Exceptional viral potential with {competition} current competition. Strong TikTok presence driving consumer awareness. Perfect for content creators and lifestyle consumers. Act fast before market saturation.",
        'high': f"{early_trend_context}Solid opportunity with growing demand. {'Strong' if trend_score >= 80 else 'Building'} TikTok presence. {'Low advertiser activity creates favorable entry conditions.' if competition == 'low' else 'Moderate competition requires clear value proposition.'} Good time to test with controlled ad spend.",
        'medium': f"{early_trend_context}Moderate opportunity requiring differentiation. {'Market is getting competitive' if competition == 'high' else 'Some competition present'}. {'Moderate margins provide room for competitive pricing.' if margin >= 15 else 'Thin margins demand high volume strategy.'} Proceed with caution.",
        'low': f"Challenging market conditions. {'Crowded market demands strong differentiation.' if competition == 'high' else 'Limited market validation.'} Consider alternative products or unique angle.",
    }
    base = templates.get(opportunity, templates['medium'])
    category_insights = {
        'Electronics': 'Tech products benefit from early review content.',
        'Home Decor': 'Visual content performs well in this category.',
        'Fashion': 'Influencer seeding highly effective.',
        'Health & Fitness': 'Before/after content drives sales.',
    }
    insight = category_insights.get(category, '')
    return f"{base} {insight}".strip()


def calculate_early_trend_score(product: dict) -> tuple:
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    view_growth_rate = product.get('view_growth_rate', 0)
    engagement_rate = product.get('engagement_rate', 0)
    supplier_order_velocity = product.get('supplier_order_velocity', 0)
    trend_stage = product.get('trend_stage', 'rising')
    if view_growth_rate >= 200:
        growth_score = 100
    elif view_growth_rate >= 100:
        growth_score = 85
    elif view_growth_rate >= 50:
        growth_score = 70
    elif view_growth_rate >= 25:
        growth_score = 55
    elif view_growth_rate >= 10:
        growth_score = 40
    else:
        growth_score = max(0, view_growth_rate * 4)
    if engagement_rate >= 15:
        engagement_score = 100
    elif engagement_rate >= 10:
        engagement_score = 85
    elif engagement_rate >= 5:
        engagement_score = 65
    elif engagement_rate >= 2:
        engagement_score = 45
    else:
        engagement_score = engagement_rate * 22.5
    if supplier_order_velocity >= 500:
        supplier_score = 100
    elif supplier_order_velocity >= 200:
        supplier_score = 85
    elif supplier_order_velocity >= 100:
        supplier_score = 70
    elif supplier_order_velocity >= 50:
        supplier_score = 55
    elif supplier_order_velocity >= 20:
        supplier_score = 40
    else:
        supplier_score = supplier_order_velocity * 2
    if ad_count == 0:
        ad_activity_score = 60
    elif ad_count < 30:
        ad_activity_score = 100
    elif ad_count < 80:
        ad_activity_score = 90
    elif ad_count < 150:
        ad_activity_score = 70
    elif ad_count < 300:
        ad_activity_score = 45
    else:
        ad_activity_score = 20
    competition_scores = {'low': 100, 'medium': 55, 'high': 15}
    competition_score = competition_scores.get(competition_level, 50)
    stage_bonus = 0
    if trend_stage == 'early' and tiktok_views >= 100000:
        stage_bonus = 10
    elif trend_stage == 'rising' and ad_count < 100:
        stage_bonus = 5
    early_trend_score = (
        growth_score * 0.25 +
        engagement_score * 0.20 +
        supplier_score * 0.20 +
        ad_activity_score * 0.20 +
        competition_score * 0.15 +
        stage_bonus
    )
    early_trend_score = min(100, max(0, round(early_trend_score)))
    if early_trend_score >= 85:
        label = 'exploding'
    elif early_trend_score >= 65:
        label = 'rising'
    elif early_trend_score >= 45:
        label = 'early_trend'
    else:
        label = 'stable'
    return early_trend_score, label


def should_generate_early_trend_alert(product: dict) -> bool:
    early_trend_score = product.get('early_trend_score', 0)
    early_trend_label = product.get('early_trend_label', 'stable')
    return early_trend_score >= 70 or early_trend_label in ['exploding', 'rising']


def calculate_market_score(product: dict) -> tuple:
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    estimated_margin = product.get('estimated_margin', 0)
    estimated_retail_price = product.get('estimated_retail_price', 0)
    trend_score = product.get('trend_score', 0)
    early_trend_score = product.get('early_trend_score', 0)
    active_competitor_stores = product.get('active_competitor_stores', 0)
    market_saturation = product.get('market_saturation', 0)
    margin_percent = (estimated_margin / estimated_retail_price * 100) if estimated_retail_price > 0 else 0
    demand_signals = 0
    if tiktok_views >= 50000000:
        views_score = 100
    elif tiktok_views >= 10000000:
        views_score = 85
    elif tiktok_views >= 1000000:
        views_score = 70
    elif tiktok_views >= 100000:
        views_score = 50
    else:
        views_score = min(50, (tiktok_views / 100000) * 50)
    demand_signals += views_score * 0.40
    combined_trend = (trend_score + early_trend_score) / 2
    demand_signals += combined_trend * 0.40
    if ad_count == 0:
        ad_demand_score = 30
    elif ad_count < 50:
        ad_demand_score = 70
    elif ad_count < 150:
        ad_demand_score = 100
    elif ad_count < 300:
        ad_demand_score = 80
    else:
        ad_demand_score = 60
    demand_signals += ad_demand_score * 0.20
    demand_score = min(100, demand_signals)
    margin_signals = 0
    if estimated_margin >= 40:
        abs_margin_score = 100
    elif estimated_margin >= 30:
        abs_margin_score = 85
    elif estimated_margin >= 20:
        abs_margin_score = 70
    elif estimated_margin >= 15:
        abs_margin_score = 55
    elif estimated_margin >= 10:
        abs_margin_score = 40
    else:
        abs_margin_score = max(0, estimated_margin * 4)
    margin_signals += abs_margin_score * 0.60
    if margin_percent >= 70:
        pct_margin_score = 100
    elif margin_percent >= 50:
        pct_margin_score = 85
    elif margin_percent >= 35:
        pct_margin_score = 70
    elif margin_percent >= 25:
        pct_margin_score = 55
    else:
        pct_margin_score = max(0, margin_percent * 2.2)
    margin_signals += pct_margin_score * 0.40
    margin_score_val = min(100, margin_signals)
    competition_signals = 0
    if active_competitor_stores == 0:
        stores_score = 90
    elif active_competitor_stores < 10:
        stores_score = 100
    elif active_competitor_stores < 30:
        stores_score = 75
    elif active_competitor_stores < 60:
        stores_score = 50
    elif active_competitor_stores < 100:
        stores_score = 30
    else:
        stores_score = 15
    competition_signals += stores_score * 0.40
    comp_level_scores = {'low': 100, 'medium': 60, 'high': 25}
    competition_signals += comp_level_scores.get(competition_level, 50) * 0.30
    saturation_score = max(0, 100 - market_saturation)
    competition_signals += saturation_score * 0.30
    competition_score_val = min(100, competition_signals)
    market_score = (
        demand_score * 0.35 +
        margin_score_val * 0.35 +
        competition_score_val * 0.30
    )
    market_score = min(100, max(0, round(market_score)))
    if market_score >= 80:
        market_label = 'high'
    elif market_score >= 60:
        market_label = 'medium'
    elif market_score >= 40:
        market_label = 'low'
    else:
        market_label = 'very_low'
    score_breakdown = {
        'demand': round(demand_score),
        'margin': round(margin_score_val),
        'competition': round(competition_score_val),
        'ad_activity': ad_demand_score,
    }
    return market_score, market_label, score_breakdown


def calculate_launch_score(product: dict) -> tuple:
    trend_score = product.get('trend_score', 0)
    margin_score = product.get('margin_score', 0)
    competition_score = product.get('competition_score', 0)
    ad_activity_score = product.get('ad_activity_score', 0)
    supplier_demand_score = product.get('supplier_demand_score', 0)

    # Competition penalty: heavy ad activity should reduce opportunity
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    market_saturation = product.get('market_saturation', 0)
    active_stores = product.get('active_competitor_stores', 0)

    # Calculate saturation penalty (0 to 25 points deducted)
    saturation_penalty = 0
    if competition_level == 'high':
        saturation_penalty += 8
    if ad_count > 200:
        saturation_penalty += min(12, (ad_count - 200) / 50 * 3)
    if market_saturation > 60:
        saturation_penalty += min(5, (market_saturation - 60) / 10 * 2)
    if active_stores > 50:
        saturation_penalty += min(5, (active_stores - 50) / 30 * 3)

    # Convert ad_activity_score to an opportunity score
    # High ad activity validates demand BUT reduces opportunity
    if ad_count > 300:
        ad_opportunity = max(15, ad_activity_score * 0.3)
    elif ad_count > 150:
        ad_opportunity = max(25, ad_activity_score * 0.5)
    elif ad_count > 50:
        ad_opportunity = ad_activity_score * 0.75
    else:
        ad_opportunity = ad_activity_score

    launch_score = (
        trend_score * 0.30 +
        margin_score * 0.25 +
        competition_score * 0.20 +
        ad_opportunity * 0.15 +
        supplier_demand_score * 0.10
    ) - saturation_penalty

    launch_score = min(100, max(0, round(launch_score)))
    if launch_score >= 80:
        label = 'strong_launch'
    elif launch_score >= 60:
        label = 'promising'
    elif launch_score >= 40:
        label = 'risky'
    else:
        label = 'avoid'
    reasoning_parts = []
    scores = {
        'Trend momentum': trend_score,
        'Profit margins': margin_score,
        'Market accessibility': competition_score,
        'Ad opportunity': round(ad_opportunity),
        'Supplier reliability': supplier_demand_score
    }
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    strengths = [name for name, score in sorted_scores[:2] if score >= 60]
    weaknesses = [name for name, score in sorted_scores if score < 40]
    if strengths:
        reasoning_parts.append(f"Strong: {', '.join(strengths)}")
    if weaknesses and label in ['risky', 'avoid']:
        reasoning_parts.append(f"Weak: {', '.join(weaknesses[:2])}")
    if saturation_penalty > 10:
        reasoning_parts.append(f"Heavy competition penalty (-{round(saturation_penalty)}pts)")
    elif saturation_penalty > 5:
        reasoning_parts.append(f"Moderate competition drag (-{round(saturation_penalty)}pts)")
    if label == 'strong_launch':
        reasoning_parts.append("Excellent conditions for launch")
    elif label == 'promising':
        reasoning_parts.append("Good potential with manageable risks")
    elif label == 'risky':
        reasoning_parts.append("Proceed with caution - test small first")
    else:
        reasoning_parts.append("High risk - consider alternatives")
    reasoning = ". ".join(reasoning_parts) if reasoning_parts else "Insufficient data for analysis"
    return launch_score, label, reasoning


def generate_mock_competitor_data(product: dict) -> dict:
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    estimated_retail_price = product.get('estimated_retail_price', 0)
    supplier_cost = product.get('supplier_cost', 0)
    base_stores = {
        'low': random.randint(3, 15),
        'medium': random.randint(15, 45),
        'high': random.randint(45, 120),
    }
    active_stores = base_stores.get(competition_level, 25)
    if ad_count > 200:
        active_stores = int(active_stores * 1.5)
    elif ad_count < 30:
        active_stores = int(active_stores * 0.6)
    price_variation = estimated_retail_price * 0.25
    min_price = max(supplier_cost + 5, estimated_retail_price - price_variation)
    max_price = estimated_retail_price + price_variation
    avg_price = estimated_retail_price + random.uniform(-5, 10)
    saturation_base = {
        'low': random.randint(15, 35),
        'medium': random.randint(35, 60),
        'high': random.randint(60, 90),
    }
    market_saturation = saturation_base.get(competition_level, 45)
    trend_stage = product.get('trend_stage', 'rising')
    if trend_stage == 'saturated':
        market_saturation = min(95, market_saturation + 20)
    elif trend_stage == 'early':
        market_saturation = max(10, market_saturation - 20)
    estimated_monthly_ad_spend = ad_count * random.randint(80, 200)
    store_name_prefixes = ['Quick', 'Best', 'Top', 'Premium', 'Smart', 'Value', 'Direct', 'Pro', 'Elite', 'Super']
    store_name_suffixes = ['Shop', 'Store', 'Market', 'Deals', 'Hub', 'Zone', 'Express', 'Outlet', 'Central', 'Direct']
    competitor_stores = []
    num_visible_stores = min(10, active_stores)
    for i in range(num_visible_stores):
        store_price = round(random.uniform(min_price, max_price), 2)
        has_ads = random.random() < 0.6
        competitor_stores.append({
            'id': f'comp_{product.get("id", "unknown")}_{i}',
            'name': f'{random.choice(store_name_prefixes)}{random.choice(store_name_suffixes)}',
            'price': store_price,
            'currency': 'GBP',
            'has_active_ads': has_ads,
            'estimated_monthly_sales': random.randint(10, 200) if has_ads else random.randint(5, 50),
            'rating': round(random.uniform(3.5, 5.0), 1),
            'reviews_count': random.randint(10, 500),
            'last_seen': datetime.now(timezone.utc).isoformat(),
        })
    competitor_stores.sort(key=lambda x: x['price'])
    return {
        'active_competitor_stores': active_stores,
        'avg_selling_price': round(avg_price, 2),
        'price_range': {'min': round(min_price, 2), 'max': round(max_price, 2)},
        'estimated_monthly_ad_spend': estimated_monthly_ad_spend,
        'market_saturation': market_saturation,
        'competitor_stores': competitor_stores,
        'data_freshness': datetime.now(timezone.utc).isoformat(),
        'data_source': 'simulated',
    }


def calculate_success_probability(product: dict) -> tuple:
    stores_created = product.get('stores_created', 0)
    exports_count = product.get('exports_count', 0)
    success_signals = product.get('success_signals', 0)
    trend_score = product.get('trend_score', 0)
    early_trend_score = product.get('early_trend_score', 0)
    estimated_margin = product.get('estimated_margin', 0)
    if stores_created >= 20:
        stores_score = 100
    elif stores_created >= 10:
        stores_score = 90
    elif stores_created >= 5:
        stores_score = 75
    elif stores_created >= 3:
        stores_score = 60
    elif stores_created >= 1:
        stores_score = 40
    else:
        stores_score = 0
    if exports_count >= 15:
        export_score = 100
    elif exports_count >= 8:
        export_score = 85
    elif exports_count >= 4:
        export_score = 70
    elif exports_count >= 2:
        export_score = 50
    elif exports_count >= 1:
        export_score = 30
    else:
        export_score = 0
    if success_signals >= 100:
        success_score = 100
    elif success_signals >= 50:
        success_score = 85
    elif success_signals >= 20:
        success_score = 70
    elif success_signals >= 10:
        success_score = 55
    elif success_signals >= 5:
        success_score = 40
    else:
        success_score = success_signals * 8
    combined_trend = (trend_score + early_trend_score) / 2
    trend_metrics_score = min(100, combined_trend)
    if estimated_margin >= 40:
        margin_score = 100
    elif estimated_margin >= 30:
        margin_score = 85
    elif estimated_margin >= 20:
        margin_score = 70
    elif estimated_margin >= 15:
        margin_score = 55
    elif estimated_margin >= 10:
        margin_score = 40
    else:
        margin_score = max(0, estimated_margin * 4)
    success_probability = (
        stores_score * 0.30 +
        export_score * 0.20 +
        success_score * 0.20 +
        trend_metrics_score * 0.15 +
        margin_score * 0.15
    )
    success_probability = min(100, max(0, round(success_probability)))
    user_engagement_score = round(
        (stores_created * 10 + exports_count * 5 + success_signals * 2) / 3, 1
    )
    proven_winner = (
        success_probability >= 70 and
        stores_created >= 3 and
        (exports_count >= 2 or success_signals >= 10)
    )
    return success_probability, proven_winner, user_engagement_score


def should_generate_alert(product: dict) -> bool:
    trend_score = product.get('trend_score', 0)
    opportunity = product.get('opportunity_rating', 'low')
    return trend_score >= 75 and opportunity in ['high', 'very high']


def generate_alert(product: dict) -> Optional[dict]:
    if not should_generate_alert(product):
        return None
    trend_stage = product.get('trend_stage', 'rising')
    trend_score = product.get('trend_score', 0)
    opportunity = product.get('opportunity_rating', 'medium')
    margin = product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)
    if trend_stage == 'early' and trend_score >= 80:
        alert_type = 'early_stage'
        title = f"Early Stage Winner: {product.get('product_name')}"
    elif trend_stage == 'rising':
        alert_type = 'rising_trend'
        title = f"Rising Trend Alert: {product.get('product_name')}"
    elif margin >= 40:
        alert_type = 'high_margin'
        title = f"High Margin Opportunity: {product.get('product_name')}"
    else:
        alert_type = 'new_opportunity'
        title = f"New Opportunity: {product.get('product_name')}"
    if trend_score >= 90 and opportunity == 'very high':
        priority = 'critical'
    elif trend_score >= 80:
        priority = 'high'
    else:
        priority = 'medium'
    return {
        'id': str(uuid.uuid4()),
        'product_id': product.get('id'),
        'product_name': product.get('product_name'),
        'alert_type': alert_type,
        'priority': priority,
        'title': title,
        'body': f"Detected product with {trend_score} trend score and {opportunity} opportunity rating.",
        'trend_score': trend_score,
        'opportunity_rating': opportunity,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'read': False,
        'dismissed': False,
    }


def generate_early_trend_alert(product: dict) -> Optional[dict]:
    if not should_generate_early_trend_alert(product):
        return None
    early_trend_score = product.get('early_trend_score', 0)
    early_trend_label = product.get('early_trend_label', 'stable')
    view_growth_rate = product.get('view_growth_rate', 0)
    engagement_rate = product.get('engagement_rate', 0)
    if early_trend_label == 'exploding':
        alert_type = 'exploding_trend'
        title = f"EXPLODING: {product.get('product_name')}"
        priority = 'critical'
    elif early_trend_label == 'rising':
        alert_type = 'rising_early_trend'
        title = f"Rising Fast: {product.get('product_name')}"
        priority = 'high'
    else:
        alert_type = 'early_trend_detected'
        title = f"Early Trend: {product.get('product_name')}"
        priority = 'medium'
    body_parts = []
    if view_growth_rate >= 50:
        body_parts.append(f"{view_growth_rate:.0f}% view growth")
    if engagement_rate >= 5:
        body_parts.append(f"{engagement_rate:.1f}% engagement")
    body_parts.append(f"Early trend score: {early_trend_score}")
    return {
        'id': str(uuid.uuid4()),
        'product_id': product.get('id'),
        'product_name': product.get('product_name'),
        'alert_type': alert_type,
        'priority': priority,
        'title': title,
        'body': f"Early trend signals detected. {' | '.join(body_parts)}. Act before competition increases.",
        'trend_score': product.get('trend_score', 0),
        'early_trend_score': early_trend_score,
        'early_trend_label': early_trend_label,
        'opportunity_rating': product.get('opportunity_rating', 'medium'),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'read': False,
        'dismissed': False,
    }


def run_full_automation(product: dict) -> dict:
    trend_stage = calculate_trend_stage(product)
    product['trend_stage'] = trend_stage
    trend_score = calculate_trend_score(product)
    product['trend_score'] = trend_score
    opportunity_rating = calculate_opportunity_rating(product)
    product['opportunity_rating'] = opportunity_rating
    early_trend_score_val, early_trend_label = calculate_early_trend_score(product)
    product['early_trend_score'] = early_trend_score_val
    product['early_trend_label'] = early_trend_label
    ai_summary = generate_ai_summary(product)
    product['ai_summary'] = ai_summary
    margin = product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)
    product['estimated_margin'] = margin
    competitor_data = generate_mock_competitor_data(product)
    product['active_competitor_stores'] = competitor_data['active_competitor_stores']
    product['avg_selling_price'] = competitor_data['avg_selling_price']
    product['price_range'] = competitor_data['price_range']
    product['estimated_monthly_ad_spend'] = competitor_data['estimated_monthly_ad_spend']
    product['market_saturation'] = competitor_data['market_saturation']
    market_score, market_label, score_breakdown = calculate_market_score(product)
    product['market_score'] = market_score
    product['market_label'] = market_label
    product['market_score_breakdown'] = score_breakdown
    launch_score, launch_label, launch_reasoning = calculate_launch_score(product)
    product['launch_score'] = launch_score
    product['launch_score_label'] = launch_label
    product['launch_score_reasoning'] = launch_reasoning
    product['updated_at'] = datetime.now(timezone.utc).isoformat()
    alert = generate_alert(product)
    early_alert = generate_early_trend_alert(product)
    return {'product': product, 'alert': alert, 'early_alert': early_alert}


# ── Score Normalisation ──────────────────────────────────────

def get_canonical_score(product: dict) -> int:
    """Single source of truth: launch_score > viability_score > trend_score > 0."""
    return product.get("launch_score") or product.get("viability_score") or product.get("trend_score") or 0


def normalise_product_scores(product: dict) -> dict:
    """Ensure viability_score and launch_score are always in sync."""
    score = get_canonical_score(product)
    return {**product, "viability_score": score, "launch_score": score}


def score_label(score: int) -> str:
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    if score >= 40: return "Fair"
    if score >= 20: return "Weak"
    return "Poor"

