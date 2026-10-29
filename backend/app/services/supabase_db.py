import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import Client, create_client

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY missing from backend/.env")

# Elevated credentials: never expose this client or key to the browser.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def save_scan_to_supabase(scan_record: dict) -> dict:
    user_id = scan_record.get("user_id")
    if not user_id:
        raise ValueError("user_id is required")
    file_data = scan_record.get("file", {})
    forensic_data = scan_record.get("forensic_analysis", {})
    database_row = {
        "scan_id": scan_record.get("scan_id"),
        "user_id": user_id,
        "created_at": scan_record.get("created_at"),
        "filename": file_data.get("filename"),
        "content_type": file_data.get("content_type"),
        "file_size": file_data.get("size"),
        "width": file_data.get("width"),
        "height": file_data.get("height"),
        "risk_score": forensic_data.get("risk_score"),
        "risk_level": forensic_data.get("risk_level"),
        "full_record": scan_record,
    }
    # Insert, not upsert: prevent accidental overwriting of existing scan ownership.
    response = supabase.table("scans").insert(database_row).execute()
    return response.data[0] if response.data else database_row

def get_all_scans_from_supabase(user_id: str) -> list:
    if not user_id:
        raise ValueError("user_id is required")
    response = (
        supabase.table("scans").select("full_record")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return [row["full_record"] for row in (response.data or []) if row.get("full_record")]

def get_scan_from_supabase(scan_id: str, user_id: str):
    if not user_id:
        raise ValueError("user_id is required")
    response = (
        supabase.table("scans").select("full_record")
        .eq("scan_id", scan_id).eq("user_id", user_id)
        .limit(1).execute()
    )
    return response.data[0].get("full_record") if response.data else None

def test_supabase_connection() -> bool:
    response = supabase.table("scans").select("id").limit(1).execute()
    return response.data is not None
