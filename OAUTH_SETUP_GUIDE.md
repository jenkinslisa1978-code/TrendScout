# How to Set Up OAuth Apps for TrendScout

## What is this about?

TrendScout can connect to your online stores and ad accounts automatically — but first, you need to tell each platform "Hey, TrendScout is allowed to talk to me." You do this by creating an "OAuth App" on each platform.

Think of it like giving TrendScout a special key to your store. The store knows this key belongs to TrendScout, so when TrendScout shows up, the store lets it in.

You only need to do this **once per platform**. After setup, all your users get **one-click** connections.

---

## Shopify (Already Done!)

Your Shopify app is already configured. Skip to the next platform.

---

## Meta (Facebook/Instagram Ads)

### What you'll get
Users can connect their Meta ad accounts to see ad performance data and trending products from Facebook/Instagram.

### Step-by-step

1. **Go to Meta for Developers**
   - Open: https://developers.facebook.com/
   - Click **"My Apps"** in the top right
   - Click **"Create App"**

2. **Choose App Type**
   - Select **"Business"**
   - Click **"Next"**

3. **Fill in App Details**
   - **App Name**: `TrendScout`
   - **Contact Email**: Your business email
   - **Business Account**: Select your business (or create one)
   - Click **"Create App"**

4. **Add Facebook Login Product**
   - On your app dashboard, find **"Facebook Login"** and click **"Set Up"**
   - Choose **"Web"**
   - For **Site URL**, enter: `https://trendscout.click`

5. **Configure OAuth Redirect**
   - In the left menu: **Facebook Login** > **Settings**
   - Under **"Valid OAuth Redirect URIs"**, add:
     ```
     https://trendscout.click/api/oauth/meta/callback
     ```
   - Click **"Save Changes"**

6. **Get Your Credentials**
   - In the left menu: **Settings** > **Basic**
   - Copy the **App ID** (this is your Client ID)
   - Click **"Show"** next to App Secret (this is your Client Secret)

7. **Enter in TrendScout**
   - Go to: **Settings > Connections** > **Admin: OAuth App Credentials**
   - Click **"Configure"** next to Meta
   - Paste your App ID and App Secret
   - Click **"Save"**

8. **Go Live** (Important!)
   - In Meta's left menu: **App Review** > **Requests**
   - Request these permissions: `ads_management`, `ads_read`
   - Switch your app from **Development** to **Live** mode (toggle at the top)

---

## Etsy

### What you'll get
Users can connect their Etsy shops to sync products and see listing performance.

### Step-by-step

1. **Go to Etsy Developer Portal**
   - Open: https://www.etsy.com/developers
   - Sign in with your Etsy account
   - Click **"Create a New App"**

2. **Fill in App Details**
   - **App Name**: `TrendScout`
   - **Description**: `Product validation and trend analysis tool`
   - Agree to the terms
   - Click **"Create App"**

3. **Configure Your App**
   - Once created, you'll see your **Keystring** (this is your Client ID)
   - Below it is the **Shared Secret** (this is your Client Secret)

4. **Set the Callback URL**
   - Under app settings, find **"Callback URLs"**
   - Add:
     ```
     https://trendscout.click/api/oauth/etsy/callback
     ```
   - Save

5. **Request Permissions**
   - Under **"Requested Scopes"**, check:
     - `listings_r` (read listings)
     - `shops_r` (read shop info)
     - `transactions_r` (read sales data)
   - Save

6. **Enter in TrendScout**
   - Go to: **Settings > Connections** > **Admin: OAuth App Credentials**
   - Click **"Configure"** next to Etsy
   - Paste your Keystring and Shared Secret
   - Click **"Save"**

---

## TikTok Ads

### What you'll get
Users can connect their TikTok Ads accounts to see ad performance and trending products from TikTok.

### Step-by-step

1. **Go to TikTok for Business**
   - Open: https://business-api.tiktok.com/portal/docs
   - Click **"Create App"** or go to: https://business-api.tiktok.com/portal/register

2. **Register Your App**
   - **App Name**: `TrendScout`
   - **App Type**: Choose **"Marketing API"**
   - **Description**: `Product validation and trend analysis`
   - Submit for review

3. **Wait for Approval**
   - TikTok reviews apps manually. This can take **1-3 business days**.
   - You'll receive an email when approved.

4. **Once Approved, Get Credentials**
   - Go to your app dashboard
   - Copy the **App ID** and **App Secret**

5. **Set the Redirect URI**
   - In your app settings, add this redirect URI:
     ```
     https://trendscout.click/api/oauth/tiktok_ads/callback
     ```

6. **Enter in TrendScout**
   - Go to: **Settings > Connections** > **Admin: OAuth App Credentials**
   - Click **"Configure"** next to TikTok Ads
   - Paste your App ID and App Secret
   - Click **"Save"**

---

## Google Ads

### What you'll get
Users can connect Google Ads accounts to see search ad data, keyword trends, and competition levels.

### Step-by-step

1. **Go to Google Cloud Console**
   - Open: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a Project**
   - Click the project dropdown at the top
   - Click **"New Project"**
   - Name it: `TrendScout`
   - Click **"Create"**

3. **Enable the Google Ads API**
   - Go to: **APIs & Services** > **Library**
   - Search for **"Google Ads API"**
   - Click it, then click **"Enable"**

4. **Create OAuth Credentials**
   - Go to: **APIs & Services** > **Credentials**
   - Click **"Create Credentials"** > **"OAuth 2.0 Client ID"**
   - If prompted, configure the **OAuth Consent Screen** first:
     - Choose **"External"**
     - Fill in app name: `TrendScout`, support email, etc.
     - Add scopes: `https://www.googleapis.com/auth/adwords`
     - Save and continue

5. **Set Up the OAuth Client**
   - **Application type**: Web application
   - **Name**: `TrendScout`
   - Under **"Authorized redirect URIs"**, add:
     ```
     https://trendscout.click/api/oauth/google_ads/callback
     ```
   - Click **"Create"**

6. **Get Your Credentials**
   - A popup shows your **Client ID** and **Client Secret**
   - Copy both

7. **Get a Developer Token**
   - Go to: https://ads.google.com/
   - Sign into your Google Ads account
   - Go to **Tools & Settings** > **Setup** > **API Center**
   - Apply for a **Developer Token**
   - Note: Basic access is fine for read-only data

8. **Enter in TrendScout**
   - Go to: **Settings > Connections** > **Admin: OAuth App Credentials**
   - Click **"Configure"** next to Google Ads
   - Paste your Client ID and Client Secret
   - Click **"Save"**

---

## Amazon Seller (Beta)

### What you'll get
Users can connect Amazon Seller accounts to sync product listings.

### Step-by-step

1. **Go to Amazon Seller Central**
   - Open: https://sellercentral.amazon.co.uk/
   - Navigate to **Apps & Services** > **Develop Apps**

2. **Register as a Developer**
   - Fill in your developer profile
   - Company name: Your business name
   - Primary contact: Your details

3. **Create an App**
   - Click **"Add new app client"**
   - **App name**: `TrendScout`
   - **API type**: `SP API` (Selling Partner API)
   - **OAuth Login URI**: `https://trendscout.click/api/oauth/amazon_seller/callback`
   - **OAuth Redirect URI**: `https://trendscout.click/api/oauth/amazon_seller/callback`

4. **Get Your Credentials**
   - After creation, you'll see:
     - **Client ID** (LWA Client ID)
     - **Client Secret** (LWA Client Secret)

5. **Enter in TrendScout**
   - Go to: **Settings > Connections** > **Admin: OAuth App Credentials**
   - Click **"Configure"** next to Amazon Seller
   - Paste your Client ID and Client Secret
   - Click **"Save"**

---

## Quick Reference: All Redirect URIs

| Platform       | Redirect URI |
|---------------|-------------|
| Shopify       | `https://trendscout.click/api/shopify/oauth/callback` |
| Meta          | `https://trendscout.click/api/oauth/meta/callback` |
| Etsy          | `https://trendscout.click/api/oauth/etsy/callback` |
| TikTok Ads    | `https://trendscout.click/api/oauth/tiktok_ads/callback` |
| Google Ads    | `https://trendscout.click/api/oauth/google_ads/callback` |
| Amazon Seller | `https://trendscout.click/api/oauth/amazon_seller/callback` |

---

## Troubleshooting

### "OAuth redirect URI mismatch"
Make sure the redirect URI in your app settings **exactly** matches the one in the table above. No trailing slashes, no http (must be https).

### "App not approved" / "App in development mode"
Some platforms (Meta, TikTok) require app review before going live. Until approved, only test users you add can connect.

### "Invalid client_id"
Double-check you copied the full Client ID with no extra spaces. Some platforms show it in a small font that's easy to copy incorrectly.

### "Credentials not working after saving"
Try removing and re-adding the credentials in the Admin OAuth panel. The encrypted cache refreshes automatically.
