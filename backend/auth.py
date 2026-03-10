"""
Authentication module for ViralScout API.
Handles JWT verification using Supabase tokens.
"""

import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Security scheme for extracting Bearer token
security = HTTPBearer(auto_error=False)

# Supabase JWT configuration
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")
ALGORITHM = "HS256"


class AuthenticatedUser:
    """Represents an authenticated user extracted from JWT"""
    def __init__(self, user_id: str, email: Optional[str] = None, role: str = "authenticated"):
        self.user_id = user_id
        self.email = email
        self.role = role
    
    def __repr__(self):
        return f"AuthenticatedUser(user_id={self.user_id}, email={self.email})"


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> AuthenticatedUser:
    """
    Dependency that extracts and verifies the user from a Supabase JWT token.
    
    Returns:
        AuthenticatedUser: The authenticated user with user_id from the token
        
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 403: If user role is not authenticated
    """
    # Check if JWT secret is configured
    if not SUPABASE_JWT_SECRET:
        # In development/demo mode without JWT secret, check for demo token
        if credentials and credentials.credentials:
            token = credentials.credentials
            # Handle demo mode tokens (prefixed with "demo_")
            if token.startswith("demo_"):
                demo_user_id = token.replace("demo_", "")
                logger.info(f"Demo mode: Authenticated as user {demo_user_id}")
                return AuthenticatedUser(user_id=demo_user_id, role="demo")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication not configured. Please provide SUPABASE_JWT_SECRET.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Require credentials
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=[ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["sub", "exp"]
            }
        )
        
        # Extract user ID (Supabase uses 'sub' claim as UUID)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify role is authenticated (Supabase includes this claim)
        role = payload.get("role", "")
        if role not in ["authenticated", "service_role"]:
            logger.warning(f"Token has invalid role: {role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role. Token must be from authenticated user.",
            )
        
        # Extract email if available
        email = payload.get("email")
        
        return AuthenticatedUser(
            user_id=user_id,
            email=email,
            role=role
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AuthenticatedUser]:
    """
    Optional authentication dependency.
    Returns None if no valid token provided (useful for public endpoints
    that have enhanced behavior for authenticated users).
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
