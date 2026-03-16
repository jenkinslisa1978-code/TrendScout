import React, { useEffect, lazy, Suspense } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { Toaster } from "sonner";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { trackPageView } from "@/services/analytics";

// Pages
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import SignupPage from "@/pages/SignupPage";
import DashboardPage from "@/pages/DashboardPage";
import DiscoverPage from "@/pages/DiscoverPage";
import ProductDetailPage from "@/pages/ProductDetailPage";
import SavedProductsPage from "@/pages/SavedProductsPage";
import AdminPage from "@/pages/AdminPage";
import AdminAutomationPage from "@/pages/AdminAutomationPage";
import AnalyticsDashboardPage from "@/pages/AnalyticsDashboardPage";
import AdminImageReviewPage from "@/pages/AdminImageReviewPage";
import TrendAlertsPage from "@/pages/TrendAlertsPage";
import StoresPage from "@/pages/StoresPage";
import StoreDetailPage from "@/pages/StoreDetailPage";
import StorePreviewPage from "@/pages/StorePreviewPage";
import TrendingProductsPage from "@/pages/TrendingProductsPage";
import TrendingProductPage from "@/pages/TrendingProductPage";
import TrendingIndexPage from "@/pages/TrendingIndexPage";
import ApiDocsPage from "@/pages/ApiDocsPage";
import WeeklyDigestPage from "@/pages/WeeklyDigestPage";
import DigestArchivePage from "@/pages/DigestArchivePage";
import PublicProductPage from "@/pages/PublicProductPage";
import ReferralPage from "@/pages/ReferralPage";

// Reports Pages
import ReportsPage from "@/pages/ReportsPage";
import WeeklyReportPage from "@/pages/WeeklyReportPage";
import MonthlyReportPage from "@/pages/MonthlyReportPage";
import PublicWeeklyReportPage from "@/pages/PublicWeeklyReportPage";
import PublicMonthlyReportPage from "@/pages/PublicMonthlyReportPage";

// Settings Pages
import NotificationSettingsPage from "@/pages/NotificationSettingsPage";

// Subscription
import PricingPage from "@/pages/PricingPage";
import { SubscriptionProvider } from "@/hooks/useSubscription";
import ProductLaunchWizard from "@/pages/ProductLaunchWizard";
import OptimizationPage from "@/pages/OptimizationPage";
import { ViewModeProvider } from "@/contexts/ViewModeContext";
import SeoPage from "@/pages/SeoPage";
import FreeToolsPage from "@/pages/FreeToolsPage";
import OutcomesPage from "@/pages/OutcomesPage";
import AdTestsPage from "@/pages/AdTestsPage";
import SystemHealthDashboard from "@/pages/SystemHealthDashboard";
import IntegrationStatusPage from "@/pages/IntegrationStatusPage";
import ShopifyAnalyzerPage from "@/pages/ShopifyAnalyzerPage";
import CompetitorTrackerPage from "@/pages/CompetitorTrackerPage";
import TikTokIntelligencePage from "@/pages/TikTokIntelligencePage";
import TopTrendingPage from "@/pages/TopTrendingPage";
import SeoTrendingPage from "@/pages/SeoTrendingPage";
import SeoCategoryPage from "@/pages/SeoCategoryPage";
import BlogPage from "@/pages/BlogPage";
import BlogPostPage from "@/pages/BlogPostPage";
import NotFoundPage from "@/pages/NotFoundPage";
import TermsPage from "@/pages/TermsPage";
import PrivacyPage from "@/pages/PrivacyPage";
import PlatformConnectionsPage from "@/pages/PlatformConnectionsPage";
import HelpPage from "@/pages/HelpPage";
import DemoPage from "@/pages/DemoPage";
import ForgotPasswordPage from "@/pages/ForgotPasswordPage";
import ResetPasswordPage from "@/pages/ResetPasswordPage";
import ProfitabilitySimulatorPage from "@/pages/ProfitabilitySimulatorPage";
import AdSpyPage from "@/pages/AdSpyPage";
import CompetitorIntelPage from "@/pages/CompetitorIntelPage";
import RadarAlertsPage from "@/pages/RadarAlertsPage";
import VerifiedWinnersPage from "@/pages/VerifiedWinnersPage";

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
      <Route path="/tools" element={<FreeToolsPage />} />
      <Route path="/tools/shopify-analyzer" element={<ShopifyAnalyzerPage />} />
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

      {/* Fallback */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
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
