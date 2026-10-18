
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client
from supabase.lib.client_options import ClientOptions

from app.services.supabase_db import (
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY,
)

ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not ANON_KEY:
    raise RuntimeError(
        "SUPABASE_ANON_KEY is missing from backend/.env"
    )

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


def get_auth_client():
    # Create an isolated client so concurrent logins
    # do not share the same in-memory auth session.
    return create_client(
        SUPABASE_URL,
        ANON_KEY,
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )


class RegisterInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


def error_response(message: str, code: int = 400):
    raise HTTPException(status_code=code, detail=message)


@router.post("/register", status_code=201)
def register(data: RegisterInput):
    client = get_auth_client()

    try:
        response = client.auth.sign_up({
            "email": str(data.email).strip().lower(),
            "password": data.password,
            "options": {
                "data": {"name": data.name.strip()}
            },
        })

        user = response.user
        if not user:
            error_response("Registration could not be completed.")

        return {
            "message": (
                "Account created. Check your email if verification is required."
            ),
            "user": {
                "id": user.id,
                "email": user.email,
                "name": data.name.strip(),
            },
            "access_token": (
                response.session.access_token
                if response.session else None
            ),
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception:
        error_response(
            "Registration failed. Check the email and try again."
        )


@router.post("/login")
def login(data: LoginInput):
    client = get_auth_client()

    try:
        response = client.auth.sign_in_with_password({
            "email": str(data.email).strip().lower(),
            "password": data.password,
        })

        if not response.user or not response.session:
            error_response(
                "Login failed. Verify your email if required.",
                401,
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "name": (
                    response.user.user_metadata or {}
                ).get("name", ""),
            },
        }
    except HTTPException:
        raise
    except Exception:
        error_response("Incorrect email or password.", 401)


@router.get("/me")
def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if credentials is None:
        error_response("Please sign in first.", 401)

    try:
        # Verify the supplied user token against Supabase Auth.
        admin_client = create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_KEY,
            options=ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
            ),
        )
        response = admin_client.auth.get_user(
            credentials.credentials
        )
        user = response.user

        if not user:
            error_response("Invalid session.", 401)

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": (user.user_metadata or {}).get("name", ""),
            }
        }
    except HTTPException:
        raise
    except Exception:
        error_response("Invalid or expired session.", 401)
