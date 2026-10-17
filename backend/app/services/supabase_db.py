import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
# The .env file is located inside the backend folder.
# This file contains our Supabase URL and secret key.

BACKEND_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# Read Supabase credentials
# ---------------------------------------------------------
# These values are loaded from backend/.env.
# The secret key must never be exposed to the frontend.

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


# ---------------------------------------------------------
# Validate the credentials
# ---------------------------------------------------------
# Clear errors help us identify missing configuration.

if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL is missing from backend/.env"
    )

if not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_KEY is missing from backend/.env"
    )


# ---------------------------------------------------------
# Create Supabase client
# ---------------------------------------------------------
# This client communicates with the Supabase database.

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)


# ---------------------------------------------------------
# Save scan record
# ---------------------------------------------------------
# The complete scan response is stored in the JSONB column
# named full_record.

def save_scan_to_supabase(scan_record: dict) -> dict:
    """
    Permanently save a ScamScan record in Supabase.
    """

    file_data = scan_record.get("file", {})

    forensic_data = scan_record.get(
        "forensic_analysis",
        {}
    )

    database_row = {
        "scan_id": scan_record.get("scan_id"),

        "created_at": scan_record.get("created_at"),

        "filename": file_data.get("filename"),

        "content_type": file_data.get("content_type"),

        "file_size": file_data.get("size"),

        "width": file_data.get("width"),

        "height": file_data.get("height"),

        "risk_score": forensic_data.get("risk_score"),

        "risk_level": forensic_data.get("risk_level"),

        "full_record": scan_record
    }

    response = (
        supabase
        .table("scans")
        .upsert(
            database_row,
            on_conflict="scan_id"
        )
        .execute()
    )

    return response.data[0] if response.data else database_row


# ---------------------------------------------------------
# Retrieve all scan records
# ---------------------------------------------------------
# Newest scans are returned first.

def get_all_scans_from_supabase() -> list:
    """
    Retrieve all saved scan records.
    """

    response = (
        supabase
        .table("scans")
        .select("full_record")
        .order("created_at", desc=True)
        .execute()
    )

    records = []

    for row in response.data or []:
        full_record = row.get("full_record")

        if full_record:
            records.append(full_record)

    return records


# ---------------------------------------------------------
# Retrieve one scan record
# ---------------------------------------------------------

def get_scan_from_supabase(scan_id: str):
    """
    Retrieve one scan using its unique scan ID.
    """

    response = (
        supabase
        .table("scans")
        .select("full_record")
        .eq("scan_id", scan_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0].get("full_record")


# ---------------------------------------------------------
# Test Supabase connection
# ---------------------------------------------------------
# This checks whether our backend can access the scans table.

def test_supabase_connection() -> bool:
    """
    Test the connection with Supabase.
    """

    response = (
        supabase
        .table("scans")
        .select("id")
        .limit(1)
        .execute()
    )

    return response.data is not None