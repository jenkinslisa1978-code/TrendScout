# ViralScout Beta Launch Guide

## Current Status: READY FOR BETA LAUNCH

The application is fully functional in Demo Mode. To enable live authentication and payments, complete the configuration steps below.

---

## Step 1: Configure Supabase Authentication (Required for Live Beta)

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Create a new project (note: database password for later)
4. Wait for project to initialize (~2 minutes)

### 1.2 Get API Credentials
1. Go to **Settings → API**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGci...` (long JWT token)

### 1.3 Create Profiles Table
1. Go to **SQL Editor** in Supabase dashboard
2. Run this SQL:

```sql
-- Create profiles table
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  email TEXT,
  role TEXT DEFAULT 'user',
  plan TEXT DEFAULT 'starter',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own profile
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

-- Policy: New users can insert their profile
CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Create function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, email)
  VALUES (
    NEW.id,
    NEW.raw_user_meta_data->>'full_name',
    NEW.email
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to auto-create profile on signup
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### 1.4 Update Environment Variables
Edit `/app/frontend/.env`:
```env
REACT_APP_SUPABASE_URL=https://your-project-id.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key-here
```

### 1.5 Restart Frontend
```bash
sudo supervisorctl restart frontend
```

---

## Step 2: Configure Daily Automation (Recommended)

### Option A: Using cron-job.org (Free)
1. Go to [cron-job.org](https://cron-job.org)
2. Create free account
3. Add new cron job:
   - **URL**: `https://your-domain.com/api/automation/scheduled/daily`
   - **Method**: POST
   - **Headers**: Add header `X-API-Key` with value `vs_automation_key_2024`
   - **Schedule**: Daily at 6:00 AM UTC

### Option B: Using server cron
Add to crontab (`crontab -e`):
```bash
0 6 * * * curl -X POST https://your-domain.com/api/automation/scheduled/daily -H "X-API-Key: vs_automation_key_2024"
```

### Change API Key (Recommended for Production)
Edit `/app/backend/.env`:
```env
AUTOMATION_API_KEY=your-secure-random-key-here
```

---

## Step 3: Configure Stripe Payments (Optional - for monetization)

### 3.1 Create Stripe Account
1. Go to [stripe.com](https://stripe.com)
2. Complete account setup

### 3.2 Create Products & Prices
In Stripe Dashboard → Products:

| Plan | Price | Billing |
|------|-------|---------|
| Pro | $29 | Monthly |
| Elite | $79 | Monthly |

Note the Price IDs (e.g., `price_1ABC...`)

### 3.3 Configure Webhook
1. Go to **Developers → Webhooks**
2. Add endpoint: `https://your-domain.com/api/stripe/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy the webhook signing secret

### 3.4 Update Environment Variables
Edit `/app/backend/.env`:
```env
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_PRO_PRICE_ID=price_xxxxx
STRIPE_ELITE_PRICE_ID=price_xxxxx
```

### 3.5 Restart Backend
```bash
sudo supervisorctl restart backend
```

---

## Environment Variables Summary

### Frontend (`/app/frontend/.env`)
```env
REACT_APP_BACKEND_URL=https://your-domain.com
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
```

### Backend (`/app/backend/.env`)
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
AUTOMATION_API_KEY=your-secure-api-key
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_PRO_PRICE_ID=price_xxxxx
STRIPE_ELITE_PRICE_ID=price_xxxxx
```

---

## Verification Checklist

After configuration, verify:

- [ ] Supabase: Can create new user account
- [ ] Supabase: Can login with created account
- [ ] Supabase: Profile is created automatically
- [ ] Supabase: Logout works correctly
- [ ] Automation: Daily cron triggers successfully
- [ ] Stripe: Checkout session creates (if configured)
- [ ] Stripe: Webhook receives events (if configured)

---

## Quick Test Commands

```bash
# Test backend health
curl https://your-domain.com/api/health

# Test scheduled automation
curl -X POST https://your-domain.com/api/automation/scheduled/daily \
  -H "X-API-Key: vs_automation_key_2024"

# Check products
curl https://your-domain.com/api/products?limit=5
```

---

## Support

For issues during setup:
1. Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
2. Check frontend logs: `tail -f /var/log/supervisor/frontend.err.log`
3. Verify environment variables are set correctly
4. Restart services after env changes: `sudo supervisorctl restart all`
