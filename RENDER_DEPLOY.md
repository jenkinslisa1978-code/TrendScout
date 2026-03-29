# TrendScout — Render Single-Service Deployment Guide

## Architecture

One Render **Web Service** (Python). FastAPI serves:
- `/api/*` — All backend API routes
- `/health` — K8s/Render health check (no DB dependency)
- `/*` — React SPA (built at deploy time, served as static files)

No separate frontend service. No `start.js`. No `serve.js`. No Node process at runtime.

---

## Build Command
```
pip install -r backend/requirements.txt && cd frontend && yarn install --frozen-lockfile && CI=false yarn build
```

## Start Command
```
cd backend && python -m uvicorn server:app --host 0.0.0.0 --port $PORT
```

## Health Check Path
```
/health
```

---

## Environment Variables

### Required (app crashes without these)
| Variable | Example | Notes |
|---|---|---|
| `MONGO_URL` | `mongodb+srv://user:pass@cluster.mongodb.net/trendscout` | MongoDB Atlas connection string |
| `DB_NAME` | `trendscout` | Database name |
| `SUPABASE_JWT_SECRET` | `(from Supabase dashboard)` | JWT validation for auth |
| `TOKEN_ENCRYPTION_KEY` | `f4AD9h5NAf-hcxGkib...` | Fernet key for encrypting OAuth tokens |
| `SITE_URL` | `https://trendscout.click` | Canonical site URL (emails, OAuth callbacks) |

### Auth / Payments (Stripe)
| Variable | Notes |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe API secret |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `STRIPE_STARTER_PRICE_ID` | Starter plan price ID |
| `STRIPE_PRO_PRICE_ID` | Pro plan price ID |
| `STRIPE_ELITE_PRICE_ID` | Elite plan price ID |

### AI / LLM
| Variable | Notes |
|---|---|
| `EMERGENT_LLM_KEY` | Emergent universal LLM key (GPT, Claude, Gemini) |

### Email (Resend)
| Variable | Notes |
|---|---|
| `RESEND_API_KEY` | Resend API key |
| `SENDER_EMAIL` | `noreply@trendscout.click` |

### Shopify OAuth
| Variable | Notes |
|---|---|
| `SHOPIFY_CLIENT_ID` | Shopify app client ID |
| `SHOPIFY_CLIENT_SECRET` | Shopify app client secret |
| `SHOPIFY_SCOPES` | `read_products,write_products,read_inventory,write_inventory` |

### Supplier APIs
| Variable | Notes |
|---|---|
| `CJ_API_KEY` | CJ Dropshipping API key |
| `CJ_DROPSHIPPING_API_KEY` | CJ secondary key |
| `META_AD_LIBRARY_TOKEN` | Meta Ad Library access token |
| `PEXELS_API_KEY` | Pexels image search |

### Observability
| Variable | Notes |
|---|---|
| `SENTRY_DSN` | Sentry error tracking DSN |

### Feature Flags (defaults shown)
| Variable | Default | Notes |
|---|---|---|
| `FEATURE_PRERENDER_PUBLIC` | `true` | Enable SEO prerendering |
| `FEATURE_NOJS_AUTH` | `true` | Enable no-JS auth pages |
| `FEATURE_CSP_ENFORCE` | `true` | Enforce CSP headers |
| `APP_VERSION` | `1.0.0` | Shown in admin panel |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |

### Frontend (baked at build time)
| Variable | Value for Render | Notes |
|---|---|---|
| `REACT_APP_BACKEND_URL` | `` (empty) | Empty = relative paths = same-origin |
| `REACT_APP_SUPABASE_URL` | `(from Supabase)` | Supabase project URL |
| `REACT_APP_SUPABASE_ANON_KEY` | `(from Supabase)` | Supabase anon key |
| `REACT_APP_SENTRY_DSN` | `(from Sentry)` | Frontend Sentry DSN |
| `REACT_APP_SHOPIFY_CLIENT_ID` | Same as `SHOPIFY_CLIENT_ID` | For OAuth redirect |
| `REACT_APP_GTM_ID` | `GTM-XXXXXXX` | Google Tag Manager |
| `CI` | `false` | Prevents build warnings from failing |
| `PYTHON_VERSION` | `3.11.12` | Render Python version |
| `NODE_VERSION` | `20` | Render Node version for build |

### Optional (graceful degradation if missing)
| Variable | Notes |
|---|---|
| `REDIS_URL` | Redis for caching (falls back to in-memory) |
| `JWT_SECRET` | Falls back to SUPABASE_JWT_SECRET |
| `ADMIN_EMAILS` | Comma-separated admin email list |

---

## Files Changed

| File | Change |
|---|---|
| `backend/common/database.py` | Lazy proxy; crashes with `sys.exit(1)` if MONGO_URL/DB_NAME missing |
| `backend/database.py` | Re-export shim → `common.database` |
| `backend/server.py` | Hardened SPA serving: path traversal guard, `/api/*` 404 guard, startup logging |
| `render.yaml` | New: single web service config |

## Files NOT used in production (but kept for local dev)
- `frontend/start.js` — Local dev startup script
- `frontend/serve.js` — Local dev static server with SSR
- `frontend/prerender.js` — Runs at BUILD TIME only (in yarn build)

---

## Remaining Blockers: None

All routes work through a single FastAPI process on `$PORT`.
