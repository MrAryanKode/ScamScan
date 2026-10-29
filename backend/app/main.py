
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routes.auth import router as auth_router
from app.routes.scan import router as scan_router


# ---------------------------------------------------------
# Create FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="ScamScan API",
    description="Digital document forensic analysis API",
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS configuration
# Allow local development and the live Vercel frontend.
# The origin must match the browser's website origin exactly.
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://scam-scan-one.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Output directory for forensic evidence images
# ---------------------------------------------------------

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Serve generated evidence images
# ---------------------------------------------------------

app.mount(
    "/outputs",
    StaticFiles(directory=str(OUTPUT_DIR)),
    name="outputs"
)


# ---------------------------------------------------------
# Register API routes
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
