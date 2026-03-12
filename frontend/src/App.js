import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { Toaster } from "sonner";
import { ErrorBoundary } from "@/components/ErrorBoundary";

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
import TrendAlertsPage from "@/pages/TrendAlertsPage";
import StoresPage from "@/pages/StoresPage";
import StoreDetailPage from "@/pages/StoreDetailPage";
import StorePreviewPage from "@/pages/StorePreviewPage";
import TrendingProductsPage from "@/pages/TrendingProductsPage";
import TrendingProductPage from "@/pages/TrendingProductPage";
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

function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/trending-products" element={<TrendingProductsPage />} />
      <Route path="/trending/:slug" element={<TrendingProductPage />} />
      <Route path="/p/:id" element={<PublicProductPage />} />
      <Route path="/tools" element={<FreeToolsPage />} />

      {/* Protected routes */}
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
        path="/alerts"
        element={
          <ProtectedRoute>
            <TrendAlertsPage />
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

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
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
