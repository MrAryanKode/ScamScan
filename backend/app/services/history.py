from datetime import datetime
from uuid import uuid4
from app.services.supabase_db import (
    save_scan_to_supabase, get_all_scans_from_supabase, get_scan_from_supabase
)

def generate_scan_id() -> str:
    return f"SCN-{datetime.now():%Y%m%d}-{uuid4().hex[:6].upper()}"

def save_scan_record(scan_record: dict) -> None:
    if not scan_record.get("user_id"):
        raise ValueError("Authenticated user_id required to save a scan")
    save_scan_to_supabase(scan_record)

def get_all_scan_records(user_id: str) -> list:
    if not user_id:
        raise ValueError("Authenticated user_id required")
    return get_all_scans_from_supabase(user_id)

def get_scan_by_id(scan_id: str, user_id: str):
    if not user_id:
        raise ValueError("Authenticated user_id required")
    return get_scan_from_supabase(scan_id, user_id)
