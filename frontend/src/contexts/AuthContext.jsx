import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase, isSupabaseConfigured } from '@/lib/supabase';

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

// Mock user for demo mode when Supabase is not configured
const DEMO_USER = {
  id: 'demo-user-id',
  email: 'demo@trendscout.com',
  user_metadata: { full_name: 'Demo User' }
};

const DEMO_PROFILE = {
  id: 'demo-user-id',
  full_name: 'Demo User',
  email: 'demo@trendscout.com',
  role: 'admin',
  plan: 'pro'
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);

  useEffect(() => {
    if (!isSupabaseConfigured()) {
      // Demo mode - no Supabase configured
      setIsDemoMode(true);
      setLoading(false);
      return;
    }

    // Check for existing session
    const getSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        setUser(session?.user ?? null);
        if (session?.user) {
          await fetchProfile(session.user.id);
        }
      } catch (error) {
        console.error('Error getting session:', error);
      }
      setLoading(false);
    };

    getSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      setUser(session?.user ?? null);
      if (session?.user) {
        await fetchProfile(session.user.id);
      } else {
        setProfile(null);
      }
    });

    return () => subscription?.unsubscribe();
  }, []);

  const fetchProfile = async (userId) => {
    if (!supabase) return;
    
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single();

      if (!error && data) {
        setProfile(data);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const signUp = async (email, password, fullName) => {
    if (isDemoMode || !supabase) {
      setUser(DEMO_USER);
      setProfile(DEMO_PROFILE);
      return { data: { user: DEMO_USER }, error: null };
    }

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: fullName }
      }
    });
    return { data, error };
  };

  const signIn = async (email, password) => {
    if (isDemoMode || !supabase) {
      setUser(DEMO_USER);
      setProfile(DEMO_PROFILE);
      return { data: { user: DEMO_USER }, error: null };
    }

    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });
    return { data, error };
  };

  const signOut = async () => {
    if (isDemoMode || !supabase) {
      setUser(null);
      setProfile(null);
      return { error: null };
    }

    const { error } = await supabase.auth.signOut();
    setProfile(null);
    return { error };
  };

  const value = {
    user,
    profile,
    loading,
    isDemoMode,
    signUp,
    signIn,
    signOut,
    isAuthenticated: !!user,
    isAdmin: profile?.role === 'admin'
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
