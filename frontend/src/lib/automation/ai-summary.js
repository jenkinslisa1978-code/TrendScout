/**
 * AI Summary Generation Module
 * 
 * Generates AI-powered product summaries and analysis.
 * 
 * Current implementation: Template-based generation
 * Future: OpenAI API integration, custom ML models
 * 
 * PLACEHOLDER FOR: OpenAI GPT-4/Claude API integration
 */

// Summary templates by opportunity rating
const TEMPLATES = {
  'very high': [
    "Exceptional viral potential with {{competition}} current competition. {{viewsAnalysis}} Perfect for content creators and {{targetAudience}}. {{actionAdvice}}",
    "Strong market opportunity detected. {{viewsAnalysis}} {{marginAnalysis}} {{actionAdvice}}",
    "High-confidence product with {{competition}} barrier to entry. {{marginAnalysis}} {{actionAdvice}}",
  ],
  'high': [
    "Solid opportunity with growing demand. {{viewsAnalysis}} {{competitionAnalysis}} {{marginAnalysis}}",
    "Promising product showing {{stageDescription}} signals. {{marginAnalysis}} {{actionAdvice}}",
    "Good profit potential with {{competition}} competition. {{viewsAnalysis}} Consider {{strategy}}.",
  ],
  'medium': [
    "Moderate opportunity requiring differentiation. {{competitionAnalysis}} {{marginAnalysis}} {{strategy}}",
    "Mixed signals present. {{viewsAnalysis}} {{competitionAnalysis}} Success requires {{strategy}}.",
    "Viable product with caveats. {{marginAnalysis}} {{competitionAnalysis}} Focus on {{strategy}}.",
  ],
  'low': [
    "Challenging market conditions. {{competitionAnalysis}} {{marginAnalysis}} Consider {{strategy}} or explore alternatives.",
    "Limited opportunity due to {{challenges}}. {{actionAdvice}}",
    "Market is {{stageDescription}}. {{competitionAnalysis}} {{actionAdvice}}",
  ],
};

// Component snippets
const SNIPPETS = {
  viewsAnalysis: {
    viral: "TikTok virality confirmed with massive organic reach.",
    trending: "Strong TikTok presence driving consumer awareness.",
    growing: "Emerging TikTok interest suggests growing demand.",
    minimal: "Limited social proof - opportunity for first-mover advantage.",
  },
  competition: {
    low: "low",
    medium: "moderate",
    high: "significant",
  },
  competitionAnalysis: {
    low: "Low advertiser activity creates favorable entry conditions.",
    medium: "Moderate competition requires clear value proposition.",
    high: "Crowded market demands strong differentiation and branding.",
  },
  marginAnalysis: {
    excellent: "Excellent profit margins support aggressive marketing spend.",
    good: "Healthy margins provide room for competitive pricing.",
    moderate: "Moderate margins require efficient operations.",
    thin: "Thin margins demand high volume strategy.",
  },
  stageDescription: {
    early: "early-stage discovery",
    rising: "rising momentum",
    peak: "at peak visibility",
    saturated: "highly saturated",
  },
  targetAudience: [
    "Gen Z consumers",
    "home improvement enthusiasts",
    "fitness-focused buyers",
    "tech early adopters",
    "budget-conscious shoppers",
    "lifestyle content consumers",
  ],
  strategy: [
    "premium branding",
    "bundle offers",
    "niche targeting",
    "influencer partnerships",
    "quality differentiation",
    "fast shipping advantage",
  ],
  actionAdvice: {
    'very high': "Act fast before market saturation.",
    'high': "Good time to test with controlled ad spend.",
    'medium': "Proceed with caution and clear differentiation.",
    'low': "Consider alternative products or unique angle.",
  },
};

/**
 * Generate AI summary for a product
 * @param {Object} product - Full product data
 * @returns {string} Generated AI summary
 */
export function generateAISummary(product) {
  const {
    opportunity_rating = 'medium',
    trend_score = 50,
    trend_stage = 'rising',
    competition_level = 'medium',
    tiktok_views = 0,
    supplier_cost = 0,
    estimated_retail_price = 0,
    category = 'General',
  } = product;

  const margin = estimated_retail_price - supplier_cost;
  const marginPercent = estimated_retail_price > 0 
    ? ((margin / estimated_retail_price) * 100).toFixed(0) 
    : 0;

  // Select random template for variety
  const templates = TEMPLATES[opportunity_rating] || TEMPLATES['medium'];
  const template = templates[Math.floor(Math.random() * templates.length)];

  // Build replacement values
  const replacements = {
    '{{competition}}': SNIPPETS.competition[competition_level],
    '{{viewsAnalysis}}': getViewsAnalysis(tiktok_views),
    '{{competitionAnalysis}}': SNIPPETS.competitionAnalysis[competition_level],
    '{{marginAnalysis}}': getMarginAnalysis(margin, marginPercent),
    '{{stageDescription}}': SNIPPETS.stageDescription[trend_stage],
    '{{targetAudience}}': getRandomItem(SNIPPETS.targetAudience),
    '{{strategy}}': getRandomItem(SNIPPETS.strategy),
    '{{actionAdvice}}': SNIPPETS.actionAdvice[opportunity_rating],
    '{{challenges}}': getChallenges(product),
  };

  // Replace all placeholders
  let summary = template;
  for (const [placeholder, value] of Object.entries(replacements)) {
    summary = summary.replace(new RegExp(placeholder, 'g'), value);
  }

  // Add category-specific insight
  summary += ' ' + getCategoryInsight(category, trend_stage);

  return summary.trim();
}

/**
 * Get views analysis snippet
 */
function getViewsAnalysis(views) {
  if (views >= 30000000) return SNIPPETS.viewsAnalysis.viral;
  if (views >= 5000000) return SNIPPETS.viewsAnalysis.trending;
  if (views >= 500000) return SNIPPETS.viewsAnalysis.growing;
  return SNIPPETS.viewsAnalysis.minimal;
}

/**
 * Get margin analysis snippet
 */
function getMarginAnalysis(margin, marginPercent) {
  if (margin >= 40 || marginPercent >= 60) return SNIPPETS.marginAnalysis.excellent;
  if (margin >= 20 || marginPercent >= 40) return SNIPPETS.marginAnalysis.good;
  if (margin >= 10 || marginPercent >= 25) return SNIPPETS.marginAnalysis.moderate;
  return SNIPPETS.marginAnalysis.thin;
}

/**
 * Get random item from array
 */
function getRandomItem(array) {
  return array[Math.floor(Math.random() * array.length)];
}

/**
 * Get challenges description for low opportunity products
 */
function getChallenges(product) {
  const challenges = [];
  if (product.competition_level === 'high') challenges.push('high competition');
  if (product.trend_stage === 'saturated') challenges.push('market saturation');
  if ((product.estimated_retail_price - product.supplier_cost) < 10) {
    challenges.push('thin margins');
  }
  return challenges.length > 0 ? challenges.join(' and ') : 'market conditions';
}

/**
 * Get category-specific insight
 */
function getCategoryInsight(category, stage) {
  const insights = {
    'Electronics': {
      early: 'Tech products benefit from early review content.',
      rising: 'Consider warranty/support as differentiator.',
      peak: 'Focus on premium positioning or accessories.',
      saturated: 'Bundle with complementary tech items.',
    },
    'Home Decor': {
      early: 'Visual content performs well in this category.',
      rising: 'Lifestyle photography drives conversions.',
      peak: 'Seasonal variations can extend lifecycle.',
      saturated: 'Consider unique color/style variants.',
    },
    'Fashion': {
      early: 'Influencer seeding highly effective.',
      rising: 'Size inclusivity can expand market.',
      peak: 'Limited editions create urgency.',
      saturated: 'Focus on niche style communities.',
    },
    'Health & Fitness': {
      early: 'Before/after content drives sales.',
      rising: 'Fitness influencers provide strong ROI.',
      peak: 'Bundle with complementary products.',
      saturated: 'Target specific fitness niches.',
    },
  };

  const categoryInsights = insights[category];
  if (categoryInsights && categoryInsights[stage]) {
    return categoryInsights[stage];
  }
  return '';
}

/**
 * Batch generate AI summaries
 */
export function batchGenerateAISummaries(products) {
  return products.map(product => ({
    ...product,
    ai_summary: generateAISummary(product),
  }));
}

/**
 * PLACEHOLDER: Future OpenAI integration
 * 
 * This function structure is ready for API integration.
 * Replace the implementation when connecting to OpenAI.
 */
export async function generateAISummaryWithAPI(product, options = {}) {
  const {
    apiKey = process.env.REACT_APP_OPENAI_API_KEY,
    model = 'gpt-4',
    temperature = 0.7,
  } = options;

  // PLACEHOLDER: Currently returns template-based summary
  // Future implementation will call OpenAI API here
  
  if (!apiKey) {
    console.log('[AI Summary] No API key configured, using template generation');
    return generateAISummary(product);
  }

  // TODO: Implement actual OpenAI API call
  // const response = await fetch('https://api.openai.com/v1/chat/completions', {
  //   method: 'POST',
  //   headers: {
  //     'Authorization': `Bearer ${apiKey}`,
  //     'Content-Type': 'application/json',
  //   },
  //   body: JSON.stringify({
  //     model,
  //     temperature,
  //     messages: [
  //       { role: 'system', content: 'You are a dropshipping product analyst...' },
  //       { role: 'user', content: `Analyze this product: ${JSON.stringify(product)}` }
  //     ],
  //   }),
  // });

  return generateAISummary(product);
}
