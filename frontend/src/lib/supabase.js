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

// Only create client if properly configured
export const supabase = isSupabaseConfigured() 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;
