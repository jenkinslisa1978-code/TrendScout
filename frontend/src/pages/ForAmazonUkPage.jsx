import React from 'react';
import SeoLandingTemplate from '@/components/SeoLandingTemplate';
import { ShoppingBag, Search, TrendingUp, PoundSterling, Shield, Layers, Target, BarChart3 } from 'lucide-react';

export default function ForAmazonUkPage() {
  return (
    <SeoLandingTemplate
      headline="Product research for Amazon UK sellers"
      subtitle="Discover products gaining demand on Amazon.co.uk before the category gets crowded. TrendScout helps Amazon UK sellers validate product opportunities with UK-specific data."
      intro={[
        'Selling on Amazon UK is competitive. By the time a product hits the best-seller lists, the window of opportunity has already narrowed. The sellers who profit most are those who spot demand early — before saturation peaks.',
        'TrendScout monitors multi-channel trends to identify products gaining traction. Combined with UK-specific margin analysis and competition data, it helps Amazon UK sellers make faster, better-informed sourcing decisions.',
        'Unlike Amazon-only tools that focus on BSR and keyword volume, TrendScout looks at cross-channel signals — giving you an edge by showing demand before it fully materialises on Amazon.',
      ]}
      features={[
        { icon: ShoppingBag, title: 'Amazon UK market intelligence', desc: 'Track products gaining traction on Amazon.co.uk alongside signals from other channels that predict future Amazon demand.' },
        { icon: TrendingUp, title: 'Early trend detection', desc: 'Spot products trending on TikTok and Google before they saturate Amazon. Get in early while margins are still healthy.' },
        { icon: PoundSterling, title: 'UK margin estimation', desc: 'Calculate estimated margins after FBA fees, UK shipping, VAT, and supplier costs. Know the numbers before you commit.' },
        { icon: Shield, title: 'Saturation scoring', desc: 'See how many sellers are already listing this product on Amazon UK. Avoid categories that are already overcrowded.' },
        { icon: Target, title: 'Competition analysis', desc: 'Understand pricing strategies, listing quality, and review counts of existing Amazon UK competitors.' },
        { icon: BarChart3, title: 'Demand validation', desc: 'Cross-reference Amazon search trends with TikTok engagement and Google search volume for stronger demand signals.' },
      ]}
      steps={[
        { title: 'Discover cross-channel trends', desc: 'Find products trending across TikTok, Google, and social before Amazon saturation.' },
        { title: 'Check Amazon UK saturation', desc: 'See how many sellers are already active and how crowded the category is.' },
        { title: 'Estimate UK margins', desc: 'Factor in FBA fees, VAT, shipping, and realistic pricing for the UK market.' },
        { title: 'Decide whether to source', desc: 'Use launch scores and competitive data to make an informed go/no-go decision.' },
      ]}
      ukPoints={[
        'FBA UK fees are factored into margin calculations, not just US FBA estimates.',
        'Product demand is validated against UK-specific search and social data.',
        'Saturation is measured on Amazon.co.uk specifically, not Amazon.com.',
        'Seasonal demand patterns account for UK buying cycles and holidays.',
      ]}
      faqs={[
        { q: 'Is TrendScout a replacement for Jungle Scout?', a: 'TrendScout takes a different approach. While Jungle Scout focuses on Amazon keyword data, TrendScout monitors multi-channel trends to identify products before they fully saturate Amazon. It is best used as a complementary tool or an alternative for UK-focused sellers who need cross-channel intelligence.' },
        { q: 'Does TrendScout track Amazon BSR?', a: 'TrendScout focuses on cross-channel trend signals rather than raw BSR data. The value is in identifying products gaining demand across multiple channels — which often predicts future Amazon performance.' },
        { q: 'Can I use this for private label products?', a: 'Yes. The trend detection, saturation analysis, and margin estimation features are useful for both private label and arbitrage/wholesale sellers on Amazon UK.' },
        { q: 'How is this different from Helium 10?', a: 'Helium 10 is an Amazon-specific keyword and listing optimisation tool. TrendScout focuses on cross-channel product discovery and UK-specific viability analysis. They solve different problems and can work well together.' },
      ]}
      ctaText="Find your next Amazon UK product"
      relatedLinks={[
        { href: '/uk-product-research', label: 'UK Product Research' },
        { href: '/for-shopify', label: 'For Shopify Sellers' },
        { href: '/for-tiktok-shop-uk', label: 'For TikTok Shop UK' },
        { href: '/compare/jungle-scout-vs-trendscout', label: 'vs Jungle Scout' },
        { href: '/pricing', label: 'Pricing' },
      ]}
    />
  );
}
