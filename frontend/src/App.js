import React, { useEffect, lazy, Suspense } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { Toaster } from "sonner";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { trackPageView } from "@/services/analytics";
import { SubscriptionProvider } from "@/hooks/useSubscription";
import { ViewModeProvider } from "@/contexts/ViewModeContext";

// Eager — critical landing path
import LandingPage from "@/pages/LandingPage";
import NotFoundPage from "@/pages/NotFoundPage";

// Lazy-loaded pages (code-split by route)
const LoginPage = lazy(() => import("@/pages/LoginPage"));
const SignupPage = lazy(() => import("@/pages/SignupPage"));
const ForgotPasswordPage = lazy(() => import("@/pages/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("@/pages/ResetPasswordPage"));
const PricingPage = lazy(() => import("@/pages/PricingPage"));
const HowItWorksPage = lazy(() => import("@/pages/HowItWorksPage"));
const AboutPage = lazy(() => import("@/pages/AboutPage"));
const ContactPage = lazy(() => import("@/pages/ContactPage"));

// Dashboard & core app
const DashboardPage = lazy(() => import("@/pages/DashboardPage"));
const DiscoverPage = lazy(() => import("@/pages/DiscoverPage"));
const ProductDetailPage = lazy(() => import("@/pages/ProductDetailPage"));
const SavedProductsPage = lazy(() => import("@/pages/SavedProductsPage"));
const ProductLaunchWizard = lazy(() => import("@/pages/ProductLaunchWizardPage"));
const OptimizationPage = lazy(() => import("@/pages/OptimizationPage"));
const OutcomesPage = lazy(() => import("@/pages/OutcomesPage"));
const AdTestsPage = lazy(() => import("@/pages/AdTestsPage"));
const ProfitabilitySimulatorPage = lazy(() => import("@/pages/ProfitabilitySimulatorPage"));
const AdSpyPage = lazy(() => import("@/pages/AdSpyPage"));
const CompetitorIntelPage = lazy(() => import("@/pages/CompetitorIntelPage"));
const RadarAlertsPage = lazy(() => import("@/pages/RadarAlertsPage"));
const VerifiedWinnersPage = lazy(() => import("@/pages/VerifiedWinnersPage"));
const CJSourcingPage = lazy(() => import("@/pages/CJSourcingPage"));
const CompetitorTrackerPage = lazy(() => import("@/pages/CompetitorTrackerPage"));
const TikTokIntelligencePage = lazy(() => import("@/pages/TikTokIntelligencePage"));

// Admin
const AdminPage = lazy(() => import("@/pages/AdminPage"));
const AdminAutomationPage = lazy(() => import("@/pages/AdminAutomationPage"));
const AnalyticsDashboardPage = lazy(() => import("@/pages/AnalyticsDashboardPage"));
const AdminImageReviewPage = lazy(() => import("@/pages/AdminImageReviewPage"));
const SystemHealthDashboard = lazy(() => import("@/pages/SystemHealthDashboardPage"));
const IntegrationStatusPage = lazy(() => import("@/pages/IntegrationStatusPage"));

// Trending & SEO
const TrendingProductsPage = lazy(() => import("@/pages/TrendingProductsPage"));
const TrendingProductPage = lazy(() => import("@/pages/TrendingProductPage"));
const TrendingIndexPage = lazy(() => import("@/pages/TrendingIndexPage"));
const TopTrendingPage = lazy(() => import("@/pages/TopTrendingPage"));
const SeoTrendingPage = lazy(() => import("@/pages/SeoTrendingPage"));
const SeoCategoryPage = lazy(() => import("@/pages/SeoCategoryPage"));
const SeoPage = lazy(() => import("@/pages/SeoPage"));

// Reports
const ReportsPage = lazy(() => import("@/pages/ReportsPage"));
const WeeklyReportPage = lazy(() => import("@/pages/WeeklyReportPage"));
const MonthlyReportPage = lazy(() => import("@/pages/MonthlyReportPage"));
const PublicWeeklyReportPage = lazy(() => import("@/pages/PublicWeeklyReportPage"));
const PublicMonthlyReportPage = lazy(() => import("@/pages/PublicMonthlyReportPage"));

// Stores & Shopify
const StoresPage = lazy(() => import("@/pages/StoresPage"));
const StoreDetailPage = lazy(() => import("@/pages/StoreDetailPage"));
const StorePreviewPage = lazy(() => import("@/pages/StorePreviewPage"));
const ShopifyAnalyzerPage = lazy(() => import("@/pages/ShopifyAnalyzerPage"));
const ShopifyAppPage = lazy(() => import("@/pages/ShopifyAppPage"));
const ShopifyEmbeddedDashboard = lazy(() => import("@/pages/ShopifyEmbeddedDashboard"));

// Alerts, Digest, Referral
const TrendAlertsPage = lazy(() => import("@/pages/TrendAlertsPage"));
const WeeklyDigestPage = lazy(() => import("@/pages/WeeklyDigestPage"));
const DigestArchivePage = lazy(() => import("@/pages/DigestArchivePage"));
const ReferralPage = lazy(() => import("@/pages/ReferralPage"));
const ApiDocsPage = lazy(() => import("@/pages/ApiDocsPage"));
const PublicProductPage = lazy(() => import("@/pages/PublicProductPage"));

// Settings
const NotificationSettingsPage = lazy(() => import("@/pages/NotificationSettingsPage"));
const PlatformConnectionsPage = lazy(() => import("@/pages/PlatformConnectionsPage"));

// Content / Marketing / Free Tools
const FreeToolsPage = lazy(() => import("@/pages/FreeToolsPage"));
const BlogPage = lazy(() => import("@/pages/BlogPage"));
const BlogPostPage = lazy(() => import("@/pages/BlogPostPage"));
const DemoPage = lazy(() => import("@/pages/DemoPage"));
const HelpPage = lazy(() => import("@/pages/HelpPage"));
const TermsPage = lazy(() => import("@/pages/TermsPage"));
const PrivacyPage = lazy(() => import("@/pages/PrivacyPage"));
const CookiePolicyPage = lazy(() => import("@/pages/CookiePolicyPage"));
const RefundPolicyPage = lazy(() => import("@/pages/RefundPolicyPage"));

// UK Landing Pages
const UkProductResearchPage = lazy(() => import("@/pages/UkProductResearchPage"));
const ForShopifyPage = lazy(() => import("@/pages/ForShopifyPage"));
const ForAmazonUkPage = lazy(() => import("@/pages/ForAmazonUkPage"));
const ForTikTokShopUkPage = lazy(() => import("@/pages/ForTikTokShopUkPage"));
const ViabilityScorePage = lazy(() => import("@/pages/ViabilityScorePage"));
const DropshippingUkPage = lazy(() => import("@/pages/DropshippingUkPage"));
const WinningProductsUkPage = lazy(() => import("@/pages/WinningProductsUkPage"));
const ProductValidationUkPage = lazy(() => import("@/pages/ProductValidationUkPage"));
const TrendAnalysisUkPage = lazy(() => import("@/pages/TrendAnalysisUkPage"));
const BestProductsUkPage = lazy(() => import("@/pages/BestProductsUkPage"));
const TikTokProductResearchUkPage = lazy(() => import("@/pages/TikTokProductResearchUkPage"));
const ShopifyProductResearchUkPage = lazy(() => import("@/pages/ShopifyProductResearchUkPage"));
const SampleAnalysisPage = lazy(() => import("@/pages/SampleAnalysisPage"));
const MethodologyPage = lazy(() => import("@/pages/MethodologyPage"));
const AccuracyPage = lazy(() => import("@/pages/AccuracyPage"));

// Comparison
const ComparisonPage = lazy(() => import("@/pages/ComparisonPage"));

// Quiz
const ProductQuizPage = lazy(() => import("@/pages/ProductQuizPage"));

// Changelog
const ChangelogPage = lazy(() => import("@/pages/ChangelogPage"));

// Page loading fallback
const PageLoader = () => (
  <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
    <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent"></div>
  </div>
);


// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, isDemoMode } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent"></div>
      </div>
    );
  }

  // In demo mode, allow access without authentication
  if (isDemoMode) {
    return children;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Admin Route Component - Requires admin role
const AdminRoute = ({ children }) => {
  const { isAuthenticated, isAdmin, loading, isDemoMode } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent"></div>
      </div>
    );
  }

  // In demo mode, allow admin access for testing
  if (isDemoMode) {
    return children;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

function PageTracker() {
  const location = useLocation();
  useEffect(() => {
    trackPageView(location.pathname);
  }, [location.pathname]);
  return null;
}

function AppRoutes() {
  return (
    <Suspense fallback={<PageLoader />}>
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/trending-products" element={<TrendingProductsPage />} />
      <Route path="/trending/:slug" element={<TrendingProductPage />} />
      <Route path="/p/:id" element={<PublicProductPage />} />
      <Route path="/how-it-works" element={<HowItWorksPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/contact" element={<ContactPage />} />
      <Route path="/uk-product-research" element={<UkProductResearchPage />} />
      <Route path="/for-shopify" element={<ForShopifyPage />} />
      <Route path="/for-amazon-uk" element={<ForAmazonUkPage />} />
      <Route path="/for-tiktok-shop-uk" element={<ForTikTokShopUkPage />} />
      <Route path="/compare/:slug" element={<ComparisonPage />} />
      <Route path="/product-quiz" element={<ProductQuizPage />} />
      <Route path="/changelog" element={<ChangelogPage />} />
      <Route path="/methodology" element={<MethodologyPage />} />
      <Route path="/accuracy" element={<AccuracyPage />} />
      <Route path="/uk-product-viability-score" element={<ViabilityScorePage />} />
      <Route path="/dropshipping-product-research-uk" element={<DropshippingUkPage />} />
      <Route path="/winning-products-uk" element={<WinningProductsUkPage />} />
      <Route path="/product-validation-uk" element={<ProductValidationUkPage />} />
      <Route path="/uk-ecommerce-trend-analysis" element={<TrendAnalysisUkPage />} />
      <Route path="/cookie-policy" element={<CookiePolicyPage />} />
      <Route path="/refund-policy" element={<RefundPolicyPage />} />
      <Route path="/sample-product-analysis" element={<SampleAnalysisPage />} />
      <Route path="/best-products-to-sell-online-uk" element={<BestProductsUkPage />} />
      <Route path="/tiktok-shop-product-research-uk" element={<TikTokProductResearchUkPage />} />
      <Route path="/shopify-product-research-uk" element={<ShopifyProductResearchUkPage />} />
      <Route path="/tools" element={<FreeToolsPage />} />
      <Route path="/free-tools" element={<FreeToolsPage />} />
      <Route path="/tools/shopify-analyzer" element={<ShopifyAnalyzerPage />} />
      <Route path="/shopify-app" element={<ShopifyAppPage />} />
      <Route path="/embedded" element={<ShopifyEmbeddedDashboard />} />
      <Route path="/top-trending-products" element={<TopTrendingPage />} />
      <Route path="/trending-products-today" element={<SeoTrendingPage />} />
      <Route path="/trending-products-this-week" element={<SeoTrendingPage />} />
      <Route path="/trending-products-this-month" element={<SeoTrendingPage />} />
      <Route path="/category/:slug" element={<SeoCategoryPage />} />
      <Route path="/blog" element={<BlogPage />} />
      <Route path="/blog/:slug" element={<BlogPostPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/help" element={<HelpPage />} />
      <Route path="/demo" element={<DemoPage />} />
      <Route path="/trending" element={<TrendingIndexPage />} />
      <Route path="/weekly-digest" element={<WeeklyDigestPage />} />
      <Route path="/weekly-digest/archive" element={<DigestArchivePage />} />
      <Route path="/weekly-digest/:digestId" element={<WeeklyDigestPage />} />

      {/* Protected routes */}
      <Route
        path="/api-docs"
        element={
          <ProtectedRoute>
            <ApiDocsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/discover"
        element={
          <ProtectedRoute>
            <DiscoverPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/product/:id"
        element={
          <ProtectedRoute>
            <ProductDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/launch/:productId"
        element={
          <ProtectedRoute>
            <ProductLaunchWizard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/optimization"
        element={
          <ProtectedRoute>
            <OptimizationPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/optimization/:testId"
        element={
          <ProtectedRoute>
            <OptimizationPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/saved"
        element={
          <ProtectedRoute>
            <SavedProductsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <AdminPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/automation"
        element={
          <AdminRoute>
            <AdminAutomationPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/health"
        element={
          <AdminRoute>
            <SystemHealthDashboard />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/integrations"
        element={
          <AdminRoute>
            <IntegrationStatusPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/analytics"
        element={
          <AdminRoute>
            <AnalyticsDashboardPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/image-review"
        element={
          <AdminRoute>
            <AdminImageReviewPage />
          </AdminRoute>
        }
      />
      <Route
        path="/alerts"
        element={
          <ProtectedRoute>
            <TrendAlertsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/competitor-tracker"
        element={
          <ProtectedRoute>
            <CompetitorTrackerPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/tiktok-intelligence"
        element={
          <ProtectedRoute>
            <TikTokIntelligencePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/stores"
        element={
          <ProtectedRoute>
            <StoresPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/stores/:storeId"
        element={
          <ProtectedRoute>
            <StoreDetailPage />
          </ProtectedRoute>
        }
      />
      {/* Public store preview */}
      <Route path="/preview/:storeId" element={<StorePreviewPage />} />

      {/* Reports - Public Routes for SEO */}
      <Route path="/reports/weekly-winning-products" element={<PublicWeeklyReportPage />} />
      <Route path="/reports/monthly-market-trends" element={<PublicMonthlyReportPage />} />

      {/* Settings Routes */}
      <Route
        path="/settings/notifications"
        element={
          <ProtectedRoute>
            <NotificationSettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings/connections"
        element={
          <ProtectedRoute>
            <PlatformConnectionsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/referrals"
        element={
          <ProtectedRoute>
            <ReferralPage />
          </ProtectedRoute>
        }
      />

      {/* Reports - Protected Routes */}
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <ReportsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports/weekly/:slug"
        element={
          <ProtectedRoute>
            <WeeklyReportPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports/monthly/:slug"
        element={
          <ProtectedRoute>
            <MonthlyReportPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/outcomes"
        element={
          <ProtectedRoute>
            <OutcomesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/ad-tests"
        element={
          <ProtectedRoute>
            <AdTestsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profitability-simulator"
        element={
          <ProtectedRoute>
            <ProfitabilitySimulatorPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/ad-spy"
        element={
          <ProtectedRoute>
            <AdSpyPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/competitor-intel"
        element={
          <ProtectedRoute>
            <CompetitorIntelPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/radar-alerts"
        element={
          <ProtectedRoute>
            <RadarAlertsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/verified-winners"
        element={
          <ProtectedRoute>
            <VerifiedWinnersPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/cj-sourcing"
        element={
          <ProtectedRoute>
            <CJSourcingPage />
          </ProtectedRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
    </Suspense>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <SubscriptionProvider>
          <ViewModeProvider>
            <BrowserRouter>
              <PageTracker />
              <AppRoutes />
              <Toaster 
                position="top-right" 
                richColors 
                closeButton
                toastOptions={{
                  style: {
                    fontFamily: 'Inter, sans-serif',
                  },
                }}
              />
            </BrowserRouter>
          </ViewModeProvider>
        </SubscriptionProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
