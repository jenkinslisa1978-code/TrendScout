import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white" data-testid="privacy-page">
      <div className="max-w-3xl mx-auto px-4 py-16">
        <Button asChild variant="ghost" className="mb-8">
          <Link to="/"><ArrowLeft className="h-4 w-4 mr-2" /> Back</Link>
        </Button>
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Privacy Policy</h1>
        <p className="text-sm text-slate-500 mb-8">Last updated: March 2026</p>

        <div className="prose prose-slate max-w-none space-y-6 text-slate-700">
          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">1. Information We Collect</h2>
            <p><strong>Account data:</strong> Email address, name, and password hash when you register.</p>
            <p><strong>Usage data:</strong> Pages viewed, features used, products analysed, and interaction patterns to improve the Service.</p>
            <p><strong>Payment data:</strong> Processed securely by Stripe. We do not store card details.</p>
            <p><strong>Shopify store data:</strong> When you connect your Shopify store, we access your store name, product catalogue (titles, descriptions, images, pricing, inventory levels), and order metadata solely to provide our product intelligence and import features. We do not access or store your customers' personal information.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">2. How We Use Your Information</h2>
            <p>We use your data to: (a) provide and improve the Service; (b) process subscriptions and payments; (c) send relevant product alerts and trend reports you've opted into; (d) analyse aggregate usage patterns; (e) push product drafts to your connected Shopify store when you request it.</p>
            <p><strong>Shopify data:</strong> Store data is used exclusively to serve you within TrendScout. We do not use merchant data for purposes unrelated to your use of our app, and we never sell store data to third parties.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">3. Data Sharing</h2>
            <p>We do not sell your personal data. We may share data with: (a) payment processors (Stripe) to handle billing; (b) email service providers to send notifications you've requested; (c) law enforcement if required by law.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">4. Cookies & Analytics</h2>
            <p>We use essential cookies for authentication and session management. We use analytics to understand how users interact with the Service. You can control cookie preferences in your browser settings.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">5. Data Security</h2>
            <p>We implement industry-standard security measures including encrypted data transmission (TLS), hashed passwords (bcrypt), and secure API authentication (JWT). We regularly review our security practices.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">6. Data Retention</h2>
            <p>We retain your account data for as long as your account is active. You may request deletion of your account and associated data at any time by contacting us.</p>
            <p><strong>Shopify data:</strong> If you uninstall TrendScout from your Shopify store, we receive an automatic notification and mark your connection as inactive. Within 48 hours of receiving a shop data erasure request from Shopify, we delete all data associated with your store, including connection credentials, export history, and any cached store information.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">7. GDPR Compliance (Shopify)</h2>
            <p>TrendScout fully complies with Shopify's mandatory GDPR requirements:</p>
            <p><strong>Customer data requests:</strong> We respond to all customer data requests forwarded by Shopify. TrendScout does not store end-customer personal data from your store.</p>
            <p><strong>Customer data erasure:</strong> We process all customer data deletion requests and confirm completion.</p>
            <p><strong>Shop data erasure:</strong> When you uninstall the app or Shopify sends a shop erasure request, all shop-related data is permanently deleted from our systems.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">8. Your Rights</h2>
            <p>You have the right to: (a) access your personal data; (b) correct inaccurate data; (c) request deletion of your data; (d) opt out of marketing communications; (e) export your data.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">9. Children's Privacy</h2>
            <p>The Service is not intended for users under 16 years of age. We do not knowingly collect data from children.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">10. Changes to This Policy</h2>
            <p>We may update this policy periodically. We will notify you of material changes via email or in-app notification.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-900 mt-8 mb-3">11. Contact</h2>
            <p>For privacy-related questions or data requests, contact us at info@trendscout.click.</p>
          </section>
        </div>
      </div>
    </div>
  );
}
