import React from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { 
  TrendingUp, 
  Search, 
  BarChart3, 
  Zap, 
  Shield, 
  Clock,
  Check,
  ArrowRight
} from 'lucide-react';

const features = [
  {
    icon: TrendingUp,
    title: 'Trend Detection',
    description: 'Identify rising products before they go viral with our AI-powered trend scoring system.'
  },
  {
    icon: Search,
    title: 'Product Discovery',
    description: 'Browse thousands of trending products across multiple categories with detailed analytics.'
  },
  {
    icon: BarChart3,
    title: 'Market Analysis',
    description: 'Understand competition levels, margin potential, and market saturation at a glance.'
  },
  {
    icon: Zap,
    title: 'AI Insights',
    description: 'Get intelligent summaries and recommendations for each product opportunity.'
  },
  {
    icon: Shield,
    title: 'Verified Suppliers',
    description: 'Access pre-vetted supplier links with competitive pricing and reliable shipping.'
  },
  {
    icon: Clock,
    title: 'Real-Time Updates',
    description: 'Stay ahead with daily updates on trending products and market changes.'
  }
];

const pricingPlans = [
  {
    name: 'Starter',
    price: '19',
    description: 'Perfect for beginners exploring dropshipping',
    features: [
      'Access to 50 trending products',
      'Basic trend scores',
      'Category filtering',
      'Save up to 10 products',
      'Email support'
    ],
    cta: 'Start Free Trial',
    popular: false
  },
  {
    name: 'Pro',
    price: '49',
    description: 'For serious dropshippers scaling their business',
    features: [
      'Unlimited product access',
      'Advanced trend analytics',
      'AI-powered insights',
      'Unlimited saved products',
      'Supplier links',
      'Priority support',
      'Export to CSV'
    ],
    cta: 'Start Free Trial',
    popular: true
  },
  {
    name: 'Elite',
    price: '99',
    description: 'For agencies and power sellers',
    features: [
      'Everything in Pro',
      'Early trend alerts',
      'API access',
      'White-label reports',
      'Dedicated account manager',
      'Custom integrations',
      'Team collaboration'
    ],
    cta: 'Contact Sales',
    popular: false
  }
];

export default function LandingPage() {
  return (
    <LandingLayout>
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-indigo-100/50 blur-3xl" />
        </div>
        
        <div className="mx-auto max-w-7xl px-6 pt-24 pb-20 lg:px-8 lg:pt-32">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-indigo-50 px-4 py-1.5 text-sm font-medium text-indigo-700">
              <Zap className="h-4 w-4" />
              AI-Powered Product Research
            </div>
            <h1 className="font-manrope text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              Find winning products{' '}
              <span className="text-indigo-600">before they go viral</span>
            </h1>
            <p className="mt-6 text-lg text-slate-600 leading-relaxed">
              TrendScout analyzes millions of data points to surface the most promising 
              dropshipping opportunities. Stop guessing, start winning.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/signup">
                <Button 
                  size="lg" 
                  data-testid="hero-cta-btn"
                  className="bg-indigo-600 hover:bg-indigo-700 text-base px-8 h-12 font-semibold"
                >
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <a href="#features">
                <Button 
                  variant="outline" 
                  size="lg"
                  className="text-base px-8 h-12"
                >
                  See How It Works
                </Button>
              </a>
            </div>
            <p className="mt-4 text-sm text-slate-500">
              No credit card required • 7-day free trial
            </p>
          </div>

          {/* Dashboard Preview */}
          <div className="mt-16 relative">
            <div className="absolute inset-0 bg-gradient-to-t from-[#F8FAFC] via-transparent to-transparent z-10 pointer-events-none" />
            <div className="mx-auto max-w-5xl rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-slate-200/50 overflow-hidden">
              <div className="bg-slate-100 px-4 py-3 flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-amber-400" />
                  <div className="w-3 h-3 rounded-full bg-emerald-400" />
                </div>
                <div className="flex-1 flex justify-center">
                  <div className="bg-white rounded-md px-4 py-1 text-xs text-slate-400">
                    trendscout.app/dashboard
                  </div>
                </div>
              </div>
              <div className="p-6 bg-[#F8FAFC]">
                {/* Mock dashboard */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                  {['Total Products', 'Avg Trend Score', 'High Opportunity', 'Rising Trends'].map((label, i) => (
                    <div key={label} className="bg-white rounded-xl border border-slate-200 p-4">
                      <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
                      <p className="mt-1 font-mono text-2xl font-semibold text-slate-900">
                        {['2,847', '76', '342', '89'][i]}
                      </p>
                    </div>
                  ))}
                </div>
                <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                  <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
                    <p className="text-sm font-semibold text-slate-700">Trending Products</p>
                  </div>
                  <div className="divide-y divide-slate-100">
                    {['Portable Neck Fan', 'Sunset Projection Lamp', 'Smart Water Bottle'].map((name, i) => (
                      <div key={name} className="px-4 py-3 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-slate-100" />
                          <div>
                            <p className="text-sm font-medium text-slate-900">{name}</p>
                            <p className="text-xs text-slate-500">Electronics</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="font-mono text-sm font-semibold text-emerald-600">
                            {[87, 94, 76][i]}
                          </span>
                          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                            {['rising', 'early', 'rising'][i]}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-manrope text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Everything you need to find winning products
            </h2>
            <p className="mt-4 text-lg text-slate-600">
              Powerful tools and insights to help you make data-driven decisions
            </p>
          </div>
          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <div 
                key={feature.title}
                className="group relative rounded-2xl border border-slate-200 bg-white p-8 transition-all duration-300 hover:border-indigo-200 hover:shadow-lg hover:shadow-indigo-100/50"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 transition-colors group-hover:bg-indigo-600 group-hover:text-white">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="mt-6 font-manrope text-lg font-semibold text-slate-900">
                  {feature.title}
                </h3>
                <p className="mt-2 text-slate-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 bg-[#F8FAFC]">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-manrope text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Simple, transparent pricing
            </h2>
            <p className="mt-4 text-lg text-slate-600">
              Choose the plan that fits your business. Cancel anytime.
            </p>
          </div>
          <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-3">
            {pricingPlans.map((plan) => (
              <div
                key={plan.name}
                data-testid={`pricing-card-${plan.name.toLowerCase()}`}
                className={`relative rounded-2xl border bg-white p-8 transition-all duration-300 ${
                  plan.popular 
                    ? 'border-indigo-600 shadow-xl shadow-indigo-100/50 scale-105' 
                    : 'border-slate-200 hover:border-slate-300 hover:shadow-lg'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="inline-flex items-center rounded-full bg-indigo-600 px-4 py-1 text-xs font-semibold text-white">
                      Most Popular
                    </span>
                  </div>
                )}
                <div className="text-center">
                  <h3 className="font-manrope text-xl font-bold text-slate-900">{plan.name}</h3>
                  <p className="mt-2 text-sm text-slate-500">{plan.description}</p>
                  <div className="mt-6">
                    <span className="font-manrope text-5xl font-extrabold text-slate-900">£{plan.price}</span>
                    <span className="text-slate-500">/month</span>
                  </div>
                </div>
                <ul className="mt-8 space-y-4">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <Check className="h-5 w-5 flex-shrink-0 text-indigo-600" />
                      <span className="text-sm text-slate-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link to="/signup" className="block mt-8">
                  <Button 
                    className={`w-full h-11 font-semibold ${
                      plan.popular 
                        ? 'bg-indigo-600 hover:bg-indigo-700' 
                        : 'bg-slate-900 hover:bg-slate-800'
                    }`}
                    data-testid={`pricing-cta-${plan.name.toLowerCase()}`}
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="rounded-3xl bg-indigo-600 px-8 py-16 sm:px-16 text-center">
            <h2 className="font-manrope text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Ready to find your next winning product?
            </h2>
            <p className="mt-4 text-lg text-indigo-100">
              Join thousands of successful dropshippers using TrendScout
            </p>
            <div className="mt-8">
              <Link to="/signup">
                <Button 
                  size="lg" 
                  className="bg-white text-indigo-600 hover:bg-indigo-50 text-base px-8 h-12 font-semibold"
                  data-testid="final-cta-btn"
                >
                  Start Your Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </LandingLayout>
  );
}
