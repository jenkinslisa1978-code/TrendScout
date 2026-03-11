import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { API_URL } from '@/lib/config';

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

const TOKEN_KEY = 'trendscout_token';
const USER_KEY = 'trendscout_user';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = useCallback(async (token) => {
    try {
      const res = await fetch(`${API_URL}/api/auth/profile`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
      }
    } catch (err) {
      console.error('Failed to fetch profile:', err);
    }
  }, []);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);

      if (storedToken && storedUser) {
        try {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          await fetchProfile(storedToken);
        } catch {
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(USER_KEY);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [fetchProfile]);

  const signIn = async (email, password) => {
    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        return { data: null, error: { message: err.detail || 'Invalid email or password' } };
      }

      const data = await res.json();
      localStorage.setItem(TOKEN_KEY, data.token);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      setUser(data.user);
      await fetchProfile(data.token);
      return { data, error: null };
    } catch {
      return { data: null, error: { message: 'Login failed. Please try again.' } };
    }
  };

  const signUp = async (email, password, fullName) => {
    try {
      const res = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        return { data: null, error: { message: err.detail || 'Registration failed' } };
      }

      const data = await res.json();
      localStorage.setItem(TOKEN_KEY, data.token);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      setUser(data.user);
      await fetchProfile(data.token);
      return { data, error: null };
    } catch {
      return { data: null, error: { message: 'Registration failed. Please try again.' } };
    }
  };

  const signOut = async () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
    setProfile(null);
  };

  const getToken = () => localStorage.getItem(TOKEN_KEY);

  const value = {
    user,
    profile,
    loading,
    signIn,
    signUp,
    signOut,
    getToken,
    isAuthenticated: !!user,
    isAdmin: profile?.is_admin || false,
    isDemoMode: false,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
