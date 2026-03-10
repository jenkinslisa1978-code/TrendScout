/**
 * useOnboarding Hook
 * 
 * Manages onboarding state for new users.
 * Detects first login and shows onboarding modal.
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';

export function useOnboarding() {
  const { user, profile, isDemoMode } = useAuth();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [loading, setLoading] = useState(true);
  const [hasChecked, setHasChecked] = useState(false);
  
  // Check if user needs onboarding
  const checkOnboardingStatus = useCallback(async () => {
    if (!user || hasChecked) {
      setLoading(false);
      return;
    }
    
    try {
      // Check profile for onboarding_completed flag
      const response = await api.get('/api/user/onboarding-status');
      
      if (response.data) {
        const needsOnboarding = !response.data.onboarding_completed;
        setShowOnboarding(needsOnboarding);
      }
    } catch (error) {
      // If endpoint fails, check local profile
      const needsOnboarding = profile && !profile.onboarding_completed;
      setShowOnboarding(needsOnboarding);
    } finally {
      setLoading(false);
      setHasChecked(true);
    }
  }, [user, profile, hasChecked]);
  
  // Check on mount and when user changes
  useEffect(() => {
    if (user && !hasChecked) {
      checkOnboardingStatus();
    } else if (!user) {
      setShowOnboarding(false);
      setLoading(false);
    }
  }, [user, checkOnboardingStatus, hasChecked]);
  
  // Close onboarding
  const closeOnboarding = useCallback(() => {
    setShowOnboarding(false);
  }, []);
  
  // Reset for testing
  const resetOnboarding = useCallback(async () => {
    try {
      await api.post('/api/user/reset-onboarding');
      setHasChecked(false);
      setShowOnboarding(true);
    } catch (error) {
      console.error('Failed to reset onboarding:', error);
    }
  }, []);
  
  return {
    showOnboarding,
    loading,
    closeOnboarding,
    resetOnboarding
  };
}

export default useOnboarding;
