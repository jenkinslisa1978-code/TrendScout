import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import {
  Flame, Zap, Clock, TrendingUp, Package, ChevronRight, Star,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const CATEGORY_IMAGES = {
  'Furniture': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&h=600&fit=crop',
  'Home Office Storage': 'https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&h=600&fit=crop',
  'Kitchen Storage': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&h=600&fit=crop',
  'Hand Tools': 'https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=600&h=600&fit=crop',
  'Beauty': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&h=600&fit=crop',
  'Electronics': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=600&h=600&fit=crop',
  'Pet Bowls': 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=600&fit=crop',
  'Vehicle Cams': 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=600&h=600&fit=crop',
  'Fashion': 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=600&h=600&fit=crop',
  'DIY & Tools': 'https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=600&h=600&fit=crop',
  'Garden & Outdoors': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=600&h=600&fit=crop',
  'Pet Supplies': 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=600&fit=crop',
  'Sports & Outdoors': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600&h=600&fit=crop',
  'Home & Kitchen': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&h=600&fit=crop',
  'Health & Fitness': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600&h=600&fit=crop',
  'Home Decor': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&h=600&fit=crop',
  'Baby & Kids': 'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=600&h=600&fit=crop',
  'Automotive': 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=600&h=600&fit=crop',
  'Kitchen': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&h=600&fit=crop',
  'Toys & Games': 'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=600&h=600&fit=crop',
  'default': 'https://images.unsplash.com/photo-1560393464-5c69a73c5770?w=600&h=600&fit=crop',
};

export default function DailyPicksSection() {
  const [picks, setPicks] = useState([]);
  const [date, setDate] = useState('');

  useEffect(() => {
    fetch(`${API_URL}/api/public/daily-picks`)
      .then(r => r.json())
      .then(data => {
        setPicks(data.picks || []);
        setDate(data.date || '');
      })
      .catch(() => {});
  }, []);

  if (picks.length === 0) return null;

  const formatDate = (d) => {
    if (!d) return '';
    const dt = new Date(d + 'T00:00:00');
    return dt.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });
  };

  return (
    <section className="mb-10" data-testid="daily-picks-section">
      <div className="flex items-center justify-between mb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-amber-100">
              <Star className="h-5 w-5 text-amber-500 fill-amber-400" />
            </div>
            <h2 className="font-manrope text-xl font-bold text-slate-900">
              Today's Picks
            </h2>
          </div>
          <p className="text-sm text-slate-500 mt-1 ml-9">
            {formatDate(date)} — Curated daily from our top-scoring products
          </p>
        </div>
        <Badge className="bg-amber-50 text-amber-700 border-amber-200 border text-xs rounded-full px-3">
          {picks.length} Products
        </Badge>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {picks.map((product) => {
          const score = product.launch_score || 0;
          const confidence = score >= 75 ? { label: 'High Confidence', icon: Flame, color: 'text-emerald-500 bg-emerald-50' }
            : score >= 50 ? { label: 'Emerging', icon: Zap, color: 'text-amber-500 bg-amber-50' }
            : { label: 'Experimental', icon: Clock, color: 'text-slate-500 bg-slate-50' };
          const CIcon = confidence.icon;

          return (
            <Link
              key={product.id}
              to={`/trending/${product.slug}`}
              className="group block bg-white rounded-xl border border-slate-100 overflow-hidden hover:border-indigo-200 hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5"
              data-testid={`daily-pick-${product.id}`}
            >
              <div className="relative h-28 bg-gradient-to-br from-slate-50 to-slate-100 overflow-hidden">
                {(product.image_url || CATEGORY_IMAGES[product.category] || CATEGORY_IMAGES['default']) ? (
                  <img
                    src={product.image_url || CATEGORY_IMAGES[product.category] || CATEGORY_IMAGES['default']}
                    alt={product.product_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Package className="h-8 w-8 text-slate-300" />
                  </div>
                )}
                <div className="absolute top-2 left-2 bg-white/90 backdrop-blur-sm rounded-full px-2 py-0.5">
                  <span className="font-mono text-sm font-bold text-indigo-600">{score}</span>
                </div>
              </div>

              <div className="p-3">
                <h3 className="text-sm font-semibold text-slate-900 line-clamp-1 group-hover:text-indigo-600 transition-colors">
                  {product.product_name}
                </h3>
                <div className="flex items-center gap-1.5 mt-1.5">
                  <span className={`inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full ${confidence.color}`}>
                    <CIcon className="h-2.5 w-2.5" />
                    {confidence.label}
                  </span>
                </div>
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-50">
                  <span className="text-emerald-600 text-xs font-semibold">{product.margin_percent}% margin</span>
                  <span className="text-xs text-indigo-500 font-medium flex items-center gap-0.5 group-hover:text-indigo-600">
                    View <ChevronRight className="h-3 w-3" />
                  </span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
