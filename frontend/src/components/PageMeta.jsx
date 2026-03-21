import React from 'react';
import { Helmet } from 'react-helmet-async';

/**
 * Reusable component for per-page SEO metadata + JSON-LD schema.
 * Usage: <PageMeta title="..." description="..." schema={[...]} />
 */
export default function PageMeta({ title, description, canonical, schema, ogImage, ogType }) {
  const siteUrl = 'https://trendscout.click';
  const fullCanonical = canonical ? `${siteUrl}${canonical}` : undefined;
  const fullTitle = title ? `${title} | TrendScout` : 'TrendScout | AI Product Research for UK Ecommerce Sellers';
  const desc = description || 'Find products that can actually sell in the UK. Discover trends, analyse competition, estimate margins, and launch faster across Shopify, TikTok Shop, and Amazon.co.uk.';

  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={desc} />
      {fullCanonical && <link rel="canonical" href={fullCanonical} />}
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={desc} />
      <meta property="og:type" content={ogType || 'website'} />
      {fullCanonical && <meta property="og:url" content={fullCanonical} />}
      {ogImage && <meta property="og:image" content={ogImage} />}
      <meta property="og:site_name" content="TrendScout" />
      <meta property="og:locale" content="en_GB" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={desc} />
      {schema && schema.map((s, i) => (
        <script key={i} type="application/ld+json">{JSON.stringify(s)}</script>
      ))}
    </Helmet>
  );
}

// ── Reusable schema builders ──

export const organizationSchema = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'TrendScout',
  legalName: 'TrendScout',
  url: 'https://trendscout.click',
  email: 'info@trendscout.click',
  description: 'AI product research and launch intelligence for UK ecommerce sellers.',
  address: {
    '@type': 'PostalAddress',
    addressCountry: 'GB',
  },
};

export const websiteSchema = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'TrendScout',
  url: 'https://trendscout.click',
  description: 'AI product research and launch intelligence for UK ecommerce sellers.',
  publisher: { '@type': 'Organization', name: 'TrendScout' },
};

export const softwareAppSchema = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'TrendScout',
  applicationCategory: 'BusinessApplication',
  operatingSystem: 'Web',
  url: 'https://trendscout.click',
  description: 'AI product research and launch intelligence for UK ecommerce sellers. Discover trending products, analyse competition, estimate UK profit margins, and make faster launch decisions.',
  offers: {
    '@type': 'AggregateOffer',
    priceCurrency: 'GBP',
    lowPrice: '0',
    highPrice: '79',
    offerCount: '4',
  },
  provider: { '@type': 'Organization', name: 'TrendScout' },
};

export function faqSchema(items) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map(({ q, a }) => ({
      '@type': 'Question',
      name: q,
      acceptedAnswer: { '@type': 'Answer', text: a },
    })),
  };
}

export function breadcrumbSchema(items) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: item.name,
      item: item.url ? `https://trendscout.click${item.url}` : undefined,
    })),
  };
}

export function webPageSchema(name, description, url) {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name,
    description,
    url: `https://trendscout.click${url}`,
    isPartOf: { '@type': 'WebSite', name: 'TrendScout', url: 'https://trendscout.click' },
    provider: { '@type': 'Organization', name: 'TrendScout' },
  };
}
