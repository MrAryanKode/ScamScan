from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routes.auth import router as auth_router
from app.routes.scan import router as scan_router


# ---------------------------------------------------------
# Create FastAPI application
# ---------------------------------------------------------
# This is the main entry point of the ScamScan backend.
# The scan router contains /full-scan and other endpoints.
# ---------------------------------------------------------

app = FastAPI(
    title="ScamScan API",
    description="Digital document forensic analysis API",
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------
# Our React frontend may run on either port 5173 or 5174.
# Both localhost and 127.0.0.1 are allowed during development.
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Output directory
# ---------------------------------------------------------
# ELA, edge and heatmap services save generated evidence
# images inside the backend outputs directory.
# ---------------------------------------------------------

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Serve forensic evidence images
# ---------------------------------------------------------
# This allows the React frontend to display files such as:
#
# /outputs/ela_xxxxx.jpg
# /outputs/edges_xxxxx.jpg
# /outputs/heatmap_xxxxx.jpg
# ---------------------------------------------------------

app.mount(
    "/outputs",
    StaticFiles(directory=str(OUTPUT_DIR)),
    name="outputs"
)


# ---------------------------------------------------------
# Register ScamScan routes
# ---------------------------------------------------------
# THIS IS THE IMPORTANT PART.
#
# Without this line FastAPI does not know about:
# /full-scan
# /upload
# /ela
# /edges
# /heatmap
# /ocr
# /history
# etc.
# ---------------------------------------------------------

app.include_router(scan_router)
app.include_router(auth_router)

# ---------------------------------------------------------
# Basic health-check endpoint
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "ScamScan backend is running",
        "status": "success"
    }