from datetime import datetime
from io import BytesIO

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile
)

from PIL import Image, UnidentifiedImageError


# ---------------------------------------------------------
# Forensic services
# ---------------------------------------------------------

from app.services.ela import (
    perform_ela
)

from app.services.edge_analysis import (
    perform_edge_analysis
)

from app.services.heatmap import (
    perform_heatmap_analysis
)

from app.services.risk_engine import (
    calculate_risk
)

from app.services.ocr import (
    extract_text_from_image
)

from app.services.evidence import (
    save_evidence_image
)

from app.services.findings import (
    generate_findings
)

from app.services.ai_detection import (
    analyze_ai_generation
)


# ---------------------------------------------------------
# Scan history services
# ---------------------------------------------------------

from app.services.history import (
    generate_scan_id,
    save_scan_record,
    get_all_scan_records,
    get_scan_by_id
)


# ---------------------------------------------------------
# Create router
# ---------------------------------------------------------

router = APIRouter(
    prefix="/api/scan",
    tags=["Scan"]
)


# ---------------------------------------------------------
# Allowed image formats
# ---------------------------------------------------------

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


# ---------------------------------------------------------
# Validate uploaded file
# ---------------------------------------------------------

def validate_file_type(
    file: UploadFile
) -> None:

    if file.content_type not in ALLOWED_CONTENT_TYPES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload JPEG, PNG, or WEBP."
            )
        )


# ---------------------------------------------------------
# Validate actual image
# ---------------------------------------------------------

def validate_image_bytes(
    file_bytes: bytes
) -> tuple[int, int]:

    try:

        image = Image.open(
            BytesIO(file_bytes)
        )

        width, height = image.size

        image.verify()

        return width, height

    except UnidentifiedImageError:

        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded file is not "
                "a valid image."
            )
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to read the uploaded image."
            )
        )


# ---------------------------------------------------------
# Create evidence URL
# ---------------------------------------------------------

def create_output_url(
    filename: str
) -> str:

    return f"/outputs/{filename}"


# ---------------------------------------------------------
# Calculate ELA score
# ---------------------------------------------------------
# Your current ela.py only returns the ELA image.
# Therefore we calculate a simple numerical indicator
# directly from that generated ELA image.

def calculate_ela_score(
    ela_bytes: bytes
) -> float:

    try:

        image = Image.open(
            BytesIO(ela_bytes)
        ).convert("L")

        pixels = list(
            image.getdata()
        )

        if not pixels:

            return 0.0

        mean_value = sum(
            pixels
        ) / len(pixels)

        # Normalize the average ELA intensity
        # into a 0-100 supporting score.

        score = min(
            100.0,
            mean_value
        )

        return round(
            score,
            2
        )

    except Exception:

        return 0.0


# =========================================================
# Health Check
# =========================================================

@router.get("/")
def scan_home():

    return {
        "message": "ScamScan scan API is working",
        "status": "success"
    }


# =========================================================
# 1. Upload Validation
# =========================================================

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    validate_file_type(file)

    file_bytes = await file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    width, height = validate_image_bytes(
        file_bytes
    )

    return {

        "message": (
            "File uploaded and validated successfully"
        ),

        "filename": file.filename,

        "content_type": file.content_type,

        "size": len(file_bytes),

        "width": width,

        "height": height,

        "status": "success"
    }


# =========================================================
# 2. ELA Analysis
# =========================================================

@router.post("/ela")
async def ela_analysis(
    file: UploadFile = File(...)
):

    validate_file_type(file)

    file_bytes = await file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    width, height = validate_image_bytes(
        file_bytes
    )

    ela_bytes = perform_ela(
        file_bytes
    )

    saved_filename = save_evidence_image(
        ela_bytes,
        "ela"
    )

    return {

        "message": "ELA analysis completed",

        "filename": file.filename,

        "image_dimensions": {

            "width": width,

            "height": height
        },

        "evidence_image": {

            "filename": saved_filename,

            "url": create_output_url(
                saved_filename
            )
        },

        "status": "success"
    }


# =========================================================
# 3. Edge Analysis
# =========================================================

@router.post("/edges")
async def edge_analysis(
    file: UploadFile = File(...)
):

    validate_file_type(file)

    file_bytes = await file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    width, height = validate_image_bytes(
        file_bytes
    )

    edge_result = perform_edge_analysis(
        file_bytes
    )

    edge_bytes = edge_result["image"]

    saved_filename = save_evidence_image(
        edge_bytes,
        "edges"
    )

    return {

        "message": "Edge analysis completed",

        "filename": file.filename,

        "image_dimensions": {

            "width": width,

            "height": height
        },

        "edge_analysis": {

            "edge_pixel_count": (
                edge_result["edge_pixel_count"]
            ),

            "edge_density": (
                edge_result["edge_density"]
            )
        },

        "evidence_image": {

            "filename": saved_filename,

            "url": create_output_url(
                saved_filename
            )
        },

        "status": "success"
    }


# =========================================================
# 4. Heatmap Analysis
# =========================================================

@router.post("/heatmap")
async def heatmap_analysis(
    file: UploadFile = File(...)
):

    validate_file_type(file)

    file_bytes = await file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    width, height = validate_image_bytes(
        file_bytes
    )

    heatmap_result = perform_heatmap_analysis(
        file_bytes
    )

    heatmap_bytes = heatmap_result["image"]

    saved_filename = save_evidence_image(
        heatmap_bytes,
        "heatmap"
    )

    return {

        "message": (
            "Heatmap analysis completed"
        ),

        "filename": file.filename,

        "image_dimensions": {

            "width": width,

            "height": height
        },

        "heatmap_analysis": {

            "mean_intensity": (
                heatmap_result["mean_intensity"]
            ),

            "maximum_intensity": (
                heatmap_result["maximum_intensity"]
            ),

            "high_activity_ratio": (
                heatmap_result["high_activity_ratio"]
            )
        },

        "evidence_image": {

            "filename": saved_filename,

            "url": create_output_url(
                saved_filename
            )
        },

        "important_note": (
            "The heatmap highlights regions "
            "for investigation. It does not "
            "independently prove manipulation."
        ),

        "status": "success"
    }


# =========================================================
# 5. Risk Analysis
# =========================================================

@router.post("/risk")
async def risk_analysis(
    file: UploadFile = File(...)
):

    validate_file_type(file)

    file_bytes = await file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    width, height = validate_image_bytes(
        file_bytes
    )

    # ELA

    ela_bytes = perform_ela(
        file_bytes
    )

    ela_score = calculate_ela_score(
        ela_bytes
    )

    # Edge analysis

    edge_result = perform_edge_analysis(
        file_bytes
    )

    edge_score = min(
        100,
        edge_result["edge_density"] * 4
    )

    # Heatmap

    heatmap_result = perform_heatmap_analysis(
        file_bytes
    )

    heatmap_score = min(
        100,
        heatmap_result["high_activity_ratio"]
    )

    # OCR

    ocr_result = extract_text_from_image(
        file_bytes
    )

    ocr_text_length = ocr_result.get(
        "text_length",
        ocr_result.get(
            "character_count",
            len(
                ocr_result.get(
                    "text",
                    ""
                )
            )
        )
    )

    # Current risk engine

    risk_result = calculate_risk(
        ela_score=ela_score,
        edge_score=edge_score,
        heatmap_score=heatmap_score,
        ocr_text_length=ocr_text_length
    )

    return {

        "message": "Risk analysis completed",

        "filename": file.filename,

        "image_dimensions": {

            "width": width,

            "height": height
        },

        "forensic_analysis": risk_result,

        "status": "success"
    }


# =========================================================
# 6. OCR Analysis
# =========================================================

@router.post("/ocr")
async def ocr_analysis(
    file: UploadFile = File(...)
):

    validate_file_type(file)

    file_bytes = await file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    width, height = validate_image_bytes(
        file_bytes
    )

    ocr_result = extract_text_from_image(
        file_bytes
    )

    return {

        "message": "OCR processing completed",

        "filename": file.filename,

        "image_dimensions": {

            "width": width,

            "height": height
        },

        "ocr_result": ocr_result,

        "status": "success"
    }


# =========================================================
# 7. COMPLETE SCAMSCAN ANALYSIS
# =========================================================

@router.post("/full-scan")
async def full_scan(
    file: UploadFile = File(...)
):

    """
    Complete ScamScan forensic pipeline.
    """

    # -----------------------------------------------------
    # STEP 1: Validate file
    # -----------------------------------------------------

    validate_file_type(file)

    # -----------------------------------------------------
    # STEP 2: Read file
    # -----------------------------------------------------

    file_bytes = await file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    # -----------------------------------------------------
    # STEP 3: Validate image
    # -----------------------------------------------------

    width, height = validate_image_bytes(
        file_bytes
    )

    # -----------------------------------------------------
    # STEP 4: Generate scan ID
    # -----------------------------------------------------

    scan_id = generate_scan_id()

    created_at = datetime.now().isoformat()

    # -----------------------------------------------------
    # STEP 5: ELA
    # -----------------------------------------------------

    ela_bytes = perform_ela(
        file_bytes
    )

    ela_score = calculate_ela_score(
        ela_bytes
    )

    ela_filename = save_evidence_image(
        ela_bytes,
        "ela"
    )

    # -----------------------------------------------------
    # STEP 6: Edge Analysis
    # -----------------------------------------------------

    edge_result = perform_edge_analysis(
        file_bytes
    )

    edge_bytes = edge_result["image"]

    edge_filename = save_evidence_image(
        edge_bytes,
        "edges"
    )

    edge_score = min(
        100,
        edge_result["edge_density"] * 4
    )

    # -----------------------------------------------------
    # STEP 7: Heatmap
    # -----------------------------------------------------

    heatmap_result = perform_heatmap_analysis(
        file_bytes
    )

    heatmap_bytes = heatmap_result["image"]

    heatmap_filename = save_evidence_image(
        heatmap_bytes,
        "heatmap"
    )

    heatmap_score = min(
        100,
        heatmap_result["high_activity_ratio"]
    )

    # -----------------------------------------------------
    # STEP 8: OCR
    # -----------------------------------------------------

    ocr_result = extract_text_from_image(
        file_bytes
    )

    ocr_text_length = ocr_result.get(
        "text_length",
        ocr_result.get(
            "character_count",
            len(
                ocr_result.get(
                    "text",
                    ""
                )
            )
        )
    )

    # -----------------------------------------------------
    # STEP 9: Risk calculation
    # -----------------------------------------------------

    risk_result = calculate_risk(

        ela_score=ela_score,

        edge_score=edge_score,

        heatmap_score=heatmap_score,

        ocr_text_length=ocr_text_length
    )

    # -----------------------------------------------------
    # Add detailed measurements
    # -----------------------------------------------------

    risk_result["ela_analysis"] = {

        "ela_score": round(
            ela_score,
            2
        )
    }

    risk_result["edge_analysis"] = {

        "edge_pixel_count": (
            edge_result["edge_pixel_count"]
        ),

        "edge_density": (
            edge_result["edge_density"]
        ),

        "edge_score": round(
            edge_score,
            2
        )
    }

    risk_result["heatmap_analysis"] = {

        "mean_intensity": (
            heatmap_result["mean_intensity"]
        ),

        "maximum_intensity": (
            heatmap_result["maximum_intensity"]
        ),

        "high_activity_ratio": (
            heatmap_result["high_activity_ratio"]
        ),

        "heatmap_score": round(
            heatmap_score,
            2
        )
    }

    # -----------------------------------------------------
    # STEP 10: AI Generation Analysis
    # -----------------------------------------------------
    # This is a preliminary forensic heuristic.
    # It is NOT a trained AI classifier.

    ai_analysis = analyze_ai_generation(
        file_bytes
    )

    # -----------------------------------------------------
    # STEP 11: Generate findings
    # -----------------------------------------------------

    findings_result = generate_findings(

        ela_score=ela_score,

        edge_score=edge_score,

        heatmap_score=heatmap_score,

        ocr_text_length=ocr_text_length
    )

    # Add AI-generation information.

    findings_result.append(
        (
            "AI-generation analysis indicates "
            f"{ai_analysis['likelihood']} likelihood "
            "based on preliminary forensic heuristics."
        )
    )

    # -----------------------------------------------------
    # STEP 12: Create scan record
    # -----------------------------------------------------

    scan_record = {

        "scan_id": scan_id,

        "created_at": created_at,

        "file": {

            "filename": file.filename,

            "content_type": file.content_type,

            "size": len(file_bytes),

            "width": width,

            "height": height
        },

        "forensic_analysis": risk_result,

        "ocr_analysis": ocr_result,

        "ai_analysis": ai_analysis,

        "findings": findings_result,

        "visual_evidence": {

            "ela": {

                "filename": ela_filename,

                "url": create_output_url(
                    ela_filename
                )
            },

            "edges": {

                "filename": edge_filename,

                "url": create_output_url(
                    edge_filename
                )
            },

            "heatmap": {

                "filename": heatmap_filename,

                "url": create_output_url(
                    heatmap_filename
                )
            }
        },

        "next_step": (
            "Review suspicious regions and verify "
            "important information using an official "
            "bank, payment-provider, or trusted source."
        ),

        "disclaimer": (
            "This is a preliminary forensic analysis. "
            "ELA, edge analysis, heatmaps, OCR and "
            "AI-generation indicators provide "
            "investigative evidence only. They do not "
            "prove that an image is genuine, forged, "
            "or AI-generated."
        )
    }

    # -----------------------------------------------------
    # STEP 13: Save to Supabase
    # -----------------------------------------------------

    try:

        save_scan_record(
            scan_record
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={

                "message": (
                    "Forensic analysis completed, "
                    "but saving the scan to Supabase failed."
                ),

                "error": str(error)
            }
        )

    # -----------------------------------------------------
    # STEP 14: Return result
    # -----------------------------------------------------

    return {

        "message": (
            "Complete ScamScan analysis finished"
        ),

        "status": "success",

        **scan_record
    }


# =========================================================
# 8. Scan History
# =========================================================

@router.get("/history")
def scan_history():

    try:

        records = get_all_scan_records()

        return {

            "message": (
                "Scan history retrieved successfully"
            ),

            "count": len(records),

            "records": records,

            "status": "success"
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={

                "message": (
                    "Unable to retrieve scan history"
                ),

                "error": str(error)
            }
        )


# =========================================================
# 9. Single Scan History
# =========================================================

@router.get("/history/{scan_id}")
def single_scan_history(
    scan_id: str
):

    try:

        record = get_scan_by_id(
            scan_id
        )

        if record is None:

            raise HTTPException(
                status_code=404,
                detail="Scan record not found."
            )

        return {

            "message": (
                "Scan record retrieved successfully"
            ),

            "record": record,

            "status": "success"
        }

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={

                "message": (
                    "Unable to retrieve scan record"
                ),

                "error": str(error)
            }
        )