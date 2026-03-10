import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ShoppingCart, 
  Check, 
  Star, 
  Truck, 
  Shield, 
  RefreshCw,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Loader2
} from 'lucide-react';
import { getStorePreview } from '@/services/storeService';

export default function StorePreviewPage() {
  const { storeId } = useParams();
  const [store, setStore] = useState(null);
  const [product, setProduct] = useState(null);
  const [allProducts, setAllProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedFaq, setExpandedFaq] = useState(null);

  useEffect(() => {
    loadPreview();
  }, [storeId]);

  const loadPreview = async () => {
    setLoading(true);
    const data = await getStorePreview(storeId);
    if (data.store) {
      setStore(data.store);
      setProduct(data.featured_product);
      setAllProducts(data.all_products || []);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-slate-600" />
      </div>
    );
  }

  if (!store) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-slate-900">Store not found</h1>
          <p className="mt-2 text-slate-600">This store may have been removed or is not published.</p>
        </div>
      </div>
    );
  }

  const branding = store.branding || {};
  const primaryColor = branding.primary_color || '#0f172a';
  const secondaryColor = branding.secondary_color || '#3b82f6';
  const accentColor = branding.accent_color || '#10b981';

  return (
    <div className="min-h-screen bg-white">
      {/* Preview Banner */}
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-center text-sm text-amber-800">
        This is a preview of your store. 
        <Link to={`/stores/${storeId}`} className="ml-2 font-medium underline">
          Back to Editor
        </Link>
      </div>

      {/* Header */}
      <header 
        className="border-b"
        style={{ backgroundColor: primaryColor }}
      >
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div 
              className="w-10 h-10 rounded-lg flex items-center justify-center text-lg font-bold"
              style={{ backgroundColor: secondaryColor, color: 'white' }}
            >
              {store.name?.charAt(0)}
            </div>
            <div>
              <h1 className="font-bold text-white text-lg">{store.name}</h1>
              <p className="text-xs text-white/70">{store.tagline}</p>
            </div>
          </div>
          <Button 
            variant="outline" 
            className="bg-white/10 border-white/20 text-white hover:bg-white/20"
          >
            <ShoppingCart className="h-4 w-4 mr-2" />
            Cart (0)
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 px-4" style={{ backgroundColor: `${primaryColor}08` }}>
        <div className="max-w-4xl mx-auto text-center">
          <Badge className="mb-4" style={{ backgroundColor: secondaryColor, color: 'white' }}>
            Trending Now
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: primaryColor }}>
            {store.headline || `Welcome to ${store.name}`}
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            {store.tagline || 'Discover amazing products curated just for you'}
          </p>
        </div>
      </section>

      {/* Featured Product */}
      {product && (
        <section className="py-16 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-2 gap-12 items-start">
              {/* Product Image Placeholder */}
              <div className="aspect-square rounded-2xl bg-slate-100 flex items-center justify-center">
                {product.image_url ? (
                  <img 
                    src={product.image_url} 
                    alt={product.title}
                    className="w-full h-full object-cover rounded-2xl"
                  />
                ) : (
                  <div className="text-center">
                    <div className="w-24 h-24 mx-auto mb-4 rounded-xl bg-slate-200" />
                    <p className="text-slate-400">Product Image</p>
                  </div>
                )}
              </div>

              {/* Product Details */}
              <div className="space-y-6">
                <div>
                  <Badge 
                    className="mb-3"
                    style={{ backgroundColor: `${accentColor}20`, color: accentColor }}
                  >
                    {product.category}
                  </Badge>
                  <h3 className="text-3xl font-bold text-slate-900 mb-2">
                    {product.title}
                  </h3>
                  <div className="flex items-center gap-2 mb-4">
                    <div className="flex">
                      {[1,2,3,4,5].map((star) => (
                        <Star 
                          key={star} 
                          className="h-5 w-5" 
                          style={{ color: '#fbbf24', fill: '#fbbf24' }} 
                        />
                      ))}
                    </div>
                    <span className="text-sm text-slate-600">(127 reviews)</span>
                  </div>
                </div>

                {/* Price */}
                <div className="flex items-baseline gap-3">
                  <span className="text-4xl font-bold" style={{ color: primaryColor }}>
                    ${product.price?.toFixed(2)}
                  </span>
                  {product.compare_at_price > product.price && (
                    <span className="text-xl text-slate-400 line-through">
                      ${product.compare_at_price?.toFixed(2)}
                    </span>
                  )}
                  {product.compare_at_price > product.price && (
                    <Badge style={{ backgroundColor: accentColor, color: 'white' }}>
                      Save {Math.round((1 - product.price / product.compare_at_price) * 100)}%
                    </Badge>
                  )}
                </div>

                {/* Description */}
                <p className="text-slate-600 leading-relaxed">
                  {product.description?.slice(0, 300)}...
                </p>

                {/* Bullet Points */}
                <ul className="space-y-3">
                  {product.bullet_points?.map((point, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <div 
                        className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                        style={{ backgroundColor: `${accentColor}20` }}
                      >
                        <Check className="h-4 w-4" style={{ color: accentColor }} />
                      </div>
                      <span className="text-slate-700">{point}</span>
                    </li>
                  ))}
                </ul>

                {/* CTA Button */}
                <Button 
                  size="lg"
                  className="w-full text-lg py-6"
                  style={{ backgroundColor: secondaryColor }}
                  data-testid="add-to-cart-btn"
                >
                  <ShoppingCart className="h-5 w-5 mr-2" />
                  Add to Cart
                </Button>

                {/* Trust Badges */}
                <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                  <div className="text-center">
                    <Truck className="h-6 w-6 mx-auto mb-1 text-slate-400" />
                    <p className="text-xs text-slate-600">Free Shipping</p>
                  </div>
                  <div className="text-center">
                    <Shield className="h-6 w-6 mx-auto mb-1 text-slate-400" />
                    <p className="text-xs text-slate-600">Secure Checkout</p>
                  </div>
                  <div className="text-center">
                    <RefreshCw className="h-6 w-6 mx-auto mb-1 text-slate-400" />
                    <p className="text-xs text-slate-600">30-Day Returns</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* FAQ Section */}
      {store.faqs?.length > 0 && (
        <section className="py-16 px-4 bg-slate-50">
          <div className="max-w-3xl mx-auto">
            <h3 className="text-2xl font-bold text-center mb-8" style={{ color: primaryColor }}>
              Frequently Asked Questions
            </h3>
            <div className="space-y-4">
              {store.faqs.map((faq, i) => (
                <div 
                  key={i}
                  className="bg-white rounded-xl border border-slate-200 overflow-hidden"
                >
                  <button
                    onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                    className="w-full px-6 py-4 flex items-center justify-between text-left"
                  >
                    <span className="font-medium text-slate-900">{faq.question}</span>
                    {expandedFaq === i ? (
                      <ChevronUp className="h-5 w-5 text-slate-400" />
                    ) : (
                      <ChevronDown className="h-5 w-5 text-slate-400" />
                    )}
                  </button>
                  {expandedFaq === i && (
                    <div className="px-6 pb-4 text-slate-600">
                      {faq.answer}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="py-8 px-4 border-t">
        <div className="max-w-4xl mx-auto text-center text-sm text-slate-500">
          <p>&copy; {new Date().getFullYear()} {store.name}. All rights reserved.</p>
          <p className="mt-2">
            Powered by <span className="font-semibold text-indigo-600">ViralScout</span>
          </p>
        </div>
      </footer>
    </div>
  );
}
