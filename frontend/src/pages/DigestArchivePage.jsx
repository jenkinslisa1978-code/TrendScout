import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Calendar, ArrowRight, BookOpen, Loader2, Star, Zap,
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function DigestArchivePage() {
  const [digests, setDigests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/api/digest/archive`);
        if (res.ok) {
          const d = await res.json();
          setDigests(d.digests || []);
        }
      } catch {}
      setLoading(false);
    })();
  }, []);

  return (
    <>
      <Helmet>
        <title>Weekly Product Digest Archive | TrendScout</title>
        <meta name="description" content="Browse past weekly trending product digests. AI-scored product roundups for dropshippers, updated every Monday." />
      </Helmet>

      <div className="min-h-screen bg-slate-50" data-testid="digest-archive-page">
        <nav className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
          <Link to="/" className="text-lg font-bold text-slate-900">TrendScout</Link>
          <div className="flex items-center gap-3">
            <Link to="/trending" className="text-xs text-slate-500 hover:text-indigo-600">Trending</Link>
            <Link to="/weekly-digest" className="text-xs text-slate-500 hover:text-indigo-600">Latest Digest</Link>
            <Link to="/register">
              <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700">Start Free Trial</Button>
            </Link>
          </div>
        </nav>

        <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">
          <div className="text-center">
            <h1 className="text-3xl font-black text-slate-900">Weekly Digest Archive</h1>
            <p className="text-sm text-slate-500 mt-2">Browse past weekly trending product roundups.</p>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
            </div>
          ) : digests.length === 0 ? (
            <Card className="border-0 shadow-lg">
              <CardContent className="flex flex-col items-center justify-center py-16">
                <BookOpen className="h-12 w-12 text-slate-300 mb-4" />
                <p className="text-sm text-slate-500">No digests published yet.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4" data-testid="archive-list">
              {digests.map(d => (
                <Link key={d.id} to={`/weekly-digest/${d.id}`} className="block group" data-testid="archive-card">
                  <Card className="border-0 shadow-md hover:shadow-lg transition-shadow">
                    <CardContent className="py-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="h-12 w-12 rounded-xl bg-indigo-50 flex items-center justify-center">
                            <Calendar className="h-5 w-5 text-indigo-600" />
                          </div>
                          <div>
                            <p className="text-sm font-bold text-slate-900 group-hover:text-indigo-700 transition-colors">{d.title}</p>
                            <div className="flex items-center gap-3 mt-1">
                              <Badge className="bg-indigo-50 text-indigo-600 border-indigo-200 text-[10px]">
                                <Star className="h-3 w-3 mr-0.5" /> {d.avg_score}/100
                              </Badge>
                              <span className="text-xs text-slate-400">{d.product_count} products</span>
                              <span className="text-xs text-slate-400">{d.categories_featured?.length || 0} categories</span>
                            </div>
                          </div>
                        </div>
                        <ArrowRight className="h-4 w-4 text-slate-300 group-hover:text-indigo-500 transition-colors" />
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}

          <div className="text-center py-6">
            <Link to="/register">
              <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="archive-cta">
                <Zap className="h-4 w-4 mr-1.5" /> Get Full Access — Free
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
