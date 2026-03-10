import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase, isSupabaseConfigured } from '@/lib/supabase';

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

// Mock user for demo mode when Supabase is not configured
const DEMO_USER = {
  id: 'demo-user-id',
  email: 'demo@viralscout.com',
  user_metadata: { full_name: 'Demo User' }
};

const DEMO_PROFILE = {
  id: 'demo-user-id',
  full_name: 'Demo User',
  email: 'demo@viralscout.com',
  role: 'admin',
  plan: 'elite'
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);

  useEffect(() => {
    // Check if Supabase is configured
    const supabaseConfigured = isSupabaseConfigured();
    setIsDemoMode(!supabaseConfigured);

    if (!supabaseConfigured) {
      // Demo mode - no Supabase configured
      console.log('ViralScout running in Demo Mode - configure Supabase for live auth');
      setLoading(false);
      return;
    }

    // Live mode - check for existing session
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
      console.log('Auth state changed:', event);
      setUser(session?.user ?? null);
      
      if (session?.user) {
        // On sign up, create profile if it doesn't exist
        if (event === 'SIGNED_IN' || event === 'USER_UPDATED') {
          await fetchProfile(session.user.id);
        }
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

      if (error && error.code === 'PGRST116') {
        // Profile doesn't exist, create one
        console.log('Creating new profile for user:', userId);
        const { data: userData } = await supabase.auth.getUser();
        const newProfile = {
          id: userId,
          full_name: userData?.user?.user_metadata?.full_name || 'User',
          email: userData?.user?.email || '',
          role: 'user',
          plan: 'free'
        };
        
        const { data: created, error: createError } = await supabase
          .from('profiles')
          .insert([newProfile])
          .select()
          .single();
          
        if (!createError && created) {
          setProfile(created);
        }
      } else if (!error && data) {
        setProfile(data);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const signUp = async (email, password, fullName) => {
    // In demo mode, simulate signup
    if (isDemoMode) {
      setUser(DEMO_USER);
      setProfile(DEMO_PROFILE);
      return { data: { user: DEMO_USER }, error: null };
    }

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { full_name: fullName }
        }
      });
      
      if (error) {
        const msg = error.message || '';
        if (msg.includes('rate') || msg.includes('429') || msg.includes('Too many')) {
          return { data: null, error: { message: 'Too many attempts. Please wait 60 seconds and try again.' } };
        }
        if (msg.includes('already registered') || msg.includes('already exists')) {
          return { data: null, error: { message: 'This email is already registered. Try logging in instead.' } };
        }
      }
      
      return { data, error };
    } catch (err) {
      console.error('Signup error:', err);
      const msg = err.message || '';
      if (msg.includes('rate') || msg.includes('429')) {
        return { data: null, error: { message: 'Too many attempts. Please wait 60 seconds and try again.' } };
      }
      // Body stream errors during signup usually mean rate limiting or existing account
      return { data: null, error: { message: 'Unable to create account. You may already have an account - try logging in, or wait a minute and try again.' } };
    }
  };

  const signIn = async (email, password) => {
    // In demo mode, simulate login
    if (isDemoMode) {
      setUser(DEMO_USER);
      setProfile(DEMO_PROFILE);
      return { data: { user: DEMO_USER }, error: null };
    }

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      });
      
      if (error) {
        const msg = error.message || '';
        if (msg.includes('Email not confirmed')) {
          return { data: null, error: { message: 'Please confirm your email first. Check your inbox and spam folder for the verification link.', showResend: true } };
        }
        if (msg.includes('Invalid login credentials')) {
          return { data: null, error: { message: 'Invalid email or password. If you haven\'t signed up yet, click "Sign up for free" below.' } };
        }
        // Catch-all: any other error (including body stream, JSON parse errors)
        return { data: null, error: { message: 'Invalid email or password. Please check your credentials and try again.' } };
      }
      
      return { data, error };
    } catch (err) {
      // The Supabase SDK throws "body stream already read" when it can't parse error responses.
      // This typically means invalid credentials (400 from Supabase). Return a clear message.
      console.error('SignIn error:', err);
      return { data: null, error: { message: 'Invalid email or password. If you haven\'t signed up yet, please create an account first.' } };
    }
  };

  const signOut = async () => {
    if (isDemoMode) {
      setUser(null);
      setProfile(null);
      return { error: null };
    }

    const { error } = await supabase.auth.signOut();
    setUser(null);
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
    isAuthenticated: !!user || isDemoMode,
    isAdmin: profile?.role === 'admin' || isDemoMode
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
