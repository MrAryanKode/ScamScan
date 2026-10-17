import os
from pathlib import Path

import requests

from dotenv import load_dotenv
from fastapi import Header, HTTPException


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
# The .env file contains our Supabase project URL
# and backend service key.

BACKEND_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# Read Supabase configuration
# ---------------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_SERVICE_KEY = os.getenv(
    "SUPABASE_SERVICE_KEY"
)


# ---------------------------------------------------------
# Validate configuration
# ---------------------------------------------------------

if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL is missing from backend/.env"
    )

if not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_KEY is missing from backend/.env"
    )


# ---------------------------------------------------------
# Verify the user's access token
# ---------------------------------------------------------
# Supabase validates the token and returns the user data.
# This avoids depending on the legacy HS256 JWT secret.

def get_current_user(
    authorization: str | None = Header(default=None)
) -> dict:
    """
    Verify a Supabase Bearer access token.
    """

    # -----------------------------------------------------
    # Check authorization header
    # -----------------------------------------------------

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format."
        )

    access_token = authorization.replace(
        "Bearer ",
        "",
        1
    ).strip()

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token is missing."
        )

    # -----------------------------------------------------
    # Ask Supabase to validate the token
    # -----------------------------------------------------

    user_url = f"{SUPABASE_URL}/auth/v1/user"

    headers = {
        "Authorization": f"Bearer {access_token}",

        "apikey": SUPABASE_SERVICE_KEY
    }

    try:
        response = requests.get(
            user_url,
            headers=headers,
            timeout=10
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Unable to contact Supabase authentication."
        )

    # -----------------------------------------------------
    # Reject invalid or expired tokens
    # -----------------------------------------------------

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token."
        )

    user_data = response.json()

    # -----------------------------------------------------
    # Return only required user information
    # -----------------------------------------------------

    return {
        "user_id": user_data.get("id"),

        "email": user_data.get("email"),

        "role": user_data.get("role")
    }