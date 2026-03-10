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
          plan: 'starter'
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
      
      return { data, error };
    } catch (err) {
      console.error('Signup error:', err);
      // Handle common error cases with user-friendly messages
      const errorMessage = err.message || '';
      if (errorMessage.includes('body stream already read') || errorMessage.includes('fetch')) {
        return { data: null, error: { message: 'Unable to connect to authentication service. Please try again.' } };
      }
      if (errorMessage.includes('rate') || errorMessage.includes('429') || errorMessage.includes('Too many')) {
        return { data: null, error: { message: 'Too many attempts. Please wait a moment and try again.' } };
      }
      return { data: null, error: { message: err.message || 'Signup failed. Please try again.' } };
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
      
      return { data, error };
    } catch (err) {
      console.error('SignIn error:', err);
      // Handle common error cases with user-friendly messages
      const errorMessage = err.message || '';
      if (errorMessage.includes('body stream already read') || errorMessage.includes('fetch')) {
        return { data: null, error: { message: 'Unable to connect to authentication service. Please try again.' } };
      }
      if (errorMessage.includes('rate') || errorMessage.includes('429') || errorMessage.includes('Too many')) {
        return { data: null, error: { message: 'Too many attempts. Please wait a moment and try again.' } };
      }
      return { data: null, error: { message: err.message || 'Login failed. Please try again.' } };
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
