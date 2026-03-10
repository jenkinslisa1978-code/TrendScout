import React from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import ProductOfTheWeek from '@/components/common/ProductOfTheWeek';
import NewsletterCapture from '@/components/common/NewsletterCapture';
import { Button } from '@/components/ui/button';
import { 
  TrendingUp, 
  Rocket, 
  Store, 
  Zap, 
  Clock,
  Check,
  ArrowRight,
  Trophy,
  Package
} from 'lucide-react';

const features = [
  {
    icon: Trophy,
    title: 'Find Winning Products',
    description: 'Our AI identifies products with the highest win scores based on trends, momentum, and proven success data.'
  },
  {
    icon: Rocket,
    title: 'Launch in Minutes',
    description: 'Generate your complete store with product descriptions, pricing, and branding - ready for Shopify.'
  },
  {
    icon: TrendingUp,
    title: 'Early Trend Detection',
    description: 'Get in before saturation. Spot exploding products before your competition does.'
  },
  {
    icon: Store,
    title: 'Store Builder',
    description: 'One-click store creation with AI-generated content, branding, and Shopify-ready export.'
  },
  {
    icon: Package,
    title: 'Proven Winners',
    description: 'See which products are already working for other sellers with real success tracking data.'
  },
  {
    icon: Clock,
    title: 'Daily Updates',
    description: 'Fresh winning products every day. Never miss the next big opportunity.'
  }
];

const pricingPlans = [
  {
    name: 'Free',
    price: '0',
    description: 'Get started with product research',
    features: [
      'Limited product insights',
      'Report previews',
      '1 store',
      'Limited watchlist',
      'Community support'
    ],
    cta: 'Get Started',
    popular: false
  },
  {
    name: 'Starter',
    price: '19',
    description: 'Launch your first winning store',
    features: [
      'Full product insights',
      'Complete reports access',
      '1 store',
      'Full watchlist access',
      'Email support'
    ],
    cta: 'Get Starter',
    popular: false
  },
  {
    name: 'Pro',
    price: '39',
    description: 'Scale with multiple stores',
    features: [
      'Everything in Starter',
      'Up to 5 stores',
      'Full alerts access',
      'Priority support',
      'Advanced filters'
    ],
    cta: 'Upgrade to Pro',
    popular: true
  },
  {
    name: 'Elite',
    price: '99',
    description: 'For serious sellers',
    features: [
      'Everything in Pro',
      'Unlimited stores',
      'Early trend detection',
      'Automation insights',
      'Dedicated support'
    ],
    cta: 'Go Elite',
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
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-emerald-50 px-4 py-1.5 text-sm font-medium text-emerald-700">
              <Rocket className="h-4 w-4" />
              Launch Stores in Minutes
            </div>
            <h1 className="font-manrope text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              Launch your next winning{' '}
              <span className="text-indigo-600">ecommerce store</span>{' '}
              in minutes
            </h1>
            <p className="mt-6 text-lg text-slate-600 leading-relaxed">
              Find proven winning products, generate your store with AI, and export to Shopify. 
              Stop researching endlessly. Start selling today.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/signup">
                <Button 
                  size="lg" 
                  data-testid="hero-cta-btn"
                  className="bg-indigo-600 hover:bg-indigo-700 text-base px-8 h-12 font-semibold"
                >
                  <Rocket className="mr-2 h-5 w-5" />
                  Start Building Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/login">
                <Button 
                  variant="outline" 
                  size="lg"
                  className="text-base px-8 h-12"
                >
                  Sign In
                </Button>
              </Link>
            </div>
            <p className="mt-4 text-sm text-slate-500">
              No credit card required • Launch your first store today
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
                    trendscout.click/dashboard
                  </div>
                </div>
              </div>
              <div className="p-6 bg-[#F8FAFC]">
                {/* Mock dashboard */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                  {['Winning Products', 'Avg Win Score', 'Stores Launched', 'Early Trends'].map((label, i) => (
                    <div key={label} className="bg-white rounded-xl border border-slate-200 p-4">
                      <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
                      <p className="mt-1 font-mono text-2xl font-semibold text-slate-900">
                        {['847', '82', '156', '34'][i]}
                      </p>
                    </div>
                  ))}
                </div>
                <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                  <div className="bg-gradient-to-r from-amber-50 to-orange-50 px-4 py-3 border-b border-slate-200">
                    <p className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                      <Trophy className="h-4 w-4 text-amber-500" />
                      Winning Products Today
                    </p>
                  </div>
                  <div className="divide-y divide-slate-100">
                    {['Sunset Projection Lamp', 'Smart Water Bottle', 'Portable Neck Fan'].map((name, i) => (
                      <div key={name} className="px-4 py-3 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-100 to-orange-100 flex items-center justify-center font-bold text-amber-700">
                            #{i + 1}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-slate-900">{name}</p>
                            <p className="text-xs text-slate-500">£{[26, 30, 21][i]} margin</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="font-mono text-sm font-semibold text-amber-600">
                            {[89, 85, 82][i]}
                          </span>
                          <button className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-700 transition-colors">
                            Build Store
                          </button>
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
              From product discovery to store launch
            </h2>
            <p className="mt-4 text-lg text-slate-600">
              Everything you need to launch a winning ecommerce store, fast
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

      {/* Product of the Week */}
      <ProductOfTheWeek />

      {/* Newsletter Capture */}
      <NewsletterCapture />

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
          <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
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
          <div className="rounded-3xl bg-gradient-to-r from-indigo-600 to-purple-600 px-8 py-16 sm:px-16 text-center">
            <h2 className="font-manrope text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Ready to launch your winning store?
            </h2>
            <p className="mt-4 text-lg text-indigo-100">
              Find a product. Build your store. Launch to Shopify. All in minutes.
            </p>
            <div className="mt-8">
              <Link to="/signup">
                <Button 
                  size="lg" 
                  className="bg-white text-indigo-600 hover:bg-indigo-50 text-base px-8 h-12 font-semibold"
                  data-testid="final-cta-btn"
                >
                  <Rocket className="mr-2 h-5 w-5" />
                  Start Building Free
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
