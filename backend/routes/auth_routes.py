"""Authentication routes: register, login, profile."""
from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone
import uuid

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.helpers import generate_auth_token

from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

auth_router = APIRouter(prefix="/api/auth")


@auth_router.get("/profile")
async def auth_profile(current_user: AuthenticatedUser = Depends(get_current_user)):
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    if not profile:
        profile = {
            "id": current_user.user_id,
            "email": current_user.email,
            "is_admin": current_user.email == "jenkinslisa1978@gmail.com",
            "subscription_plan": "free",
        }
        await db.profiles.update_one(
            {"id": current_user.user_id},
            {"$set": profile},
            upsert=True,
        )
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
    return {
        "token": token,
        "user": {"id": user_id, "email": email, "full_name": full_name},
    }


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
    return {
        "token": token,
        "user": {"id": user["id"], "email": email, "full_name": user.get("full_name", "")},
    }


routers = [auth_router]
