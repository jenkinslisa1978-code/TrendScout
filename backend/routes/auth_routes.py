"""Authentication routes: register, login, refresh, logout, profile, server-rendered forms."""
from fastapi import APIRouter, HTTPException, Request, Depends, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from datetime import datetime, timezone
import uuid
import os

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.helpers import generate_auth_token, generate_refresh_token, verify_refresh_token, set_auth_cookies
from common.limiter import limiter

auth_router = APIRouter(prefix="/api/auth")


ADMIN_EMAILS = set(
    e.strip() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()
) | {"jenkinslisa1978@gmail.com", "reviewer@trendscout.click"}


@auth_router.get("/profile")
async def auth_profile(current_user: AuthenticatedUser = Depends(get_current_user)):
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    if not profile:
        profile = {
            "id": current_user.user_id,
            "email": current_user.email,
            "is_admin": current_user.email in ADMIN_EMAILS,
            "role": "admin" if current_user.email in ADMIN_EMAILS else "user",
            "subscription_plan": "free",
        }
        await db.profiles.update_one(
            {"id": current_user.user_id},
            {"$set": profile},
            upsert=True,
        )
    # Always sync admin status from email list
    if current_user.email in ADMIN_EMAILS and (not profile.get("is_admin") or profile.get("role") != "admin"):
        await db.profiles.update_one(
            {"id": current_user.user_id},
            {"$set": {"is_admin": True, "role": "admin"}}
        )
        profile["is_admin"] = True
        profile["role"] = "admin"
    return profile


@auth_router.post("/register")
@limiter.limit("5/minute")
async def auth_register(request: Request):
    import bcrypt
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    full_name = body.get("full_name", "")

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = await db.auth_users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered. Try logging in.")

    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    await db.auth_users.insert_one({
        "id": user_id,
        "email": email,
        "password_hash": password_hash,
        "full_name": full_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    is_admin = email == "jenkinslisa1978@gmail.com"
    await db.profiles.update_one(
        {"email": email},
        {"$set": {
            "id": user_id,
            "email": email,
            "name": full_name or email.split("@")[0],
            "is_admin": is_admin,
            "subscription_plan": "elite" if is_admin else "free",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )

    token = generate_auth_token(user_id, email)
    response = JSONResponse(content={
        "token": token,
        "user": {"id": user_id, "email": email, "full_name": full_name},
    })
    set_auth_cookies(response, user_id, email)

    # Send welcome email in background (don't block the response)
    import asyncio
    from services.email_service import send_welcome_email
    asyncio.create_task(send_welcome_email(email, full_name.split()[0] if full_name else ""))

    return response


@auth_router.post("/login")
@limiter.limit("10/minute")
async def auth_login(request: Request):
    import bcrypt
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = await db.auth_users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = generate_auth_token(user["id"], email)
    response = JSONResponse(content={
        "token": token,
        "user": {"id": user["id"], "email": email, "full_name": user.get("full_name", "")},
    })
    set_auth_cookies(response, user["id"], email)
    return response


@auth_router.post("/refresh")
@limiter.limit("5/minute")
async def auth_refresh(request: Request):
    """Exchange a valid __Host-refresh cookie for a new short-lived access token."""
    refresh_cookie = request.cookies.get("__Host-refresh")
    if not refresh_cookie:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = verify_refresh_token(refresh_cookie)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = payload["sub"]
    email = payload.get("email", "")

    # Verify user still exists
    user = await db.auth_users.find_one({"id": user_id}, {"_id": 0, "id": 1, "email": 1})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = generate_auth_token(user_id, email)
    response = JSONResponse(content={"token": new_access})
    # Rotate refresh token
    set_auth_cookies(response, user_id, email)
    return response


@auth_router.post("/logout")
async def auth_logout():
    """Clear auth cookies."""
    response = JSONResponse(content={"success": True})
    response.delete_cookie("__Host-refresh", path="/")
    response.delete_cookie("__Host-csrf", path="/")
    return response


# --- Forgot / Reset Password ---

@auth_router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(request: Request):
    """Generate a password reset token. Returns the reset link in response (no email service configured)."""
    import secrets
    body = await request.json()
    email = body.get("email", "").strip().lower()

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")

    user = await db.auth_users.find_one({"email": email}, {"_id": 0, "id": 1, "email": 1})

    # Always return success to prevent email enumeration
    if not user:
        return {"success": True, "message": "If an account with that email exists, a reset link has been sent."}

    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc).isoformat()

    # Store reset token (expires in 1 hour)
    await db.password_resets.delete_many({"user_id": user["id"]})
    await db.password_resets.insert_one({
        "user_id": user["id"],
        "email": email,
        "token": reset_token,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at_epoch": int(datetime.now(timezone.utc).timestamp()) + 3600,
    })

    site_url = os.environ.get("SITE_URL", request.headers.get("origin", ""))
    reset_link = f"{site_url}/reset-password?token={reset_token}"

    # Send email via Resend
    from services.email_service import send_password_reset_email
    email_sent = await send_password_reset_email(email, reset_link)

    import logging
    logging.getLogger(__name__).info(f"Password reset requested for {email} (email_sent={email_sent})")

    result = {
        "success": True,
        "message": "If an account with that email exists, a reset link has been sent.",
    }
    # Include reset_link in response for dev/testing (remove in production)
    if not email_sent:
        result["reset_link"] = reset_link
    return result


@auth_router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request):
    """Reset password using a valid reset token."""
    import bcrypt
    body = await request.json()
    token = body.get("token", "").strip()
    new_password = body.get("password", "")

    if not token:
        raise HTTPException(status_code=400, detail="Reset token is required")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.isdigit() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")

    # Find reset record
    reset = await db.password_resets.find_one({"token": token}, {"_id": 0})
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Check expiry
    import time
    if reset.get("expires_at_epoch", 0) < int(time.time()):
        await db.password_resets.delete_one({"token": token})
        raise HTTPException(status_code=400, detail="Reset token has expired. Please request a new one.")

    # Update password
    password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    await db.auth_users.update_one(
        {"id": reset["user_id"]},
        {"$set": {"password_hash": password_hash}},
    )

    # Clean up token
    await db.password_resets.delete_many({"user_id": reset["user_id"]})

    return {"success": True, "message": "Password has been reset. You can now log in."}


# --- Server-rendered auth forms (work without JavaScript) ---

_FORM_STYLE = """
body { font-family: 'Manrope','Inter',system-ui,sans-serif; background:#0f172a; color:#e2e8f0; display:flex; justify-content:center; align-items:center; min-height:100vh; margin:0; }
.card { background:#1e293b; border:1px solid #334155; border-radius:16px; padding:40px; width:100%; max-width:400px; }
h1 { font-size:24px; font-weight:700; color:#fff; margin:0 0 8px; }
.sub { color:#94a3b8; font-size:14px; margin-bottom:24px; }
label { display:block; font-size:13px; font-weight:500; color:#cbd5e1; margin-bottom:4px; }
input { width:100%; padding:10px 14px; border:1px solid #334155; border-radius:10px; background:#0f172a; color:#fff; font-size:14px; margin-bottom:16px; box-sizing:border-box; }
input:focus { outline:none; border-color:#6366f1; }
button { width:100%; padding:12px; background:linear-gradient(135deg,#6366f1,#8b5cf6); color:#fff; border:none; border-radius:10px; font-size:14px; font-weight:600; cursor:pointer; }
button:hover { opacity:0.9; }
.link { text-align:center; margin-top:16px; font-size:13px; color:#94a3b8; }
.link a { color:#818cf8; text-decoration:none; }
.error { background:#7f1d1d; color:#fca5a5; border-radius:8px; padding:10px; margin-bottom:16px; font-size:13px; }
.brand { display:flex; align-items:center; gap:8px; margin-bottom:24px; }
.brand svg { width:28px; height:28px; }
.brand span { font-size:18px; font-weight:700; color:#fff; }
nav { display:flex; gap:16px; justify-content:center; margin-bottom:24px; }
nav a { color:#94a3b8; font-size:13px; text-decoration:none; }
nav a:hover { color:#fff; }
"""

SITE_URL = os.environ.get("SITE_URL", "")


@auth_router.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    error_html = f'<div class="error">{error}</div>' if error else ""
    return HTMLResponse(f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Log In - TrendScout</title>
<meta name="description" content="Log in to TrendScout to discover trending products and grow your ecommerce business.">
<style>{_FORM_STYLE}</style></head><body>
<div class="card">
<div class="brand"><svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#6366f1"/><path d="M8 12l3 3 5-5" stroke="#fff" stroke-width="2"/></svg><span>TrendScout</span></div>
<nav><a href="/">Home</a><a href="/trending-products">Products</a><a href="/pricing">Pricing</a></nav>
<h1>Welcome back</h1><p class="sub">Log in to your account</p>
{error_html}
<form method="POST" action="/api/auth/login-submit">
<label for="email">Email</label><input type="email" id="email" name="email" required placeholder="you@example.com">
<label for="password">Password</label><input type="password" id="password" name="password" required placeholder="Your password" minlength="6">
<button type="submit">Log In</button>
</form>
<p class="link">Don't have an account? <a href="/api/auth/signup-page">Sign up</a> | <a href="/login">JS App</a></p>
</div></body></html>""")


@auth_router.post("/login-submit")
@limiter.limit("10/minute")
async def login_submit(request: Request):
    """Handle no-JS form login. Redirects on success."""
    import bcrypt
    form = await request.form()
    email = (form.get("email") or "").strip().lower()
    password = form.get("password") or ""

    if not email or not password:
        return RedirectResponse(url="/api/auth/login-page?error=Email+and+password+required", status_code=303)

    user = await db.auth_users.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return RedirectResponse(url="/api/auth/login-page?error=Invalid+email+or+password", status_code=303)

    response = RedirectResponse(url="/dashboard", status_code=303)
    set_auth_cookies(response, user["id"], email)
    return response


@auth_router.get("/signup-page", response_class=HTMLResponse)
async def signup_page(request: Request, error: str = ""):
    error_html = f'<div class="error">{error}</div>' if error else ""
    return HTMLResponse(f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sign Up - TrendScout</title>
<meta name="description" content="Create a free TrendScout account to discover trending products.">
<style>{_FORM_STYLE}</style></head><body>
<div class="card">
<div class="brand"><svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#6366f1"/><path d="M8 12l3 3 5-5" stroke="#fff" stroke-width="2"/></svg><span>TrendScout</span></div>
<nav><a href="/">Home</a><a href="/trending-products">Products</a><a href="/pricing">Pricing</a></nav>
<h1>Create account</h1><p class="sub">Start discovering winning products</p>
{error_html}
<form method="POST" action="/api/auth/signup-submit">
<label for="name">Full Name</label><input type="text" id="name" name="full_name" placeholder="Jane Smith">
<label for="email">Email</label><input type="email" id="email" name="email" required placeholder="you@example.com">
<label for="password">Password</label><input type="password" id="password" name="password" required placeholder="Min 6 characters" minlength="6">
<button type="submit">Sign Up Free</button>
</form>
<p class="link">Already have an account? <a href="/api/auth/login-page">Log in</a> | <a href="/signup">JS App</a></p>
</div></body></html>""")


@auth_router.post("/signup-submit")
@limiter.limit("5/minute")
async def signup_submit(request: Request):
    """Handle no-JS form signup. Redirects on success."""
    import bcrypt
    form = await request.form()
    email = (form.get("email") or "").strip().lower()
    password = form.get("password") or ""
    full_name = form.get("full_name") or ""

    if not email or "@" not in email:
        return RedirectResponse(url="/api/auth/signup-page?error=Valid+email+required", status_code=303)
    if len(password) < 6:
        return RedirectResponse(url="/api/auth/signup-page?error=Password+must+be+at+least+6+characters", status_code=303)

    existing = await db.auth_users.find_one({"email": email})
    if existing:
        return RedirectResponse(url="/api/auth/signup-page?error=Email+already+registered", status_code=303)

    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    await db.auth_users.insert_one({
        "id": user_id,
        "email": email,
        "password_hash": password_hash,
        "full_name": full_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    is_admin = email == "jenkinslisa1978@gmail.com"
    await db.profiles.update_one(
        {"email": email},
        {"$set": {
            "id": user_id,
            "email": email,
            "name": full_name or email.split("@")[0],
            "is_admin": is_admin,
            "subscription_plan": "elite" if is_admin else "free",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )

    response = RedirectResponse(url="/dashboard", status_code=303)
    set_auth_cookies(response, user_id, email)

    # Send welcome email in background
    import asyncio
    from services.email_service import send_welcome_email
    asyncio.create_task(send_welcome_email(email, full_name.split()[0] if full_name else ""))

    return response


routers = [auth_router]
