import React from 'react';
import SeoLandingTemplate from '@/components/SeoLandingTemplate';
import { TrendingUp, Search, PoundSterling, Shield, Zap, Target, Layers, Globe } from 'lucide-react';

export default function WinningProductsUkPage() {
  return (
    <SeoLandingTemplate
      headline="Winning products UK: find what actually sells"
      subtitle="Stop guessing which products to sell in the UK. TrendScout identifies products with real commercial potential in the UK market — not just viral videos or trending hashtags."
      intro={[
        'The phrase "winning products" gets thrown around constantly in ecommerce communities, but for UK sellers, what counts as a winner is different. A product needs to be profitable after UK-specific costs, have manageable competition in the UK market, and be practical to fulfil for UK customers.',
        'TrendScout goes beyond basic trend lists by scoring every product on UK commercial viability. Our UK Product Viability Score measures margin potential, saturation, shipping practicality, and channel fit specifically for the UK market.',
        'Whether you sell on Shopify, Amazon.co.uk, or TikTok Shop UK, TrendScout helps you find products that can actually make money — not just get likes.',
      ]}
      features={[
        { icon: TrendingUp, title: 'UK Viability Score', desc: 'Every product scored 0-100 on UK commercial viability, not just popularity or trend status.' },
        { icon: Search, title: 'Multi-channel detection', desc: 'Products identified across TikTok, Amazon, Shopify stores, and Google Trends simultaneously.' },
        { icon: PoundSterling, title: 'Profit estimation', desc: 'See estimated margins after supplier costs, UK shipping, VAT, and platform fees before you invest.' },
        { icon: Shield, title: 'Competition check', desc: 'Understand how saturated a product category is in the UK before entering.' },
        { icon: Target, title: 'Channel fit analysis', desc: 'Know which UK sales channel suits each product: Shopify, Amazon.co.uk, or TikTok Shop.' },
        { icon: Zap, title: 'Launch intelligence', desc: 'Get AI ad suggestions, target audience ideas, and competitive insights for each product.' },
      ]}
      steps={[
        { title: 'Browse winning products', desc: 'Explore products with high UK Viability Scores, updated daily across categories.' },
        { title: 'Validate before investing', desc: 'Check margins, saturation, and competition data specific to the UK market.' },
        { title: 'Choose your channel', desc: 'See which sales channel is best suited for each product.' },
        { title: 'Launch smarter', desc: 'Use data and AI suggestions to test products with more confidence and less waste.' },
      ]}
      ukPoints={[
        'UK Viability Score separates genuinely profitable products from viral noise.',
        'Margins calculated with UK-specific costs: 20% VAT, local shipping, platform fees.',
        'Competition measured in the UK market specifically, not globally.',
        'Products evaluated against UK consumer behaviour and demand patterns.',
        'Channel recommendations consider Shopify UK, Amazon.co.uk, and TikTok Shop UK dynamics.',
      ]}
      faqs={[
        { q: 'What makes a product "winning" in the UK?', a: 'A winning product in the UK has genuine demand, manageable competition, healthy margins after VAT and shipping, and practical fulfilment. TrendScout measures these factors with the UK Viability Score.' },
        { q: 'How is this different from free product lists?', a: 'Free lists typically show globally trending products without UK-specific analysis. TrendScout scores each product on UK viability, including margin estimation, saturation levels, and channel suitability.' },
        { q: 'How often are products updated?', a: 'Products and scores are updated daily. New products are added as they gain multi-channel traction.' },
        { q: 'Can I use this for Amazon UK and Shopify?', a: 'Yes. TrendScout evaluates products across all major UK ecommerce channels and recommends which channel suits each product.' },
      ]}
      ctaText="Find winning products for the UK market"
      canonical="/winning-products-uk"
      metaDesc="Find winning products for the UK market. TrendScout identifies products with real commercial potential using UK Viability Scores and margin analysis."
      relatedLinks={[
        { href: '/uk-product-research', label: 'UK Product Research' },
        { href: '/uk-product-viability-score', label: 'UK Viability Score' },
        { href: '/dropshipping-product-research-uk', label: 'UK Dropshipping' },
        { href: '/product-validation-uk', label: 'Product Validation UK' },
        { href: '/pricing', label: 'Pricing' },
      ]}
    />
  );
}
