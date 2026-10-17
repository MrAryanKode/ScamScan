from datetime import datetime
from uuid import uuid4

from app.services.supabase_db import (
    save_scan_to_supabase,
    get_all_scans_from_supabase,
    get_scan_from_supabase
)


# ---------------------------------------------------------
# Generate a unique scan ID
# ---------------------------------------------------------
# Example:
# SCN-20260924-A1B2C3

def generate_scan_id() -> str:
    """
    Generate a readable unique scan identifier.
    """

    current_date = datetime.now().strftime("%Y%m%d")

    unique_part = uuid4().hex[:6].upper()

    return f"SCN-{current_date}-{unique_part}"


# ---------------------------------------------------------
# Save scan record
# ---------------------------------------------------------
# We preserve the previous function name so scan.py
# does not require major changes.

def save_scan_record(scan_record: dict) -> None:
    """
    Save a scan record permanently in Supabase.
    """

    save_scan_to_supabase(scan_record)


# ---------------------------------------------------------
# Retrieve all scan records
# ---------------------------------------------------------

def get_all_scan_records() -> list:
    """
    Return all saved scan records.
    """

    return get_all_scans_from_supabase()


# ---------------------------------------------------------
# Retrieve one scan record
# ---------------------------------------------------------

def get_scan_by_id(scan_id: str):
    """
    Find a scan using its unique scan ID.
    """

    return get_scan_from_supabase(scan_id)