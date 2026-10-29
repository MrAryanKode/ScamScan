
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client

# Import existing Supabase configuration.
from app.services.supabase_db import (
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY,
)

# Load the public/anonymous key from backend/.env.
# supabase_db loads the backend .env during import.
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing from backend/.env")

if not SUPABASE_ANON_KEY:
    raise RuntimeError(
        "SUPABASE_ANON_KEY is missing from backend/.env"
    )

if not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_KEY is missing from backend/.env"
    )

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

security = HTTPBearer(auto_error=False)


def get_auth_client():
    """Create a Supabase client for user authentication."""
    return create_client(
        SUPABASE_URL,
        SUPABASE_ANON_KEY,
    )


class RegisterInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


@router.post("/register", status_code=201)
def register(data: RegisterInput):
    """Register a user using Supabase Auth."""
    try:
        client = get_auth_client()

        response = client.auth.sign_up({
            "email": str(data.email).strip().lower(),
            "password": data.password,
            "options": {
                "data": {
                    "name": data.name.strip(),
                }
            },
        })

        user = response.user

        if not user:
            raise HTTPException(
                status_code=400,
                detail="Registration could not be completed.",
            )

        return {
            "message": (
                "Account created. Check your email "
                "if verification is required."
            ),
            "user": {
                "id": user.id,
                "email": user.email,
                "name": data.name.strip(),
            },
            "access_token": (
                response.session.access_token
                if response.session
                else None
            ),
            "token_type": "bearer",
        }

    except HTTPException:
        raise
    except Exception as exc:
        # Keep internal Supabase errors out of the public response.
        print(f"ScamScan registration error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=400,
            detail=(
                "Registration failed. Check the server logs, "
                "email configuration, and Supabase settings."
            ),
        ) from exc


@router.post("/login")
def login(data: LoginInput):
    """Sign in an existing user."""
    try:
        client = get_auth_client()

        response = client.auth.sign_in_with_password({
            "email": str(data.email).strip().lower(),
            "password": data.password,
        })

        if not response.user or not response.session:
            raise HTTPException(
                status_code=401,
                detail="Login failed. Verify your email if required.",
            )

        user = response.user

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": (user.user_metadata or {}).get("name", ""),
            },
        }

    except HTTPException:
        raise
    except Exception as exc:
        print(f"ScamScan login error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=401,
            detail="Login failed. Check credentials and email verification.",
        ) from exc


@router.get("/me")
def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    """Validate a bearer token and return its user."""
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Please sign in first.",
        )

    try:
        # Use a separate admin client to verify the supplied user token.
        # Do not pass ClientOptions from an incompatible SDK version.
        admin_client = create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_KEY,
        )

        response = admin_client.auth.get_user(
            credentials.credentials
        )

        user = response.user

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid session.",
            )

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": (user.user_metadata or {}).get("name", ""),
            }
        }

    except HTTPException:
        raise
    except Exception as exc:
        print(f"ScamScan current-user error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session.",
        ) from exc
