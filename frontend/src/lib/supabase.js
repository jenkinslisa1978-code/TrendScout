import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || '';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || '';

// Check if Supabase is properly configured with valid credentials
export const isSupabaseConfigured = () => {
  // URL must be a valid supabase URL
  const hasValidUrl = supabaseUrl && 
    supabaseUrl.includes('.supabase.co') && 
    supabaseUrl.startsWith('https://');
  
  // Anon key must be a JWT token (starts with eyJ) and not a placeholder
  const hasValidKey = supabaseAnonKey && 
    supabaseAnonKey.startsWith('eyJ') &&
    !supabaseAnonKey.includes('YOUR_');
  
  return hasValidUrl && hasValidKey;
};

// Custom fetch wrapper that handles body stream issues
const customFetch = async (url, options = {}) => {
  try {
    const response = await fetch(url, options);
    
    // Handle rate limiting gracefully
    if (response.status === 429) {
      const errorBody = { error: 'rate_limit_exceeded', message: 'Too many requests. Please wait a moment and try again.' };
      return new Response(JSON.stringify(errorBody), {
        status: 429,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return response;
  } catch (err) {
    console.error('Fetch error:', err);
    throw err;
  }
};

// Only create client if properly configured
export const supabase = isSupabaseConfigured() 
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
      },
      global: {
        fetch: customFetch
      }
    })
  : null;
