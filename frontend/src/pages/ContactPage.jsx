import React from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { breadcrumbSchema } from '@/components/PageMeta';
import { Mail, MessageSquare, Clock, ArrowRight } from 'lucide-react';

export default function ContactPage() {
  return (
    <LandingLayout>
      <PageMeta
        title="Contact"
        description="Get in touch with TrendScout. Support enquiries, partnership opportunities, and general questions."
        canonical="/contact"
        schema={[
          { '@context': 'https://schema.org', '@type': 'ContactPage', name: 'Contact TrendScout', url: 'https://trendscout.click/contact' },
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Contact' }]),
        ]}
      />
      <div className="bg-white" data-testid="contact-page">
        <section className="pt-16 pb-20 px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              Contact us
            </h1>
            <p className="mt-4 text-lg text-slate-600 leading-relaxed">
              Have a question, suggestion, or need help with your account? We are here to help.
            </p>

            <div className="mt-10 grid sm:grid-cols-2 gap-5">
              <div className="rounded-lg border border-slate-200 p-6">
                <Mail className="h-5 w-5 text-indigo-600 mb-3" />
                <h3 className="text-sm font-semibold text-slate-900">Email us</h3>
                <p className="text-sm text-slate-500 mt-1">For general enquiries, support, or partnership opportunities.</p>
                <a href="mailto:info@trendscout.click" className="inline-block mt-3 text-sm font-medium text-indigo-600 hover:text-indigo-700">
                  info@trendscout.click
                </a>
              </div>
              <div className="rounded-lg border border-slate-200 p-6">
                <MessageSquare className="h-5 w-5 text-indigo-600 mb-3" />
                <h3 className="text-sm font-semibold text-slate-900">Help Centre</h3>
                <p className="text-sm text-slate-500 mt-1">Browse common questions, guides, and troubleshooting articles.</p>
                <Link to="/help" className="inline-block mt-3 text-sm font-medium text-indigo-600 hover:text-indigo-700">
                  Visit Help Centre <ArrowRight className="inline h-3.5 w-3.5 ml-1" />
                </Link>
              </div>
            </div>

            <div className="mt-8 rounded-lg border border-slate-200 p-6">
              <Clock className="h-5 w-5 text-indigo-600 mb-3" />
              <h3 className="text-sm font-semibold text-slate-900">Response times</h3>
              <p className="text-sm text-slate-500 mt-1 leading-relaxed">
                We aim to respond to all enquiries within 24 hours on business days. Priority support customers on Growth and Pro plans receive faster response times.
              </p>
            </div>

            <div className="mt-10 rounded-lg bg-slate-50 border border-slate-200 p-6">
              <h3 className="text-sm font-semibold text-slate-900 mb-2">Company details</h3>
              <div className="text-sm text-slate-600 space-y-1">
                <p>TrendScout Ltd</p>
                <p>United Kingdom</p>
                <p>Email: <a href="mailto:info@trendscout.click" className="text-indigo-600">info@trendscout.click</a></p>
                <p>Website: <a href="https://trendscout.click" className="text-indigo-600">trendscout.click</a></p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
