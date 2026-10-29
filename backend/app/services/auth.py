import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client
from app.services.supabase_db import SUPABASE_URL, SUPABASE_SERVICE_KEY

SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
if not SUPABASE_ANON_KEY:
    raise RuntimeError("SUPABASE_ANON_KEY is missing from backend/.env")

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)

def get_auth_client():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

class RegisterInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

@router.post("/register", status_code=201)
def register(data: RegisterInput):
    try:
        response = get_auth_client().auth.sign_up({
            "email": str(data.email).strip().lower(),
            "password": data.password,
            "options": {"data": {"name": data.name.strip()}},
        })
        if not response.user:
            raise HTTPException(status_code=400, detail="Registration could not be completed.")
        return {
            "message": "Account created. Check your email if verification is required.",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "name": data.name.strip(),
            },
            "access_token": response.session.access_token if response.session else None,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Registration error: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=400, detail="Registration failed.") from exc

@router.post("/login")
def login(data: LoginInput):
    try:
        response = get_auth_client().auth.sign_in_with_password({
            "email": str(data.email).strip().lower(),
            "password": data.password,
        })
        if not response.user or not response.session:
            raise HTTPException(status_code=401, detail="Login failed.")
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
        print(f"Login error: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=401, detail="Login failed.") from exc

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    """Verify bearer token server-side. Never trust a client-supplied user ID."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Please sign in first.")
    try:
        admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        response = admin_client.auth.get_user(credentials.credentials)
        user = response.user
        if not user:
            raise HTTPException(status_code=401, detail="Invalid session.")
        return {"user": {
            "id": user.id,
            "email": user.email,
            "name": (user.user_metadata or {}).get("name", ""),
        }}
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Token verification error: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=401, detail="Invalid or expired session.") from exc

@router.get("/me")
def me(auth: dict = Depends(current_user)):
    return auth
