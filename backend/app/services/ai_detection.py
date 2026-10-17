"""
ScamScan AI Image Detection.

Combines existing forensic heuristics with an external
pretrained-model service. Outputs are investigative signals,
not proof that an image is genuine or AI-generated.
"""

from io import BytesIO
import os

import cv2
import numpy as np
import requests
from PIL import Image

AI_SERVICE_URL = os.getenv(
    "SCAMSCAN_AI_SERVICE_URL",
    "http://localhost:8001",
)
AI_REQUEST_TIMEOUT = 60


def resolution_indicator(width: int, height: int) -> float:
    common_sizes = {
        (512, 512), (768, 768), (1024, 1024),
        (1024, 1536), (1536, 1024), (2048, 2048),
    }
    return 15.0 if (width, height) in common_sizes else 0.0


def compression_indicator(image: np.ndarray) -> float:
    success, encoded = cv2.imencode(
        ".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90]
    )
    if not success:
        return 0.0

    decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if decoded is None:
        return 0.0

    difference = cv2.absdiff(image, decoded)
    mean_difference = float(np.mean(difference))

    if mean_difference > 12:
        return 25.0
    if mean_difference > 8:
        return 15.0
    if mean_difference > 5:
        return 8.0
    return 0.0


def noise_indicator(gray: np.ndarray) -> float:
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    noise = cv2.absdiff(gray, blurred)
    mean_noise = float(np.mean(noise))

    if mean_noise < 2:
        return 20.0
    if mean_noise < 4:
        return 10.0
    return 0.0


def texture_indicator(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 100, 200)
    edge_density = (
        np.count_nonzero(edges) / edges.size
    ) * 100

    if edge_density < 2:
        return 15.0
    if edge_density > 35:
        return 10.0
    return 0.0


def analyze_pretrained_model(image_bytes: bytes) -> dict:
    """Request inference output and score from the Ubuntu model API."""
    try:
        response = requests.post(
            f"{AI_SERVICE_URL.rstrip('/')}/predict",
            files={
                "file": ("image.png", image_bytes, "image/png")
            },
            timeout=AI_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()

        available = result.get("status") == "success"

        # Keep the model-derived score separate from heuristic scoring.
        return {
            "available": available,
            "model": result.get("model"),
            "device": result.get("device"),
            "processor": result.get("processor"),
            "raw_output": result.get("raw_output"),
            "output_shape": result.get("output_shape"),
            "image_size": result.get("image_size"),
            "fake_image_score": result.get("fake_image_score"),
            "score_type": result.get("score_type"),
            "interpretation": result.get(
                "interpretation",
                "Model-derived score only; not a calibrated probability "
                "or proof that the image is fake or genuine.",
            ),
        }
    except requests.RequestException as exc:
        return {
            "available": False,
            "error": str(exc),
            "interpretation": (
                "Pretrained AI service unavailable; forensic "
                "heuristics can still run."
            ),
        }


def analyze_ai_generation(image_bytes: bytes) -> dict:
    """Combine heuristic indicators with separate model output."""
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    width, height = image.size

    rgb = np.array(image)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    signals = {
        "resolution_indicator": round(
            resolution_indicator(width, height), 2
        ),
        "compression_indicator": round(
            compression_indicator(bgr), 2
        ),
        "noise_indicator": round(noise_indicator(gray), 2),
        "texture_indicator": round(texture_indicator(gray), 2),
    }

    # Preserve the existing heuristic score independently.
    heuristic_score = round(
        min(100.0, sum(signals.values())), 2
    )

    if heuristic_score >= 70:
        likelihood = "High"
    elif heuristic_score >= 40:
        likelihood = "Moderate"
    elif heuristic_score >= 20:
        likelihood = "Low"
    else:
        likelihood = "Very Low"

    # Keep pretrained model output separate from heuristic scoring.
    pretrained = analyze_pretrained_model(image_bytes)

    return {
        "ai_likelihood_score": heuristic_score,
        "likelihood": likelihood,
        "signals": signals,
        "model_type": "Forensic heuristics + pretrained model API",
        "model_status": (
            "Connected" if pretrained["available"]
            else "Pretrained service unavailable"
        ),
        "pretrained_model": pretrained,
        "note": (
            "The heuristic score is not a calibrated probability. "
            "The pretrained model score is sigmoid-derived and unverified; "
            "it does not prove that an image was generated by AI."
        ),
    }
