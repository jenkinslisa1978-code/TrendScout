import React from 'react';
import SeoLandingTemplate from '@/components/SeoLandingTemplate';
import { Search, Shield, PoundSterling, TrendingUp, Target, Layers, Zap, Truck } from 'lucide-react';

export default function UkProductResearchPage() {
  return (
    <SeoLandingTemplate
      headline="UK product research for ecommerce sellers"
      subtitle="Find products that can actually sell profitably in the UK. TrendScout combines multi-channel trend detection with UK-specific commercial analysis to help you make smarter product decisions."
      intro={[
        'Product research for the UK market is fundamentally different from the US. Higher VAT, different shipping economics, smaller addressable markets, and local consumer behaviour all change whether a product is commercially viable.',
        'TrendScout is built specifically for UK sellers. Instead of just showing you trending products, we help you evaluate whether those products can make money in the UK — factoring in costs, competition, and channel fit that generic tools ignore.',
        'Whether you sell on Shopify, Amazon.co.uk, or TikTok Shop UK, TrendScout gives you the intelligence to validate product ideas before you waste money on ads or inventory.',
      ]}
      features={[
        { icon: Search, title: 'Multi-channel trend detection', desc: 'Spot products gaining traction across TikTok, Amazon, Shopify stores, and Google Trends — all in one dashboard.' },
        { icon: Shield, title: 'Saturation analysis', desc: 'See how many sellers are already active, how crowded the ad space is, and whether there is still room for a new entrant.' },
        { icon: PoundSterling, title: 'UK margin estimation', desc: 'Estimate profit margins after factoring in supplier costs, UK shipping, 20% VAT, platform fees, and realistic returns.' },
        { icon: TrendingUp, title: '7-signal launch score', desc: 'Every product is scored 0-100 based on trend momentum, saturation, margin potential, ad opportunity, and more.' },
        { icon: Target, title: 'Competition intelligence', desc: 'Analyse competitor stores, their pricing strategies, product range, and market positioning.' },
        { icon: Layers, title: 'Channel suitability', desc: 'Understand which UK sales channels (Shopify, Amazon.co.uk, TikTok Shop) are best suited for each product.' },
        { icon: Zap, title: 'AI ad angle suggestions', desc: 'Get AI-generated ad creative ideas and target audience suggestions for every product you research.' },
        { icon: Truck, title: 'Supplier data', desc: 'Access supplier information including costs, lead times, minimum orders, and shipping options to the UK.' },
      ]}
      steps={[
        { title: 'Browse trending products', desc: 'Explore products gaining traction across multiple channels, filtered by category and score.' },
        { title: 'Evaluate UK viability', desc: 'Check margins, saturation, VAT impact, and shipping practicality for each product.' },
        { title: 'Compare and shortlist', desc: 'Use launch scores and signal breakdowns to prioritise the best opportunities.' },
        { title: 'Launch with confidence', desc: 'Move forward with data, not guesswork. Ad angles, supplier data, and competitive context included.' },
      ]}
      ukPoints={[
        '20% VAT is factored into all margin calculations — not an afterthought.',
        'Shipping cost estimates reflect real UK delivery economics, not US averages.',
        'Saturation levels are measured for the UK market specifically, not globally.',
        'Product categories are evaluated against UK consumer demand patterns.',
        'Channel fit considers the specific dynamics of Shopify UK, Amazon.co.uk, and TikTok Shop UK.',
      ]}
      faqs={[
        { q: 'How is UK product research different from generic tools?', a: 'Generic tools typically focus on the US market. They do not account for UK VAT, local shipping costs, UK-specific competition levels, or the smaller addressable market. TrendScout is built from the ground up for UK economics.' },
        { q: 'What types of products does TrendScout track?', a: 'We track products across all major ecommerce categories including electronics, home and kitchen, beauty, fashion, pet supplies, fitness, and more. Products are added as they gain multi-channel traction.' },
        { q: 'Can I use TrendScout if I sell on multiple channels?', a: 'Yes. TrendScout evaluates products across Shopify, Amazon.co.uk, and TikTok Shop UK. You can see which channel is most suitable for each product.' },
        { q: 'How much does it cost?', a: 'TrendScout has a free tier and paid plans starting from £19/month. See the pricing page for full details.' },
      ]}
      ctaText="Start researching UK products today"
      canonical="/uk-product-research"
      metaDesc="UK product research for ecommerce sellers. Multi-channel trend detection, saturation analysis, and UK-specific margin estimation for Shopify, Amazon UK, and TikTok Shop."
      relatedLinks={[
        { href: '/for-shopify', label: 'For Shopify Sellers' },
        { href: '/for-amazon-uk', label: 'For Amazon UK' },
        { href: '/for-tiktok-shop-uk', label: 'For TikTok Shop UK' },
        { href: '/how-it-works', label: 'How It Works' },
        { href: '/pricing', label: 'Pricing' },
      ]}
    />
  );
}
