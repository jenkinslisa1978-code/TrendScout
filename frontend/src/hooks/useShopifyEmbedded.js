import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Detect if app is running inside Shopify Admin iframe.
 * Shopify passes `shop` and `host` query params when loading embedded apps.
 */
export default function useShopifyEmbedded() {
  const location = useLocation();

  return useMemo(() => {
    const params = new URLSearchParams(location.search);
    const shop = params.get('shop') || '';
    const host = params.get('host') || '';
    const embedded = !!(shop && host);

    return { embedded, shop, host };
  }, [location.search]);
}
