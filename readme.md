# ScamScan 🔍

### Digital Media Forensics and AI-Generated Media Detection

ScamScan is a digital forensics project designed to analyze images for potential signs of manipulation and help users understand suspicious visual patterns. It combines image-processing techniques, OCR, and risk indicators to provide an initial analysis report.

> **Disclaimer:** ScamScan provides preliminary indicators only. It cannot conclusively determine whether an image is genuine, forged, or AI-generated. Results should not be treated as proof of fraud.

## 🚀 Features

- **Error Level Analysis (ELA):** Highlights differences that may appear after image recompression.
- **Edge Analysis:** Examines edges and visual boundaries for unusual patterns.
- **Heatmap Visualization:** Displays areas with higher local image activity.
- **OCR (Optical Character Recognition):** Extracts text from supported images.
- **Risk Assessment:** Combines selected indicators into an illustrative risk score.
- **Findings and Evidence:** Generates readable findings and supporting analysis images.
- **Scan History:** Stores and retrieves previous scan records using Supabase.
- **Web Interface:** Provides a frontend for interacting with the application.

*AI-generated media detection capabilities depend on the implementation and model currently configured in the project.*

## 🛠️ Technology Stack

### Backend
- Python
- FastAPI
- OpenCV
- Pillow
- Tesseract OCR
- Supabase

### Frontend
- React
- Vite
- JavaScript
- CSS

## 📁 Project Structure

```text
ScamScan/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── docs/
├── .gitignore
└── README.md
```

## ⚙️ Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/MrAryanKode/ScamScan.git
cd ScamScan
```

### 2. Set up the backend

Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
pip install -r backend/requirements.txt
```

Configure the required environment variables in `backend/.env`, including the Supabase URL and service key, according to the backend configuration. Never commit real secrets to GitHub.

Install Tesseract OCR separately if required, and ensure the backend can locate its executable.

### 3. Start the backend

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

### 4. Set up the frontend

Open a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your terminal.

## 🔐 Security and Privacy

- Never upload `.env` files, API keys, service-role keys, passwords, or tokens.
- Do not use real cheque images or documents containing personal or banking information in public demonstrations.
- Use dummy or appropriately redacted images for testing.
- Treat extracted OCR text and scan reports as potentially sensitive data.

## ⚠️ Limitations

- ELA and edge patterns can be affected by ordinary image editing, compression, resizing, and screenshots.
- A heatmap represents image activity; it does not independently prove manipulation.
- Risk scores are heuristic indicators, not calibrated probabilities of fraud.
- OCR may misread text, especially in low-quality images.
- Important financial transactions should be verified through the relevant bank or authorized payment provider.

## 👥 Team

**Project:** ScamScan

**Repository:** [MrAryanKode/ScamScan](https://github.com/MrAryanKode/ScamScan)

This is a collaborative group project. Add all six team members' names and their respective contributions here.

## 📜 License

A license has not yet been specified. Please add an appropriate license before granting others permission to reuse, modify, or distribute this project.
