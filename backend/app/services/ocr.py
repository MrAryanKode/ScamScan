
# ============================================================
# ScamScan OCR Service
# Extracts readable text from uploaded document images.
# ============================================================

import re
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image


# ------------------------------------------------------------
# Tesseract configuration
# ------------------------------------------------------------
# We explicitly configure the Windows installation path.
# This fixes TesseractNotFoundError when Tesseract is installed
# but is not available through the system PATH.
# ------------------------------------------------------------

TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if TESSERACT_PATH.is_file():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)


# ------------------------------------------------------------
# Check the OCR engine
# ------------------------------------------------------------

def get_tesseract_version():
    """Return the installed Tesseract version if available."""
    try:
        return str(pytesseract.get_tesseract_version())
    except Exception:
        return "Unavailable"


TESSERACT_VERSION = get_tesseract_version()


# ------------------------------------------------------------
# Image loading
# ------------------------------------------------------------

def load_image_from_bytes(image_bytes: bytes):
    """Decode uploaded image bytes into an OpenCV image."""

    if not image_bytes:
        raise ValueError("The uploaded image is empty.")

    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Unable to decode the uploaded image.")

    return image


# ------------------------------------------------------------
# Image preprocessing
# ------------------------------------------------------------

def create_preprocessed_images(image):
    """Create image variants to improve text recognition."""

    # Convert the original image to grayscale.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Upscale the image to make small text easier to recognize.
    enlarged = cv2.resize(
        gray,
        None,
        fx=2.0,
        fy=2.0,
        interpolation=cv2.INTER_CUBIC
    )

    # Improve local contrast.
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )
    enhanced = clahe.apply(enlarged)

    # Create a black-and-white version.
    _, thresholded = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return [
        ("grayscale", gray),
        ("upscaled", enlarged),
        ("contrast_enhanced", enhanced),
        ("thresholded", thresholded),
    ]


# ------------------------------------------------------------
# Text cleanup
# ------------------------------------------------------------

def clean_ocr_text(text: str) -> str:
    """Remove blank lines and unnecessary whitespace."""

    if not text:
        return ""

    cleaned_lines = []

    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()

        # Ignore lines containing no letters or digits.
        if not any(character.isalnum() for character in line):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# ------------------------------------------------------------
# OCR execution
# ------------------------------------------------------------

def run_ocr(image, config: str):
    """Run Tesseract and return text plus confidence."""

    data = pytesseract.image_to_data(
        image,
        lang="eng",
        config=config,
        output_type=pytesseract.Output.DICT
    )

    words = []
    confidences = []

    for word, confidence_value in zip(
        data.get("text", []),
        data.get("conf", [])
    ):
        word = word.strip()

        if not word:
            continue

        try:
            confidence = float(confidence_value)
        except (ValueError, TypeError):
            confidence = -1

        words.append(word)

        if confidence >= 0:
            confidences.append(confidence)

    average_confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else 0.0
    )

    # Preserve natural line breaks using image_to_string.
    text = pytesseract.image_to_string(
        image,
        lang="eng",
        config=config
    )

    return {
        "text": clean_ocr_text(text),
        "confidence": round(average_confidence, 2),
        "word_count": len(words),
    }


# ------------------------------------------------------------
# Select the most useful OCR result
# ------------------------------------------------------------

def select_best_result(results: list):
    """Prefer results with readable text and higher confidence."""

    if not results:
        return {
            "text": "",
            "confidence": 0.0,
            "word_count": 0,
            "method": "none",
        }

    def calculate_quality(result):
        text_length = len(result["text"])
        confidence = result["confidence"]
        word_count = result["word_count"]

        # This is a heuristic quality score, not a probability.
        return (
            confidence * 0.70
            + min(text_length / 5, 100) * 0.20
            + min(word_count * 2, 50) * 0.10
        )

    return max(results, key=calculate_quality)


# ------------------------------------------------------------
# Main OCR function
# ------------------------------------------------------------

def extract_text_from_image(image_bytes: bytes) -> dict:
    """
    Extract text from an uploaded image.

    Returns structured results for ScamScan, including text,
    confidence, word count, OCR engine and error information.
    """

    try:
        # Check that Tesseract can actually run.
        if TESSERACT_VERSION == "Unavailable":
            raise RuntimeError(
                "Tesseract is unavailable. Check TESSERACT_PATH "
                "and ensure English language data is installed."
            )

        # Load the uploaded image.
        image = load_image_from_bytes(image_bytes)

        # Generate several image variants.
        processed_images = create_preprocessed_images(image)

        results = []

        # Try different page segmentation configurations.
        configurations = [
            "--oem 3 --psm 6",
            "--oem 3 --psm 11",
            "--oem 3 --psm 3",
        ]

        # Run OCR on each image variant.
        for method_name, processed_image in processed_images:
            for config in configurations:
                try:
                    result = run_ocr(processed_image, config)

                    if result["text"]:
                        result["method"] = (
                            f"{method_name} | {config}"
                        )
                        results.append(result)

                except Exception:
                    # One failed attempt should not stop other attempts.
                    continue

        # Select the strongest available result.
        best_result = select_best_result(results)
        final_text = clean_ocr_text(best_result["text"])

        # Prepare the result fields.
        character_count = len(final_text)
        word_count = len(final_text.split())

        return {
            "success": True,
            "text": final_text,
            "text_length": character_count,
            "character_count": character_count,
            "word_count": word_count,
            "confidence": best_result["confidence"],
            "ocr_quality_score": best_result["confidence"],
            "method": best_result["method"],
            "ocr_engine": "Tesseract OCR",
            "engine": "Tesseract OCR",
            "engine_version": TESSERACT_VERSION,
            "note": (
                "OCR is automated text extraction. "
                "Recognition errors may occur."
            ),
        }

    except Exception as error:
        # Return a controlled error instead of crashing OCR itself.
        return {
            "success": False,
            "text": "",
            "text_length": 0,
            "character_count": 0,
            "word_count": 0,
            "confidence": 0.0,
            "ocr_quality_score": 0.0,
            "method": "failed",
            "ocr_engine": "Tesseract OCR",
            "engine": "Tesseract OCR",
            "engine_version": TESSERACT_VERSION,
            "error": str(error),
        }
