import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, SearchX } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4" data-testid="not-found-page">
      <div className="text-center max-w-md">
        <div className="mx-auto w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center mb-6">
          <SearchX className="h-8 w-8 text-indigo-600" />
        </div>
        <h1 className="text-4xl font-bold text-slate-900 mb-2">404</h1>
        <p className="text-lg text-slate-600 mb-6">
          Page not found. The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex gap-3 justify-center">
          <Button asChild variant="default">
            <Link to="/">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Link>
          </Button>
          <Button asChild variant="outline">
            <Link to="/discover">Browse Products</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
