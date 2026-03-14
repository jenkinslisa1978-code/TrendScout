import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { API_URL } from '@/lib/config';

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

const TOKEN_KEY = 'trendscout_token';
const USER_KEY = 'trendscout_user';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const tokenRef = useRef(null);
  const refreshTimerRef = useRef(null);

  const setToken = useCallback((token) => {
    tokenRef.current = token;
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  }, []);

  const fetchProfile = useCallback(async (token) => {
    try {
      const res = await fetch(`${API_URL}/api/auth/profile`, {
        headers: { Authorization: `Bearer ${token}` },
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
      }
    } catch (err) {
      console.error('Failed to fetch profile:', err);
    }
  }, []);

  const refreshAccessToken = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        setToken(data.token);
        scheduleRefresh();
        return data.token;
      }
    } catch {}
    // Refresh failed — clear state
    setToken(null);
    localStorage.removeItem(USER_KEY);
    setUser(null);
    setProfile(null);
    return null;
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const scheduleRefresh = useCallback(() => {
    if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    // Refresh 1 minute before expiry (token is 15min = 900s)
    refreshTimerRef.current = setTimeout(() => {
      refreshAccessToken();
    }, 13 * 60 * 1000); // 13 minutes
  }, [refreshAccessToken]);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);

      if (storedToken && storedUser) {
        try {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          tokenRef.current = storedToken;

          // Try to refresh the token (old tokens from before the upgrade will be replaced)
          const res = await fetch(`${API_URL}/api/auth/refresh`, {
            method: 'POST',
            credentials: 'include',
          });
          if (res.ok) {
            const data = await res.json();
            setToken(data.token);
            await fetchProfile(data.token);
            scheduleRefresh();
          } else {
            // Refresh failed but old token might still work
            await fetchProfile(storedToken);
            scheduleRefresh();
          }
        } catch {
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(USER_KEY);
        }
      }
      setLoading(false);
    };

    initAuth();

    return () => {
      if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    };
  }, [fetchProfile, setToken, scheduleRefresh]);

  const signIn = async (email, password) => {
    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        credentials: 'include',
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const msg = err.error?.message || err.detail || 'Invalid email or password';
        return { data: null, error: { message: msg } };
      }

      const data = await res.json();
      setToken(data.token);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      setUser(data.user);
      await fetchProfile(data.token);
      scheduleRefresh();
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
        credentials: 'include',
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const msg = err.error?.message || err.detail || 'Registration failed';
        return { data: null, error: { message: msg } };
      }

      const data = await res.json();
      setToken(data.token);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      setUser(data.user);
      await fetchProfile(data.token);
      scheduleRefresh();
      return { data, error: null };
    } catch {
      return { data: null, error: { message: 'Registration failed. Please try again.' } };
    }
  };

  const signOut = async () => {
    try {
      await fetch(`${API_URL}/api/auth/logout`, { method: 'POST', credentials: 'include' });
    } catch {}
    if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    setToken(null);
    localStorage.removeItem(USER_KEY);
    setUser(null);
    setProfile(null);
  };

  const getToken = () => tokenRef.current || localStorage.getItem(TOKEN_KEY);

  const value = {
    user,
    profile,
    loading,
    signIn,
    signUp,
    signOut,
    getToken,
    refreshAccessToken,
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
