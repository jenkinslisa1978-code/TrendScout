import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || '';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || '';

// Check if Supabase is properly configured with valid credentials
export const isSupabaseConfigured = () => {
  const hasValidUrl = supabaseUrl && 
    supabaseUrl.includes('.supabase.co') && 
    supabaseUrl.startsWith('https://');
  
  const hasValidKey = supabaseAnonKey && 
    supabaseAnonKey.startsWith('eyJ') &&
    !supabaseAnonKey.includes('YOUR_');
  
  return hasValidUrl && hasValidKey;
};

// Only create client if properly configured
export const supabase = isSupabaseConfigured() 
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
      }
    })
  : null;
