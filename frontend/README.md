ScamScan — Digital Media Forensics Platform

ScamScan is a college group project designed to help users investigate potentially manipulated digital images and documents.

Objectives

- Analyze images using Error Level Analysis (ELA).
- Examine image edges using OpenCV.
- Generate heatmap visualizations for further inspection.
- Extract text using Tesseract OCR.
- Calculate a preliminary forensic risk score.
- Store scan history using Supabase.
- Extend the platform with AI-generated media detection and a Chrome extension.

Technology Stack

- Backend: Python, FastAPI
- Image Processing: Pillow, OpenCV, NumPy
- OCR: Tesseract OCR
- Database: Supabase / PostgreSQL
- Frontend: To be integrated
- Browser Integration: Chrome Extension — planned

Current Status

The backend modules are being integrated and tested. AI-generated image/video detection, frontend integration, and the Chrome extension are planned development tasks.

Setup

1. Install Python and Tesseract OCR.
2. Create a Python virtual environment.
3. Install the dependencies from "backend/requirements.txt".
4. Configure the required environment variables in "backend/.env".
5. Start the FastAPI server from the backend directory.

Disclaimer

ScamScan provides preliminary forensic indicators. Its results do not conclusively establish whether an image or document is genuine, forged, or AI-generated. Important information should be independently verified.

Team

This is a collaborative college project developed by a team of six members. See the GitHub repository contributors and project task board for development contributions.