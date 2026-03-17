import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-white" data-testid="terms-page">
      <div className="max-w-3xl mx-auto px-4 py-16">
        <Button asChild variant="ghost" className="mb-8">
          <Link to="/"><ArrowLeft className="h-4 w-4 mr-2" /> Back</Link>
        </Button>
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Terms of Service</h1>
        <p className="text-sm text-slate-500 mb-8">Last updated: March 2026</p>

        <div className="prose prose-slate max-w-none space-y-6 text-slate-700">
          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">1. Acceptance of Terms</h2>
            <p>By accessing or using TrendScout ("the Service"), you agree to be bound by these Terms of Service. If you do not agree, do not use the Service.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">2. Description of Service</h2>
            <p>TrendScout is an AI-powered product discovery platform that helps ecommerce entrepreneurs find trending products, analyse market competition, and make data-driven decisions. The Service includes product trend data, market analysis, store generation tools, and related features.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">3. User Accounts</h2>
            <p>You are responsible for maintaining the security of your account credentials. You must provide accurate information when creating an account. You may not share your account with others or use another person's account.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">4. Subscription & Billing</h2>
            <p>Paid subscriptions are billed on a recurring basis. You may cancel at any time through your account settings. Refunds are handled according to our refund policy. Free tier access may be limited in features and usage.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">5. Data & Accuracy</h2>
            <p>Product data, trend scores, and market analysis provided by the Service are for informational purposes only. While we strive for accuracy, we do not guarantee the completeness or reliability of any data. Business decisions should not be based solely on our data.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">6. Intellectual Property</h2>
            <p>All content, features, and functionality of the Service are owned by TrendScout and are protected by intellectual property laws. You may not copy, modify, or distribute any part of the Service without permission.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">7. Prohibited Conduct</h2>
            <p>You may not: (a) use the Service for any unlawful purpose; (b) attempt to reverse-engineer or scrape the Service; (c) interfere with or disrupt the Service; (d) use automated tools to access the Service beyond normal usage.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">8. Limitation of Liability</h2>
            <p>TrendScout shall not be liable for any indirect, incidental, or consequential damages arising from your use of the Service. Our total liability shall not exceed the amount you paid in the 12 months preceding the claim.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">9. Changes to Terms</h2>
            <p>We may update these Terms from time to time. Continued use of the Service after changes constitutes acceptance of the new Terms. Material changes will be communicated via email or in-app notification.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">10. Contact</h2>
            <p>For questions about these Terms, contact us at support@trendscout.app.</p>
          </section>
        </div>
      </div>
    </div>
  );
}
