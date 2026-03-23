/**
 * Page-specific content for prerendering.
 * Each route gets unique title, description, H1, body HTML, schema, and internal links.
 * This content is injected into the HTML shell at build time so crawlers see real content.
 */

const SITE = 'https://trendscout.click';

function faq(items) {
  return `<div class="pr-faq"><h2>Frequently Asked Questions</h2>${items.map(i => `<details><summary><strong>${i.q}</strong></summary><p>${i.a}</p></details>`).join('')}</div>`;
}

function links(items) {
  return `<nav class="pr-links"><h3>Related Pages</h3><ul>${items.map(i => `<li><a href="${i.href}">${i.text}</a></li>`).join('')}</ul></nav>`;
}

function faqSchema(items, url) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map(i => ({
      '@type': 'Question',
      name: i.q,
      acceptedAnswer: { '@type': 'Answer', text: i.a },
    })),
  };
}

function breadcrumb(crumbs) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: crumbs.map((c, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: c.name,
      ...(c.url ? { item: SITE + c.url } : {}),
    })),
  };
}

const orgSchema = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'TrendScout',
  url: SITE,
  logo: SITE + '/logo192.png',
  description: 'AI product research and launch intelligence for UK ecommerce sellers.',
  contactPoint: { '@type': 'ContactPoint', email: 'info@trendscout.click', contactType: 'customer service' },
};

const softwareSchema = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'TrendScout',
  applicationCategory: 'BusinessApplication',
  operatingSystem: 'Web',
  offers: { '@type': 'AggregateOffer', priceCurrency: 'GBP', lowPrice: '0', highPrice: '79' },
  description: 'AI product research and launch intelligence for UK ecommerce sellers.',
};

const commonLinks = [
  { href: '/', text: 'Home' },
  { href: '/pricing', text: 'Pricing' },
  { href: '/how-it-works', text: 'How It Works' },
  { href: '/sample-product-analysis', text: 'Sample Product Analysis' },
  { href: '/uk-product-viability-score', text: 'UK Product Viability Score' },
  { href: '/trending-products', text: 'Trending Products' },
  { href: '/for-shopify-sellers', text: 'For Shopify Sellers' },
  { href: '/for-tiktok-shop-uk', text: 'For TikTok Shop UK' },
  { href: '/for-amazon-uk-sellers', text: 'For Amazon UK Sellers' },
  { href: '/about', text: 'About' },
  { href: '/contact', text: 'Contact' },
  { href: '/terms', text: 'Terms' },
  { href: '/privacy', text: 'Privacy' },
];

// ═══════════════════════════════════════════════════════════════
// PAGE DATA
// ═══════════════════════════════════════════════════════════════

const PAGES = {

  '/': {
    title: 'TrendScout | AI Product Research for UK Ecommerce Sellers',
    description: 'Find products that can actually sell in the UK. TrendScout helps UK ecommerce sellers discover product demand, analyse competition, and check commercial viability before launching.',
    canonical: '/',
    schema: [orgSchema, softwareSchema, { '@context': 'https://schema.org', '@type': 'WebSite', name: 'TrendScout', url: SITE }],
    body: `
      <h1>Find products that can actually sell in the UK</h1>
      <p>TrendScout helps UK ecommerce sellers discover product demand, analyse competition, and check UK commercial viability before spending money on ads, stock, or supplier orders.</p>
      <h2>What TrendScout does</h2>
      <ul>
        <li><strong>Trend detection</strong> — spot rising demand across TikTok, Amazon, and Shopify before products peak or saturate.</li>
        <li><strong>Saturation analysis</strong> — see how crowded a niche is before entering it.</li>
        <li><strong>UK viability scoring</strong> — margins, VAT impact, shipping practicality, and channel fit scored for the UK market.</li>
      </ul>
      <h2>Who TrendScout is for</h2>
      <ul>
        <li><strong>Shopify sellers</strong> — find products with real UK demand before building a store around them.</li>
        <li><strong>Amazon UK sellers</strong> — spot opportunities with margin potential after FBA fees, VAT, and returns.</li>
        <li><strong>TikTok Shop UK sellers</strong> — go beyond viral views. Validate whether trending products can convert in the UK.</li>
        <li><strong>UK ecommerce founders</strong> — make data-backed product decisions. Test fewer products. Waste less money.</li>
      </ul>
      <h2>Not every viral product works in the UK</h2>
      <p>A product blowing up on US TikTok might have completely different economics here. 20% VAT, higher shipping costs, different consumer expectations, and smaller addressable markets all change the equation. TrendScout evaluates products based on UK commercial reality, not global hype alone.</p>
      <h2>How it works</h2>
      <ol>
        <li><strong>Discover products</strong> — browse products gaining traction across TikTok, Amazon, and Shopify.</li>
        <li><strong>Analyse UK viability</strong> — every product is scored across 7 signals including margin potential, competition, VAT impact, and UK-specific demand.</li>
        <li><strong>Launch with confidence</strong> — use AI-generated insights, profit projections, and competitive data to decide whether to test.</li>
      </ol>
      <h2>UK Product Viability Score</h2>
      <p>Every product on TrendScout receives a UK Viability Score — a 0-100 rating reflecting UK commercial fit, not just popularity. The score evaluates trend momentum, market saturation, margin potential, shipping practicality, return risk, channel fit, and UK market suitability.</p>
      <p><a href="/uk-product-viability-score">Learn how the UK Viability Score works</a> | <a href="/sample-product-analysis">See a sample product analysis</a></p>
      <h2>Pricing</h2>
      <p>Plans start from £19/month. Start with a 7-day free trial. No credit card required. <a href="/pricing">View pricing</a>.</p>
      <p><a href="/signup">Start Free</a> | <a href="/how-it-works">See How It Works</a> | <a href="/trending-products">Explore Trending Products</a></p>
    `,
  },

  '/pricing': {
    title: 'Pricing | TrendScout — UK Ecommerce Product Research Plans',
    description: 'TrendScout pricing plans from £19/month. Start validating UK product ideas with a 7-day free trial. No credit card required. Cancel anytime.',
    canonical: '/pricing',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Pricing' }])],
    body: `
      <h1>TrendScout Pricing</h1>
      <p>Product research plans built for UK ecommerce sellers. Start free. Upgrade when you are ready. Cancel anytime.</p>
      <h2>Plans</h2>
      <h3>Starter — £19/month (£15/month billed annually)</h3>
      <p>Start validating product ideas. Includes 10 product views per day, basic trend insights, daily product updates, category filters, trend score access, UK viability indicators, and email support.</p>
      <h3>Growth — £39/month (£31/month billed annually) — Best for serious sellers</h3>
      <p>For active sellers testing multiple ideas. Includes unlimited product discovery, full trend score analytics, AI ad creative generator, trend alerts and notifications, supplier intelligence, profitability simulator, saturation analysis, saved product workspace, and priority email support.</p>
      <h3>Pro — £79/month (£63/month billed annually)</h3>
      <p>For agencies and power users. Includes everything in Growth plus competitor store tracking, AI launch simulator, advanced analytics and reports, TikTok intelligence dashboard, API access (100 req/min), Shopify push-to-store, unlimited insights, and priority support.</p>
      <p>All plans include a 7-day free trial. No credit card required to start.</p>
      ${faq([
        { q: 'Is there a free plan?', a: 'Yes. Browse trending products and basic trend data without signing up. For full analytics, viability scoring, and AI features, start a free 7-day trial.' },
        { q: 'Can I cancel anytime?', a: 'Yes. Cancel from your account settings at any time. No cancellation fees. You keep access until the end of your billing period.' },
        { q: 'Do you charge in GBP?', a: 'Yes. All prices are in British pounds (GBP). Payments are processed securely by Stripe.' },
        { q: 'Is there a refund policy?', a: 'If you are not satisfied within the first 7 days of a paid subscription, contact us and we will arrange a refund.' },
        { q: 'Which plan is best for most sellers?', a: 'Growth is the most popular plan. It includes unlimited product discovery, AI ad creative generation, profitability simulation, and trend alerts — the tools serious sellers use most.' },
        { q: 'Do you offer annual billing?', a: 'Yes. Save 20% with annual billing on all plans.' },
      ])}
      <p><a href="/signup">Start Free Trial</a> | <a href="/how-it-works">How It Works</a> | <a href="/sample-product-analysis">See Sample Analysis</a></p>
    `,
  },

  '/how-it-works': {
    title: 'How It Works | TrendScout — UK Product Research Workflow',
    description: 'See how TrendScout helps UK ecommerce sellers discover trending products, analyse competition, check UK viability, and make better launch decisions.',
    canonical: '/how-it-works',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'How It Works' }])],
    body: `
      <h1>How TrendScout Works</h1>
      <p>TrendScout gives UK ecommerce sellers the data they need to make better product decisions. Here is how the platform works.</p>
      <h2>Step 1: Discover trending products</h2>
      <p>Browse products gaining traction across TikTok, Amazon, and Shopify. Multi-channel signals mean stronger demand validation than single-source tools. Filter by category, channel, trend velocity, and viability score.</p>
      <h2>Step 2: Analyse UK viability</h2>
      <p>Every product is scored using our 7-signal UK Viability Score: trend momentum, market saturation, margin potential, ad opportunity, search growth, social buzz, and UK market fit. The score reflects commercial viability in the UK — not just global popularity.</p>
      <h2>Step 3: Check margins and competition</h2>
      <p>View estimated selling price ranges, landed costs, margin bands, and VAT impact for UK sellers. See saturation indicators and competitive density before you enter a niche.</p>
      <h2>Step 4: Launch with confidence</h2>
      <p>Use AI-generated ad angle suggestions, launch scores, and profit projections to validate before you spend. Make faster decisions with more data and less guesswork.</p>
      <h2>Key features</h2>
      <ul>
        <li><strong>Trend detection</strong> — multi-channel product signals from TikTok, Amazon, and Shopify.</li>
        <li><strong>UK Viability Score</strong> — 7-signal scoring model built for UK commercial reality.</li>
        <li><strong>Competition analysis</strong> — seller density, ad saturation, and niche gaps.</li>
        <li><strong>Profit estimation</strong> — landed costs, margins, VAT, and shipping impact.</li>
        <li><strong>AI launch insights</strong> — ad angles, launch simulation, and profit projections.</li>
        <li><strong>Trend alerts</strong> — get notified when products match your criteria.</li>
      </ul>
      <p><a href="/signup">Start Free</a> | <a href="/sample-product-analysis">See Sample Analysis</a> | <a href="/uk-product-viability-score">How Viability Scoring Works</a> | <a href="/pricing">View Pricing</a></p>
    `,
  },

  '/sample-product-analysis': {
    title: 'Sample Product Analysis | TrendScout — See What You Get',
    description: 'View a real sample product analysis from TrendScout. See the UK Viability Score, 7-signal breakdown, margin estimates, channel fit, competition data, and AI summary.',
    canonical: '/sample-product-analysis',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Sample Product Analysis' }])],
    body: `
      <h1>Sample Product Analysis: Portable Neck Fan (Bladeless)</h1>
      <p>This is a sample product analysis showing the intelligence TrendScout provides for every trending product. Real scoring methodology. Real UK viability assessment.</p>
      <h2>Scores</h2>
      <ul>
        <li><strong>Launch Score:</strong> 74/100 — High confidence</li>
        <li><strong>UK Viability Score:</strong> 78/100 — Strong UK Fit</li>
      </ul>
      <h2>Quick Facts</h2>
      <ul>
        <li>Category: Personal Electronics</li>
        <li>Selling price range: £18.99 – £27.99</li>
        <li>Estimated cost: £4.50 – £7.20</li>
        <li>Estimated margin: 35% – 52%</li>
        <li>Shipping time: 7–14 days (ePacket/CJ)</li>
        <li>VAT impact: 20% reduces effective margin by ~£4–5 per unit</li>
      </ul>
      <h2>7-Signal Breakdown</h2>
      <ul>
        <li>Trend momentum: 82%</li>
        <li>Market saturation (inverted): 62%</li>
        <li>Margin potential: 71%</li>
        <li>Ad opportunity: 65%</li>
        <li>Search growth: 77%</li>
        <li>Social buzz: 88%</li>
        <li>UK market fit: 78%</li>
      </ul>
      <h2>Best Channel Fit</h2>
      <ul>
        <li>TikTok Shop UK — high visual appeal, impulse-buy price point</li>
        <li>Shopify Store — good for branded store with seasonal push</li>
        <li>Amazon.co.uk — established demand but moderate FBA competition</li>
      </ul>
      <h2>AI Summary</h2>
      <p>This product shows strong trend momentum with genuine UK demand signals. The portable neck fan category benefits from seasonal summer spikes and year-round gym/commute usage. Social media traction is high, particularly on TikTok. UK-specific margin analysis suggests healthy profitability even after 20% VAT, though shipping times from standard suppliers may impact customer satisfaction during peak demand. Competition is moderate — the market is not yet saturated on TikTok Shop UK, offering a first-mover window. Best suited to TikTok Shop or a branded Shopify store with targeted social advertising.</p>
      <h2>Key Strengths</h2>
      <ul>
        <li>Strong TikTok viral potential with visual product appeal</li>
        <li>Healthy margin range for UK sellers even after VAT</li>
        <li>Repeat purchase potential (seasonal + gifting)</li>
      </ul>
      <h2>Key Risks</h2>
      <ul>
        <li>Seasonal dependency — demand dips sharply in winter months</li>
        <li>Quality variance — cheap suppliers may lead to higher returns</li>
        <li>Growing competition on Amazon.co.uk</li>
      </ul>
      <h2>Recommended Next Steps</h2>
      <ol>
        <li>Source 2–3 supplier samples to test quality before committing</li>
        <li>Run a small TikTok ad test (£50–100 budget) to validate UK click-through rates</li>
        <li>Check current Amazon.co.uk listing density before launching on that channel</li>
      </ol>
      <p><a href="/signup">Start Free — Analyse Real Products</a> | <a href="/uk-product-viability-score">How Viability Scoring Works</a> | <a href="/pricing">View Pricing</a> | <a href="/trending-products">Browse Trending Products</a></p>
    `,
  },

  '/uk-product-viability-score': {
    title: 'UK Product Viability Score | TrendScout — How We Score Products for the UK',
    description: 'Understand how TrendScout scores products for UK commercial viability. Our 7-signal model evaluates trend momentum, saturation, margins, shipping, returns, and channel fit.',
    canonical: '/uk-product-viability-score',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'UK Product Viability Score' }])],
    body: `
      <h1>UK Product Viability Score</h1>
      <p>The UK Product Viability Score is TrendScout's flagship metric — a 0-100 rating that reflects how commercially viable a product is for UK ecommerce sellers. It is not a popularity score. It is a UK commercial fit score.</p>
      <h2>What makes it different</h2>
      <p>Most product research tools score products based on global trend data. That tells you what is popular, not what is profitable in the UK. TrendScout evaluates products based on UK commercial reality — factoring in VAT, higher shipping costs, different consumer expectations, and smaller addressable markets.</p>
      <h2>The 7 scoring signals</h2>
      <ol>
        <li><strong>Trend momentum</strong> — is demand rising, flat, or declining? We track multi-channel signals across TikTok, Amazon, and Shopify.</li>
        <li><strong>Market saturation</strong> — how many sellers are already competing? High saturation reduces opportunity.</li>
        <li><strong>Margin potential</strong> — estimated profit margin after landed costs, shipping, and 20% UK VAT.</li>
        <li><strong>Shipping practicality</strong> — can it be shipped affordably and reliably to UK customers?</li>
        <li><strong>Return risk</strong> — products with high return rates erode margins. We factor in category return norms.</li>
        <li><strong>Channel fit</strong> — is this product better suited to Shopify, TikTok Shop UK, or Amazon.co.uk?</li>
        <li><strong>UK market suitability</strong> — does this product have genuine UK demand, or is it a US-only trend?</li>
      </ol>
      <h2>Score ranges</h2>
      <ul>
        <li><strong>80–100:</strong> Strong UK fit — high viability across most signals.</li>
        <li><strong>60–79:</strong> Moderate UK fit — viable but with some risk factors to consider.</li>
        <li><strong>40–59:</strong> Weak UK fit — significant concerns in multiple areas.</li>
        <li><strong>0–39:</strong> Poor UK fit — not recommended for most UK sellers.</li>
      </ul>
      ${faq([
        { q: 'How often are scores updated?', a: 'Scores are recalculated daily as new trend data, competition data, and market signals are processed.' },
        { q: 'Can I see the score before signing up?', a: 'Yes. Browse trending products and view viability indicators for free. Full score breakdowns are available on paid plans. You can also view our sample product analysis for a complete example.' },
        { q: 'Does a high score guarantee success?', a: 'No. The score reflects data-driven commercial viability, not guaranteed outcomes. It helps you make better-informed decisions and avoid wasting money on products unlikely to work in the UK.' },
        { q: 'How is this different from other research tools?', a: 'Most tools score products on global popularity. TrendScout scores products specifically for UK commercial fit — including VAT impact, UK shipping costs, and UK consumer demand.' },
        { q: 'What data sources do you use?', a: 'We aggregate signals from multiple ecommerce platforms, search trends, social media, advertising data, and market intelligence sources. Our methodology is explained in detail on our methodology page.' },
        { q: 'Is the methodology transparent?', a: 'Yes. We explain exactly what factors are scored and how they contribute to the overall viability rating. See our methodology page for full details.' },
      ])}
      <p><a href="/sample-product-analysis">See a full sample analysis</a> | <a href="/methodology">View scoring methodology</a> | <a href="/signup">Start Free</a> | <a href="/pricing">View Pricing</a></p>
    `,
  },

  '/trending-products': {
    title: 'Trending Products UK | TrendScout — Products Gaining Traction Now',
    description: 'Browse products trending across TikTok, Amazon, and Shopify. Each product is scored for UK commercial viability using our 7-signal scoring model.',
    canonical: '/trending-products',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Trending Products' }])],
    body: `
      <h1>Trending Products — UK Ecommerce</h1>
      <p>Browse products gaining traction across TikTok, Amazon, and Shopify. Each product is scored for UK commercial viability using our 7-signal UK Viability Score.</p>
      <p>Filter by category, channel, trend velocity, and viability score. See which products have real UK demand — not just global hype.</p>
      <p><a href="/signup">Start Free to unlock full analytics</a> | <a href="/sample-product-analysis">See a sample analysis</a> | <a href="/uk-product-viability-score">How viability scoring works</a></p>
    `,
  },

  '/about': {
    title: 'About TrendScout | UK-First Ecommerce Intelligence Platform',
    description: 'TrendScout is a UK-first AI product research platform helping ecommerce sellers discover demand, analyse competition, and validate products before launching.',
    canonical: '/about',
    schema: [orgSchema, breadcrumb([{ name: 'Home', url: '/' }, { name: 'About' }]), { '@context': 'https://schema.org', '@type': 'AboutPage', name: 'About TrendScout', description: 'UK-first ecommerce intelligence platform.' }],
    body: `
      <h1>About TrendScout</h1>
      <p>TrendScout is a UK-first AI product research and launch intelligence platform. We help ecommerce sellers discover product demand, analyse competition, and check UK commercial viability before spending money on ads, stock, or supplier orders.</p>
      <h2>Why we built TrendScout</h2>
      <p>Most product research tools are built for the US market. They show what is trending globally but do not account for UK-specific economics — 20% VAT, higher shipping costs, different consumer expectations, and smaller addressable markets. TrendScout was built specifically to help UK ecommerce sellers make better product decisions.</p>
      <h2>What makes us different</h2>
      <ul>
        <li><strong>UK-first data</strong> — every product is scored for UK commercial viability, not just global popularity.</li>
        <li><strong>7-signal scoring</strong> — trend momentum, saturation, margins, shipping, returns, channel fit, and UK market suitability.</li>
        <li><strong>Multi-channel intelligence</strong> — signals from TikTok, Amazon, Shopify, and search data.</li>
        <li><strong>Transparent methodology</strong> — we explain exactly how scores are calculated.</li>
      </ul>
      <h2>Company</h2>
      <p>TrendScout is based in the United Kingdom. Contact us at <a href="mailto:info@trendscout.click">info@trendscout.click</a>.</p>
      <p><a href="/how-it-works">How it works</a> | <a href="/methodology">Our methodology</a> | <a href="/sample-product-analysis">Sample product analysis</a> | <a href="/pricing">Pricing</a></p>
    `,
  },

  '/contact': {
    title: 'Contact TrendScout | UK Ecommerce Product Research Support',
    description: 'Get in touch with the TrendScout team. Email us at info@trendscout.click for support, partnerships, or general enquiries.',
    canonical: '/contact',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Contact' }]), { '@context': 'https://schema.org', '@type': 'ContactPage', name: 'Contact TrendScout' }],
    body: `
      <h1>Contact TrendScout</h1>
      <p>Have a question about TrendScout? Get in touch and we will get back to you as quickly as we can.</p>
      <h2>Email</h2>
      <p><a href="mailto:info@trendscout.click">info@trendscout.click</a></p>
      <h2>What we can help with</h2>
      <ul>
        <li>Account and billing questions</li>
        <li>Product feature questions</li>
        <li>Partnership and integration enquiries</li>
        <li>Bug reports and technical support</li>
      </ul>
      <p><a href="/about">About TrendScout</a> | <a href="/pricing">Pricing</a> | <a href="/how-it-works">How It Works</a></p>
    `,
  },

  '/features': {
    title: 'Features | TrendScout — UK Ecommerce Product Research Tools',
    description: 'Explore TrendScout features: trend detection, UK viability scoring, competition analysis, profit estimation, AI launch insights, and trend alerts for UK sellers.',
    canonical: '/features',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Features' }])],
    body: `
      <h1>TrendScout Features</h1>
      <p>Product research tools built for UK ecommerce sellers. Discover trends, validate demand, and make better launch decisions.</p>
      <h2>Trend Detection</h2>
      <p>Spot rising products across TikTok, Amazon, and Shopify before they peak or saturate. Multi-channel signals give you stronger validation than single-source tools.</p>
      <h2>UK Product Viability Score</h2>
      <p>Every product is scored across 7 signals including trend momentum, market saturation, margin potential, shipping practicality, return risk, channel fit, and UK market suitability. <a href="/uk-product-viability-score">Learn more about the scoring model</a>.</p>
      <h2>Competition Analysis</h2>
      <p>See seller density, ad saturation, and where gaps still exist before entering a niche.</p>
      <h2>Profit Estimation</h2>
      <p>Estimate landed costs, margins, and VAT impact for UK customers — not just US projections.</p>
      <h2>AI Launch Insights</h2>
      <p>Get ad angle suggestions, launch scores, and profit projections to validate before you spend.</p>
      <h2>Trend Alerts</h2>
      <p>Set criteria and get notified when products match your requirements.</p>
      <p><a href="/sample-product-analysis">See a sample analysis</a> | <a href="/signup">Start Free</a> | <a href="/pricing">View Pricing</a></p>
    `,
  },

  '/uk-product-research': {
    title: 'UK Product Research | TrendScout — Find Products for UK Ecommerce',
    description: 'AI-powered product research built for the UK market. Discover trends, analyse UK-specific competition, and validate products before launching on Shopify, TikTok Shop, or Amazon UK.',
    canonical: '/uk-product-research',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'UK Product Research' }])],
    body: `
      <h1>UK Product Research</h1>
      <p>Product research built for UK ecommerce sellers. TrendScout helps you find products with genuine UK demand, analyse competition in the UK market, and check commercial viability before launching.</p>
      <h2>Why UK-specific product research matters</h2>
      <p>A product trending in the US does not automatically work in the UK. Different tax structures (20% VAT), higher shipping costs, smaller addressable markets, and different consumer preferences all affect viability. TrendScout accounts for these UK-specific factors in every product analysis.</p>
      <h2>What you get</h2>
      <ul>
        <li>Products scored specifically for UK commercial viability</li>
        <li>Margin estimates including 20% VAT impact</li>
        <li>UK shipping cost and practicality analysis</li>
        <li>Competition data from UK-specific channels</li>
        <li>Channel recommendations for Shopify, TikTok Shop UK, and Amazon.co.uk</li>
      </ul>
      <p><a href="/sample-product-analysis">View a sample product analysis</a> | <a href="/signup">Start Free</a> | <a href="/pricing">View Pricing</a></p>
    `,
  },

  '/for-shopify-sellers': {
    title: 'Product Research for Shopify UK Sellers | TrendScout',
    description: 'Find products that work for UK Shopify stores. TrendScout helps Shopify sellers discover demand, check UK viability, and validate products before building stores around them.',
    canonical: '/for-shopify-sellers',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'For Shopify Sellers' }])],
    body: `
      <h1>Product Research for Shopify UK Sellers</h1>
      <p>Find products with real UK demand before you build a Shopify store around them. TrendScout helps Shopify sellers discover trending products, check UK commercial viability, and make smarter launch decisions.</p>
      <h2>Why Shopify sellers use TrendScout</h2>
      <ul>
        <li>Discover products trending on TikTok, Amazon, and Shopify with UK demand signals</li>
        <li>Check UK viability before committing to inventory or ad spend</li>
        <li>Estimate margins after 20% VAT and UK shipping costs</li>
        <li>Get AI-generated ad angles and creative suggestions</li>
        <li>Push winning products directly to your Shopify store</li>
      </ul>
      <h2>Built for UK Shopify economics</h2>
      <p>Most product research tools show US pricing and US margins. TrendScout calculates margins, shipping, and viability specifically for UK Shopify sellers — so you know what a product will actually earn you, not what it earns someone in the US.</p>
      <p><a href="/sample-product-analysis">See a sample product analysis</a> | <a href="/signup">Start Free</a> | <a href="/pricing">View Pricing</a> | <a href="/shopify-product-research-uk">Shopify Product Research UK</a></p>
    `,
  },

  '/for-amazon-uk-sellers': {
    title: 'Product Research for Amazon UK Sellers | TrendScout',
    description: 'Find products with margin potential on Amazon.co.uk. TrendScout helps Amazon UK sellers validate demand, check competition, and estimate profitability after FBA fees and VAT.',
    canonical: '/for-amazon-uk-sellers',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'For Amazon UK Sellers' }])],
    body: `
      <h1>Product Research for Amazon UK Sellers</h1>
      <p>Spot opportunities with margin potential after FBA fees, VAT, and returns. TrendScout helps Amazon UK sellers discover trending products and validate demand before listing.</p>
      <h2>Why Amazon UK sellers use TrendScout</h2>
      <ul>
        <li>Find products with rising demand on Amazon.co.uk and cross-channel signals</li>
        <li>Check saturation — how many sellers are already competing for a keyword</li>
        <li>Estimate margins after FBA fees, 20% VAT, and shipping costs</li>
        <li>See which products have stronger opportunity on Amazon vs Shopify vs TikTok Shop</li>
      </ul>
      <p><a href="/sample-product-analysis">See a sample analysis</a> | <a href="/signup">Start Free</a> | <a href="/pricing">View Pricing</a></p>
    `,
  },

  '/for-tiktok-shop-uk': {
    title: 'Product Research for TikTok Shop UK Sellers | TrendScout',
    description: 'Go beyond viral views. TrendScout helps TikTok Shop UK sellers validate whether trending products can actually convert and profit in the UK market.',
    canonical: '/for-tiktok-shop-uk',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'For TikTok Shop UK' }])],
    body: `
      <h1>Product Research for TikTok Shop UK Sellers</h1>
      <p>Go beyond viral views. TrendScout helps TikTok Shop UK sellers validate whether a trending product can actually convert and profit in the UK market.</p>
      <h2>Why TikTok Shop UK sellers use TrendScout</h2>
      <ul>
        <li>See which viral products have genuine UK buying intent, not just views</li>
        <li>Check UK margins after VAT, shipping, and platform fees</li>
        <li>Identify TikTok Shop UK products before the niche gets saturated</li>
        <li>Get AI-generated ad angle suggestions for TikTok creative</li>
      </ul>
      <p><a href="/sample-product-analysis">See a sample analysis</a> | <a href="/signup">Start Free</a> | <a href="/tiktok-shop-product-research-uk">TikTok Shop Product Research UK</a></p>
    `,
  },

  '/compare/jungle-scout-vs-trendscout': {
    title: 'Jungle Scout vs TrendScout | UK-Focused Product Research Comparison',
    description: 'Compare Jungle Scout and TrendScout for UK product research. See how TrendScout provides UK-specific viability scoring, multi-channel data, and GBP-first economics.',
    canonical: '/compare/jungle-scout-vs-trendscout',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Compare', url: '/compare/jungle-scout-vs-trendscout' }, { name: 'Jungle Scout vs TrendScout' }])],
    body: `
      <h1>Jungle Scout vs TrendScout</h1>
      <p>How does TrendScout compare to Jungle Scout for UK ecommerce product research?</p>
      <h2>Key differences</h2>
      <ul>
        <li><strong>Market focus:</strong> Jungle Scout is primarily built for Amazon US sellers. TrendScout is built for UK ecommerce sellers across Shopify, TikTok Shop, and Amazon UK.</li>
        <li><strong>UK viability scoring:</strong> TrendScout provides a dedicated UK Viability Score factoring in VAT, UK shipping, and UK consumer demand. Jungle Scout does not offer UK-specific viability scoring.</li>
        <li><strong>Multi-channel:</strong> TrendScout tracks trends across TikTok, Amazon, and Shopify. Jungle Scout focuses primarily on Amazon.</li>
        <li><strong>Pricing:</strong> TrendScout starts at £19/month with GBP billing. Jungle Scout is priced in USD.</li>
      </ul>
      <h2>When to use TrendScout</h2>
      <p>If you sell on UK platforms, want UK-specific margin analysis including VAT, and need multi-channel product signals beyond just Amazon, TrendScout is built for you.</p>
      <h2>When to use Jungle Scout</h2>
      <p>If you primarily sell on Amazon US and need deep Amazon-specific keyword and listing tools, Jungle Scout may be a better fit.</p>
      <p><a href="/signup">Try TrendScout Free</a> | <a href="/pricing">View Pricing</a> | <a href="/sample-product-analysis">See Sample Analysis</a></p>
    `,
  },

  '/compare/sell-the-trend-vs-trendscout': {
    title: 'Sell The Trend vs TrendScout | UK Product Research Comparison',
    description: 'Compare Sell The Trend and TrendScout. See why UK sellers prefer TrendScout for UK-specific viability scoring, margin analysis, and multi-channel product intelligence.',
    canonical: '/compare/sell-the-trend-vs-trendscout',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Compare' }, { name: 'Sell The Trend vs TrendScout' }])],
    body: `
      <h1>Sell The Trend vs TrendScout</h1>
      <p>How does TrendScout compare to Sell The Trend for UK ecommerce product research?</p>
      <h2>Key differences</h2>
      <ul>
        <li><strong>UK focus:</strong> TrendScout is built specifically for UK sellers with UK Viability Scoring, GBP pricing, and VAT-adjusted margin analysis. Sell The Trend is a global tool without UK-specific intelligence.</li>
        <li><strong>Viability scoring:</strong> TrendScout scores products on 7 UK-specific signals. Sell The Trend focuses on trend detection without UK commercial fit analysis.</li>
        <li><strong>Credibility:</strong> TrendScout provides transparent methodology and sample analyses. No fake urgency or hype-driven marketing.</li>
      </ul>
      <p><a href="/signup">Try TrendScout Free</a> | <a href="/pricing">View Pricing</a></p>
    `,
  },

  '/compare/minea-vs-trendscout': {
    title: 'Minea vs TrendScout | UK Product Research Comparison',
    description: 'Compare Minea and TrendScout for UK product research. See how TrendScout provides UK-specific viability scoring and multi-channel intelligence.',
    canonical: '/compare/minea-vs-trendscout',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Compare' }, { name: 'Minea vs TrendScout' }])],
    body: `
      <h1>Minea vs TrendScout</h1>
      <p>How does TrendScout compare to Minea for UK ecommerce sellers?</p>
      <h2>Key differences</h2>
      <ul>
        <li><strong>UK focus:</strong> TrendScout provides UK Viability Scoring with VAT, shipping, and UK demand analysis. Minea is a global ad spy tool.</li>
        <li><strong>Product validation:</strong> TrendScout goes beyond ad spying to score commercial viability. Minea shows what ads are running but not whether a product will work in the UK.</li>
        <li><strong>Multi-channel:</strong> TrendScout tracks trends across TikTok, Amazon, and Shopify. Minea focuses on social ad monitoring.</li>
      </ul>
      <p><a href="/signup">Try TrendScout Free</a> | <a href="/pricing">View Pricing</a> | <a href="/sample-product-analysis">See Sample Analysis</a></p>
    `,
  },

  '/compare/helium-10-vs-trendscout': {
    title: 'Helium 10 vs TrendScout | UK Product Research Comparison',
    description: 'Compare Helium 10 and TrendScout. See why UK ecommerce sellers choose TrendScout for UK-specific viability scoring beyond Amazon-only tools.',
    canonical: '/compare/helium-10-vs-trendscout',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Compare' }, { name: 'Helium 10 vs TrendScout' }])],
    body: `
      <h1>Helium 10 vs TrendScout</h1>
      <p>How does TrendScout compare to Helium 10 for UK product research?</p>
      <h2>Key differences</h2>
      <ul>
        <li><strong>Market focus:</strong> Helium 10 is primarily an Amazon seller toolkit. TrendScout is a multi-channel UK product research platform.</li>
        <li><strong>UK viability:</strong> TrendScout scores products for UK commercial fit. Helium 10 provides Amazon keyword and listing tools without UK-specific viability analysis.</li>
        <li><strong>Multi-channel:</strong> TrendScout covers TikTok, Amazon, and Shopify. Helium 10 is Amazon-focused.</li>
        <li><strong>Pricing:</strong> TrendScout starts at £19/month in GBP. Helium 10 starts at $39/month in USD.</li>
      </ul>
      <p><a href="/signup">Try TrendScout Free</a> | <a href="/pricing">View Pricing</a></p>
    `,
  },

  '/compare/ecomhunt-vs-trendscout': {
    title: 'Ecomhunt vs TrendScout | UK Product Research Comparison',
    description: 'Compare Ecomhunt and TrendScout. See why UK sellers prefer TrendScout for UK viability scoring, margin analysis, and multi-channel product intelligence.',
    canonical: '/compare/ecomhunt-vs-trendscout',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Compare' }, { name: 'Ecomhunt vs TrendScout' }])],
    body: `
      <h1>Ecomhunt vs TrendScout</h1>
      <p>Ecomhunt curates trending products from AliExpress and social media. TrendScout provides multi-channel UK product intelligence with viability scoring.</p>
      <h2>Key differences</h2>
      <ul>
        <li><strong>Depth:</strong> TrendScout provides 7-signal UK Viability Scoring, margin analysis, and AI launch insights. Ecomhunt provides curated product lists.</li>
        <li><strong>UK focus:</strong> TrendScout factors in UK VAT, shipping, and demand. Ecomhunt is globally focused without UK-specific intelligence.</li>
      </ul>
      <p><a href="/signup">Try TrendScout Free</a> | <a href="/pricing">View Pricing</a></p>
    `,
  },

  '/tools': {
    title: 'Free Ecommerce Tools | TrendScout — UK Product Research Tools',
    description: 'Free ecommerce tools for UK sellers. Product quiz, viability check, trend analysis, and more. No signup required for basic tools.',
    canonical: '/tools',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Free Tools' }])],
    body: `
      <h1>Free Ecommerce Tools</h1>
      <p>Free product research tools for UK ecommerce sellers. Use these to get a quick read on product ideas before committing.</p>
      <h2>Quick Viability Check</h2>
      <p>Enter a product name and get an instant UK viability indication. Free, no signup required.</p>
      <h2>Product Quiz</h2>
      <p>Answer a few questions and get personalised product category suggestions based on your goals and budget. <a href="/product-quiz">Take the quiz</a>.</p>
      <h2>Trending Products</h2>
      <p>Browse products trending across TikTok, Amazon, and Shopify. Free to browse with viability indicators. <a href="/trending-products">View trending products</a>.</p>
      <p><a href="/signup">Start Free for full analytics</a> | <a href="/sample-product-analysis">See sample analysis</a> | <a href="/pricing">View Pricing</a></p>
    `,
  },

  '/product-quiz': {
    title: 'Product Quiz | TrendScout — Find Your Ideal Product Category',
    description: 'Take the TrendScout product quiz. Answer a few questions and get personalised product category suggestions for UK ecommerce.',
    canonical: '/product-quiz',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Free Tools', url: '/tools' }, { name: 'Product Quiz' }])],
    body: `
      <h1>Product Quiz — Find Your Ideal Product Category</h1>
      <p>Not sure what to sell? Answer a few quick questions about your budget, experience level, and goals, and we will suggest product categories that might work for you in the UK market.</p>
      <p><a href="/tools">Back to Free Tools</a> | <a href="/trending-products">Browse Trending Products</a></p>
    `,
  },

  '/shopify-product-research-uk': {
    title: 'Shopify Product Research UK | TrendScout',
    description: 'Find products for UK Shopify stores. TrendScout provides UK viability scoring, margin analysis, and trend data to help Shopify sellers launch smarter.',
    canonical: '/shopify-product-research-uk',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Shopify Product Research UK' }])],
    body: `
      <h1>Shopify Product Research UK</h1>
      <p>Find products for your UK Shopify store. TrendScout provides UK-specific viability scoring, margin analysis including 20% VAT, and multi-channel trend data.</p>
      <h2>What UK Shopify sellers need</h2>
      <p>UK Shopify sellers face different economics than US sellers. Higher shipping costs, 20% VAT, and different consumer expectations mean you need UK-specific product intelligence. TrendScout provides exactly that.</p>
      <p><a href="/for-shopify-sellers">Learn more about TrendScout for Shopify</a> | <a href="/sample-product-analysis">See sample analysis</a> | <a href="/signup">Start Free</a></p>
    `,
  },

  '/tiktok-shop-product-research-uk': {
    title: 'TikTok Shop Product Research UK | TrendScout',
    description: 'Find products for TikTok Shop UK. Go beyond viral views with UK viability scoring, margin analysis, and trend validation from TrendScout.',
    canonical: '/tiktok-shop-product-research-uk',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'TikTok Shop Product Research UK' }])],
    body: `
      <h1>TikTok Shop Product Research UK</h1>
      <p>Go beyond viral views. TrendScout helps TikTok Shop UK sellers validate whether trending products can actually convert and profit in the UK market.</p>
      <h2>Why TikTok Shop UK needs better research</h2>
      <p>Viral views do not equal sales. A product with millions of views on US TikTok might have completely different economics in the UK. TrendScout validates UK demand, margins, and competition before you invest.</p>
      <p><a href="/for-tiktok-shop-uk">TrendScout for TikTok Shop UK</a> | <a href="/sample-product-analysis">See sample analysis</a> | <a href="/signup">Start Free</a></p>
    `,
  },

  '/best-products-to-sell-online-uk': {
    title: 'Best Products to Sell Online in the UK | TrendScout',
    description: 'Discover the best products to sell online in the UK. Data-driven product discovery with UK viability scoring, margin analysis, and trend intelligence.',
    canonical: '/best-products-to-sell-online-uk',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Best Products to Sell Online UK' }])],
    body: `
      <h1>Best Products to Sell Online in the UK</h1>
      <p>Finding the best products to sell online in the UK requires more than browsing AliExpress. You need data on UK-specific demand, realistic margin analysis including VAT, and competition intelligence. TrendScout provides all three.</p>
      <h2>How to find products that work in the UK</h2>
      <ul>
        <li>Look for products with genuine UK search demand, not just global trends</li>
        <li>Calculate margins after 20% VAT, UK shipping, and platform fees</li>
        <li>Check competition — how many UK sellers are already offering the same product</li>
        <li>Validate across channels — Shopify, TikTok Shop UK, Amazon.co.uk</li>
      </ul>
      <p><a href="/trending-products">Browse trending products</a> | <a href="/sample-product-analysis">See sample analysis</a> | <a href="/signup">Start Free</a></p>
    `,
  },

  '/product-validation-uk': {
    title: 'Product Validation UK | TrendScout — Validate Before You Launch',
    description: 'Validate products for the UK market before spending on ads or stock. Check demand, competition, margins, and UK commercial viability with TrendScout.',
    canonical: '/product-validation-uk',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Product Validation UK' }])],
    body: `
      <h1>Product Validation UK</h1>
      <p>Validate products for the UK market before spending money on ads, stock, or supplier orders. TrendScout helps you check demand, competition, margins, and UK commercial viability in one place.</p>
      <h2>What product validation means</h2>
      <p>Product validation is the process of checking whether a product idea has real commercial potential before you invest. For UK sellers, this means checking UK-specific demand, realistic margin analysis, competition density, and channel suitability.</p>
      <p><a href="/uk-product-viability-score">How we score UK viability</a> | <a href="/sample-product-analysis">See sample analysis</a> | <a href="/signup">Start Free</a></p>
    `,
  },

  '/dropshipping-uk': {
    title: 'Dropshipping Product Research UK | TrendScout',
    description: 'Find dropshipping products that work in the UK. TrendScout provides UK viability scoring, margin analysis, and trend data for UK dropshippers.',
    canonical: '/dropshipping-uk',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Dropshipping UK' }])],
    body: `
      <h1>Dropshipping Product Research UK</h1>
      <p>Find dropshipping products that can actually work in the UK market. TrendScout helps UK dropshippers discover trending products, check margins after VAT, and validate demand before listing.</p>
      <h2>UK dropshipping challenges</h2>
      <p>UK dropshippers face unique challenges: 20% VAT on imports, longer shipping times from overseas suppliers, higher customer expectations for delivery speed, and a competitive market. TrendScout factors all of these into product analysis.</p>
      <p><a href="/trending-products">Browse trending products</a> | <a href="/sample-product-analysis">See sample analysis</a> | <a href="/signup">Start Free</a></p>
    `,
  },

  '/winning-products-uk': {
    title: 'UK Product Opportunities | TrendScout — Data-Driven Product Discovery',
    description: 'Discover product opportunities for UK ecommerce. Data-driven product discovery with UK viability scoring, margin analysis, and multi-channel trend intelligence.',
    canonical: '/winning-products-uk',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'UK Product Opportunities' }])],
    body: `
      <h1>UK Product Opportunities</h1>
      <p>Discover product opportunities for UK ecommerce with data-driven intelligence. TrendScout helps you find products with genuine UK demand, healthy margins, and manageable competition.</p>
      <p>Trend data is easy. Profitable decisions are harder. TrendScout helps you move from trending product lists to validated UK product opportunities.</p>
      <p><a href="/trending-products">Browse trending products</a> | <a href="/uk-product-viability-score">How viability scoring works</a> | <a href="/signup">Start Free</a></p>
    `,
  },

  '/trend-analysis-uk': {
    title: 'UK Ecommerce Trend Analysis | TrendScout',
    description: 'Analyse UK ecommerce trends with TrendScout. Multi-channel trend detection, UK viability scoring, and data-driven product intelligence.',
    canonical: '/trend-analysis-uk',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Trend Analysis UK' }])],
    body: `
      <h1>UK Ecommerce Trend Analysis</h1>
      <p>Analyse ecommerce trends specifically for the UK market. TrendScout tracks product trends across TikTok, Amazon, and Shopify and scores them for UK commercial viability.</p>
      <p><a href="/trending-products">Browse current trends</a> | <a href="/sample-product-analysis">See sample analysis</a> | <a href="/signup">Start Free</a></p>
    `,
  },

  // ═══ LEGAL PAGES ═══

  '/privacy': {
    title: 'Privacy Policy | TrendScout',
    description: 'TrendScout privacy policy. How we collect, use, and protect your data. British English. Last updated March 2026.',
    canonical: '/privacy',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Privacy Policy' }])],
    body: `
      <h1>Privacy Policy</h1>
      <p>Last updated: March 2026</p>
      <h2>1. Information We Collect</h2>
      <p><strong>Account data:</strong> Email address, name, and password hash when you register.</p>
      <p><strong>Usage data:</strong> Pages viewed, features used, products analysed, and interaction patterns to improve the Service.</p>
      <p><strong>Payment data:</strong> Processed securely by Stripe. We do not store card details.</p>
      <p><strong>Shopify store data:</strong> When you connect your Shopify store, we access your store name, product catalogue, and order metadata solely to provide product intelligence features. We do not access your customers' personal information.</p>
      <h2>2. How We Use Your Information</h2>
      <p>We use your data to: (a) provide and improve the Service; (b) process subscriptions and payments; (c) send relevant product alerts you have opted into; (d) analyse aggregate usage patterns; (e) push product drafts to your connected Shopify store when you request it.</p>
      <h2>3. Data Sharing</h2>
      <p>We do not sell your personal data. We may share data with: (a) payment processors (Stripe) to handle billing; (b) email service providers to send notifications; (c) law enforcement if required by law.</p>
      <h2>4. Cookies and Analytics</h2>
      <p>We use essential cookies for authentication and session management. Analytics cookies (Google Analytics) are only set after you explicitly consent via our cookie banner. See our <a href="/cookie-policy">cookie policy</a> for full details.</p>
      <h2>5. Data Security</h2>
      <p>We use encryption at rest and in transit. Access tokens for connected platforms are encrypted using industry-standard symmetric encryption. We follow security best practices for data protection.</p>
      <h2>6. Your Rights</h2>
      <p>You can request access, correction, or deletion of your personal data. Contact <a href="mailto:info@trendscout.click">info@trendscout.click</a> for data requests. We aim to respond within 30 days.</p>
      <h2>7. Data Retention</h2>
      <p>Account data is retained while your account is active. Usage data is retained for up to 24 months for analytics purposes. You may request deletion at any time.</p>
      <h2>8. Changes</h2>
      <p>We may update this policy. Material changes will be communicated via email or in-app notification.</p>
      <h2>9. Contact</h2>
      <p>For privacy enquiries, contact <a href="mailto:info@trendscout.click">info@trendscout.click</a>.</p>
      <p><a href="/terms">Terms of Service</a> | <a href="/cookie-policy">Cookie Policy</a> | <a href="/refund-policy">Refund Policy</a> | <a href="/contact">Contact</a></p>
    `,
  },

  '/terms': {
    title: 'Terms of Service | TrendScout',
    description: 'TrendScout terms of service. Acceptable use, subscriptions, billing, intellectual property, and liability. Last updated March 2026.',
    canonical: '/terms',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Terms of Service' }])],
    body: `
      <h1>Terms of Service</h1>
      <p>Last updated: March 2026</p>
      <h2>1. Acceptance of Terms</h2>
      <p>By accessing or using TrendScout ("the Service"), you agree to be bound by these Terms of Service. If you do not agree, do not use the Service.</p>
      <h2>2. Description of Service</h2>
      <p>TrendScout is an AI-powered product research platform that helps UK ecommerce sellers discover trending products, analyse market competition, and make data-driven launch decisions. The Service includes product trend data, market analysis, viability scoring, and related features.</p>
      <h2>3. User Accounts</h2>
      <p>You are responsible for maintaining the security of your account credentials. You must provide accurate information when creating an account. You may not share your account.</p>
      <h2>4. Subscription and Billing</h2>
      <p>Paid subscriptions are billed on a recurring basis in GBP. You may cancel at any time through your account settings. Refunds are handled according to our <a href="/refund-policy">refund policy</a>.</p>
      <h2>5. Shopify Integration</h2>
      <p>When you connect a Shopify store: (a) you authorise us to access your store's product catalogue and inventory data; (b) we may create draft products at your request; (c) access tokens are encrypted at rest; (d) you may disconnect at any time.</p>
      <h2>6. Acceptable Use</h2>
      <p>You may not use the Service for unlawful purposes, attempt to reverse-engineer the platform, share account credentials, or use automated tools to scrape data beyond normal usage.</p>
      <h2>7. Intellectual Property</h2>
      <p>TrendScout, its scoring models, and platform content are proprietary. You may not copy, redistribute, or create derivative works from the platform without permission.</p>
      <h2>8. Limitation of Liability</h2>
      <p>TrendScout provides product intelligence data to inform decisions. We do not guarantee commercial outcomes. Scores reflect data-driven analysis, not guaranteed success. You are responsible for your own business decisions.</p>
      <h2>9. Changes</h2>
      <p>We may update these terms. Material changes will be communicated via email or in-app notification. Continued use after changes constitutes acceptance.</p>
      <h2>10. Governing Law</h2>
      <p>These terms are governed by the laws of England and Wales.</p>
      <h2>11. Contact</h2>
      <p>For questions about these terms, contact <a href="mailto:info@trendscout.click">info@trendscout.click</a>.</p>
      <p><a href="/privacy">Privacy Policy</a> | <a href="/cookie-policy">Cookie Policy</a> | <a href="/refund-policy">Refund Policy</a> | <a href="/contact">Contact</a></p>
    `,
  },

  '/cookie-policy': {
    title: 'Cookie Policy | TrendScout',
    description: 'TrendScout cookie policy. How we use cookies, what categories we use, and how to manage your preferences. Last updated March 2026.',
    canonical: '/cookie-policy',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Cookie Policy' }])],
    body: `
      <h1>Cookie Policy</h1>
      <p>Last updated: March 2026</p>
      <h2>What are cookies?</h2>
      <p>Cookies are small text files placed on your device when you visit a website. They help the site remember your preferences and understand how you use it.</p>
      <h2>Cookie categories</h2>
      <h3>Essential cookies (always active)</h3>
      <p>Required for TrendScout to function. These handle authentication, session management, CSRF protection, and security. You cannot opt out of essential cookies.</p>
      <h3>Analytics cookies (requires consent)</h3>
      <p>Help us understand how visitors use TrendScout. Set only after you accept via the consent banner. Provider: Google Analytics (GA4).</p>
      <h3>Preference cookies (always active)</h3>
      <p>Remember your settings such as pricing toggle state, A/B test assignments, and cookie consent choice.</p>
      <h2>How we handle consent</h2>
      <p>Analytics cookies are not set until you explicitly accept them via our cookie consent banner. If you reject non-essential cookies, only essential and preference cookies are used.</p>
      <h2>Managing cookies</h2>
      <p>You can control cookies through your browser settings. To reset your consent preference, clear localStorage for this site and refresh.</p>
      <h2>Contact</h2>
      <p>For cookie questions, contact <a href="mailto:info@trendscout.click">info@trendscout.click</a>.</p>
      <p><a href="/privacy">Privacy Policy</a> | <a href="/terms">Terms of Service</a> | <a href="/refund-policy">Refund Policy</a></p>
    `,
  },

  '/refund-policy': {
    title: 'Refund and Cancellation Policy | TrendScout',
    description: 'TrendScout refund and cancellation policy. Free trial, cancellation, refund terms, and billing information. Last updated March 2026.',
    canonical: '/refund-policy',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Refund Policy' }])],
    body: `
      <h1>Refund and Cancellation Policy</h1>
      <p>Last updated: March 2026</p>
      <h2>Free trial</h2>
      <p>Paid plans include a 7-day free trial. You will not be charged during the trial period. If you cancel before the trial ends, no payment will be taken.</p>
      <h2>Cancellation</h2>
      <p>Cancel your subscription at any time from your account settings. You retain access until the end of your billing period. No cancellation fees.</p>
      <h2>Refunds</h2>
      <p>If you are not satisfied within the first 7 days of a paid subscription, contact us at <a href="mailto:info@trendscout.click">info@trendscout.click</a> and we will arrange a refund. After the first 7 days, cancellations take effect at the end of the billing period.</p>
      <h2>Annual plans</h2>
      <p>Annual subscriptions are billed once per year. Refund requests within the first 14 days are handled on a case-by-case basis.</p>
      <h2>Contact</h2>
      <p>For billing questions, contact <a href="mailto:info@trendscout.click">info@trendscout.click</a>.</p>
      <p><a href="/terms">Terms of Service</a> | <a href="/privacy">Privacy Policy</a> | <a href="/contact">Contact</a></p>
    `,
  },

  '/methodology': {
    title: 'Scoring Methodology | TrendScout — How We Score Products',
    description: 'Understand how TrendScout scores products. Transparent methodology covering our 7-signal model, data sources, and scoring approach.',
    canonical: '/methodology',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Methodology' }])],
    body: `
      <h1>Scoring Methodology</h1>
      <p>TrendScout uses a transparent, data-driven methodology to score products for UK commercial viability. Here is how it works.</p>
      <h2>The 7-signal model</h2>
      <p>Every product is evaluated across 7 weighted signals: trend momentum, market saturation, margin potential, shipping practicality, return risk, channel fit, and UK market suitability.</p>
      <h2>Data sources</h2>
      <p>We aggregate signals from ecommerce platforms (Amazon, Shopify, TikTok Shop), search trend data, social media engagement metrics, advertising data, and market intelligence sources.</p>
      <h2>UK-specific adjustments</h2>
      <p>Unlike global tools, TrendScout applies UK-specific adjustments: 20% VAT impact on margins, UK shipping cost estimates, UK consumer demand validation, and UK platform competition data.</p>
      <p><a href="/uk-product-viability-score">UK Viability Score explained</a> | <a href="/sample-product-analysis">See a sample analysis</a> | <a href="/accuracy">Accuracy and limitations</a></p>
    `,
  },

  '/accuracy': {
    title: 'Accuracy and Limitations | TrendScout',
    description: 'Understand the accuracy and limitations of TrendScout product scores. Honest assessment of what our data can and cannot tell you.',
    canonical: '/accuracy',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Accuracy' }])],
    body: `
      <h1>Accuracy and Limitations</h1>
      <p>TrendScout provides data-driven product intelligence to help you make better decisions. Here is what our scores can and cannot do.</p>
      <h2>What scores tell you</h2>
      <p>Scores reflect the current data-driven assessment of a product's commercial potential in the UK market. They are based on multiple real-time signals and are updated daily.</p>
      <h2>What scores do not guarantee</h2>
      <p>No tool can guarantee commercial success. Scores help you make better-informed decisions and avoid obviously poor product choices, but success depends on execution, timing, marketing, and many other factors.</p>
      <p><a href="/methodology">Full methodology</a> | <a href="/sample-product-analysis">See sample analysis</a></p>
    `,
  },

  '/blog': {
    title: 'Blog | TrendScout — UK Ecommerce Product Research Insights',
    description: 'UK ecommerce product research insights, guides, and updates from TrendScout.',
    canonical: '/blog',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Blog' }])],
    body: `
      <h1>TrendScout Blog</h1>
      <p>UK ecommerce product research insights, guides, and platform updates.</p>
      <p><a href="/">Home</a> | <a href="/trending-products">Trending Products</a> | <a href="/tools">Free Tools</a></p>
    `,
  },

  '/changelog': {
    title: 'Changelog | TrendScout — Platform Updates',
    description: 'TrendScout platform changelog. See what features and improvements we have shipped recently.',
    canonical: '/changelog',
    schema: [breadcrumb([{ name: 'Home', url: '/' }, { name: 'Changelog' }])],
    body: `
      <h1>Changelog</h1>
      <p>Platform updates and new features.</p>
      <p><a href="/">Home</a> | <a href="/features">Features</a></p>
    `,
  },

};

// ═══ Alternate route mappings (share content with canonical) ═══
const ALIASES = {
  '/for-shopify': '/for-shopify-sellers',
  '/for-amazon-uk': '/for-amazon-uk-sellers',
  '/dropshipping-product-research-uk': '/dropshipping-uk',
  '/uk-ecommerce-trend-analysis': '/trend-analysis-uk',
};

module.exports = { PAGES, ALIASES, SITE, commonLinks };
