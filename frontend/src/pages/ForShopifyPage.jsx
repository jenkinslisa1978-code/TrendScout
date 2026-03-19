import React from 'react';
import SeoLandingTemplate from '@/components/SeoLandingTemplate';
import { Store, Search, TrendingUp, PoundSterling, Zap, Shield, Package, Layers } from 'lucide-react';

export default function ForShopifyPage() {
  return (
    <SeoLandingTemplate
      headline="Product research for Shopify UK sellers"
      subtitle="Find trending products you can actually sell on your Shopify store. TrendScout helps Shopify sellers discover, validate, and launch products faster — with UK margins and competition already calculated."
      intro={[
        'Running a Shopify store in the UK means competing for attention in an increasingly crowded market. The difference between a profitable product and a wasted ad budget often comes down to research quality.',
        'TrendScout gives Shopify sellers the product intelligence they need: which products are trending, how saturated the market is, what margins look like after UK costs, and whether the product fits the Shopify sales model.',
        'Plus, you can push products directly from TrendScout to your Shopify store as drafts — complete with title, description, pricing, and images.',
      ]}
      features={[
        { icon: Store, title: 'Push to Shopify', desc: 'Found a product worth testing? Push it directly to your Shopify store as a draft listing with one click.' },
        { icon: Search, title: 'Trending product discovery', desc: 'Browse products gaining traction across TikTok, Amazon, and Google Trends. Updated daily.' },
        { icon: PoundSterling, title: 'UK margin calculator', desc: 'See estimated margins after supplier costs, UK shipping, VAT, and Shopify platform fees.' },
        { icon: Shield, title: 'Competition analysis', desc: 'Check how many Shopify stores are already selling this product and how crowded the ad space is.' },
        { icon: TrendingUp, title: 'Launch scores', desc: 'Every product scored 0-100 across 7 signals so you can quickly prioritise what to test.' },
        { icon: Zap, title: 'AI ad creative ideas', desc: 'Get AI-generated ad angles and audience targeting suggestions for your Shopify product pages.' },
      ]}
      steps={[
        { title: 'Browse trending products', desc: 'Explore products with strong trend signals suited to Shopify stores.' },
        { title: 'Check UK viability', desc: 'Evaluate margins, saturation, and competition for the UK market.' },
        { title: 'Push to your store', desc: 'Send products to Shopify as drafts with pricing, images, and descriptions.' },
        { title: 'Launch and test', desc: 'Use AI ad suggestions and competitor data to run smarter test campaigns.' },
      ]}
      ukPoints={[
        'Margin calculations include Shopify transaction fees, UK shipping, and 20% VAT.',
        'Competition data shows UK-specific Shopify store saturation levels.',
        'Product suitability scored specifically for the Shopify sales model.',
        'One-click push to Shopify saves hours of manual product listing setup.',
      ]}
      faqs={[
        { q: 'Do I need to connect my Shopify store?', a: 'Connecting your store unlocks one-click product push and export features. You can still use TrendScout for research without connecting, but the push-to-store feature requires a connection.' },
        { q: 'Does this work with Shopify UK?', a: 'Yes. TrendScout is built specifically for UK sellers. All pricing, margin, and competition data is calculated for the UK market.' },
        { q: 'What Shopify plans does this work with?', a: 'TrendScout works with all Shopify plans. The push-to-store feature uses the Shopify Admin API and works with Basic, Shopify, and Advanced plans.' },
        { q: 'Can I use this for dropshipping on Shopify?', a: 'Absolutely. TrendScout includes supplier data, lead times, and margin estimates that are particularly useful for Shopify dropshipping businesses.' },
      ]}
      ctaText="Find products for your Shopify store"
      relatedLinks={[
        { href: '/uk-product-research', label: 'UK Product Research' },
        { href: '/for-amazon-uk', label: 'For Amazon UK' },
        { href: '/for-tiktok-shop-uk', label: 'For TikTok Shop UK' },
        { href: '/compare/jungle-scout-vs-trendscout', label: 'vs Jungle Scout' },
        { href: '/pricing', label: 'Pricing' },
      ]}
    />
  );
}
