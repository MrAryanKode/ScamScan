# =========================================================
# ScamScan OCR Service
# =========================================================
# This service extracts readable text from document images
# using Tesseract OCR.
#
# The pipeline uses multiple preprocessing techniques
# because documents such as cheques contain:
#
# - printed text
# - boxes
# - lines
# - signatures
# - security patterns
# - stamps
# - small numbers
#
# These elements can confuse OCR.
# =========================================================


# ---------------------------------------------------------
# Standard Python imports
# ---------------------------------------------------------

import re

from io import BytesIO


# ---------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------

import cv2

import numpy as np

import pytesseract

from PIL import Image


# =========================================================
# Tesseract configuration
# =========================================================
# On Windows, Tesseract may not be available directly
# through PATH.
#
# We try common installation locations first.
# =========================================================


COMMON_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


# ---------------------------------------------------------
# Find a working Tesseract executable
# ---------------------------------------------------------

def configure_tesseract():
    """
    Configure pytesseract using a common Windows path.

    If Tesseract is already available through PATH,
    pytesseract will continue using that installation.
    """

    for path in COMMON_TESSERACT_PATHS:

        try:

            # Check whether this executable can actually
            # answer a Tesseract version request.

            version = pytesseract.get_tesseract_version()

            if version:

                return str(version)

        except Exception:

            # If the current PATH configuration fails,
            # continue checking explicit Windows paths.

            pass

        try:

            # Configure pytesseract to use this executable.

            pytesseract.pytesseract.tesseract_cmd = path

            # Verify that the executable works.

            version = (
                pytesseract
                .get_tesseract_version()
            )

            if version:

                return str(version)

        except Exception:

            # Try the next possible installation path.

            continue

    # Final attempt using whatever configuration is
    # already available in the environment.

    try:

        version = pytesseract.get_tesseract_version()

        return str(version)

    except Exception:

        return "Unknown"


# Configure Tesseract when this module loads.

TESSERACT_VERSION = configure_tesseract()


# =========================================================
# Image preparation
# =========================================================

def load_image_from_bytes(
    image_bytes: bytes
):
    """
    Convert uploaded image bytes into an OpenCV image.
    """

    # Convert raw bytes into a NumPy array.

    array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    # Decode the bytes into an OpenCV image.

    image = cv2.imdecode(
        array,
        cv2.IMREAD_COLOR
    )

    if image is None:

        raise ValueError(
            "Unable to decode image for OCR."
        )

    return image


# =========================================================
# OCR preprocessing
# =========================================================

def create_preprocessed_images(
    image
):
    """
    Create several versions of the document.

    Different preprocessing methods work better for
    different document regions.
    """

    processed_images = []

    # -----------------------------------------------------
    # Version 1: Original grayscale
    # -----------------------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    processed_images.append(
        (
            "grayscale",
            gray
        )
    )

    # -----------------------------------------------------
    # Version 2: Upscaled grayscale
    # -----------------------------------------------------
    # Upscaling helps Tesseract recognize small characters.
    # -----------------------------------------------------

    enlarged = cv2.resize(
        gray,
        None,
        fx=2.0,
        fy=2.0,
        interpolation=cv2.INTER_CUBIC
    )

    processed_images.append(
        (
            "upscaled",
            enlarged
        )
    )

    # -----------------------------------------------------
    # Version 3: Contrast enhancement
    # -----------------------------------------------------
    # CLAHE improves local contrast without aggressively
    # destroying document details.
    # -----------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(
        enlarged
    )

    processed_images.append(
        (
            "contrast_enhanced",
            enhanced
        )
    )

    # -----------------------------------------------------
    # Version 4: Otsu threshold
    # -----------------------------------------------------
    # Useful for clean black text on light documents.
    # -----------------------------------------------------

    _, otsu = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY
        + cv2.THRESH_OTSU
    )

    processed_images.append(
        (
            "otsu",
            otsu
        )
    )

    # -----------------------------------------------------
    # Version 5: Adaptive threshold
    # -----------------------------------------------------
    # Useful when different areas of the document have
    # different brightness levels.
    # -----------------------------------------------------

    adaptive = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    processed_images.append(
        (
            "adaptive",
            adaptive
        )
    )

    # -----------------------------------------------------
    # Version 6: Light denoising
    # -----------------------------------------------------
    # Remove small image noise while preserving edges.
    # -----------------------------------------------------

    denoised = cv2.fastNlMeansDenoising(
        enhanced,
        None,
        10,
        7,
        21
    )

    processed_images.append(
        (
            "denoised",
            denoised
        )
    )

    return processed_images


# =========================================================
# OCR line cleaning
# =========================================================

def clean_line(
    text: str
) -> str:
    """
    Clean one OCR line.

    Important:
    We DO NOT replace '/' with a space.

    A slash can be legitimate document information,
    for example:

        RTGS / NEFT

    We only remove obvious OCR garbage.
    """

    if text is None:

        return ""

    # Remove leading and trailing whitespace.

    text = text.strip()

    if not text:

        return ""

    # Normalize tabs and repeated spaces.

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Count useful alphanumeric characters.

    alphanumeric_count = sum(
        character.isalnum()
        for character in text
    )

    # Count total characters.

    total_count = len(text)

    # Very short fragments are often OCR noise.

    if total_count <= 2:

        return ""

    # Calculate how much of the line contains useful
    # letters or numbers.

    meaningful_ratio = (
        alphanumeric_count
        / max(total_count, 1)
    )

    # Lines consisting almost entirely of symbols are
    # usually cheque security patterns or border noise.

    if meaningful_ratio < 0.25:

        return ""

    # Remove punctuation temporarily so we can check
    # whether the remaining content is meaningful.

    compact = re.sub(
        r"[^A-Za-z0-9]+",
        "",
        text
    )

    if not compact:

        return ""

    # If the complete line consists of the same
    # repeated character, treat it as noise.

    if len(set(compact.lower())) == 1:

        return ""

    # Remove extremely long runs of one character.

    text = re.sub(
        r"(.)\1{5,}",
        r"\1\1",
        text
    )

    return text


# =========================================================
# OCR result cleaning
# =========================================================

def clean_ocr_text(
    raw_text: str
) -> str:
    """
    Convert raw Tesseract output into readable text.

    Real newline characters are preserved.
    """

    if not raw_text:

        return ""

    # Normalize Windows line endings.

    raw_text = raw_text.replace(
        "\r\n",
        "\n"
    )

    raw_text = raw_text.replace(
        "\r",
        "\n"
    )

    # If an OCR engine somehow returns the literal
    # characters "\\n", convert them into real newlines.
    #
    # This is NOT normally produced by Tesseract,
    # but it prevents escaped newline strings from
    # appearing in our frontend.

    raw_text = raw_text.replace(
        "\\n",
        "\n"
    )

    lines = raw_text.split(
        "\n"
    )

    cleaned_lines = []

    for line in lines:

        cleaned = clean_line(
            line
        )

        if cleaned:

            cleaned_lines.append(
                cleaned
            )

    # Join using REAL newline characters.

    return "\n".join(
        cleaned_lines
    )


# =========================================================
# OCR confidence calculation
# =========================================================

def calculate_ocr_confidence(
    image,
    config: str
):
    """
    Run Tesseract data extraction and calculate
    an approximate confidence score.
    """

    try:

        data = pytesseract.image_to_data(
            image,
            config=config,
            lang="eng",
            output_type=(
                pytesseract.Output.DICT
            )
        )

    except Exception:

        return "", 0.0, 0

    words = []

    confidences = []

    number_of_words = len(
        data.get(
            "text",
            []
        )
    )

    for index in range(
        number_of_words
    ):

        word = (
            data["text"][index]
            .strip()
        )

        confidence_text = (
            data["conf"][index]
        )

        if not word:

            continue

        try:

            confidence = float(
                confidence_text
            )

        except (
            ValueError,
            TypeError
        ):

            confidence = -1

        words.append(
            word
        )

        if confidence >= 0:

            confidences.append(
                confidence
            )

    # Tesseract gives confidence per word.
    # Average them to obtain a rough quality indicator.

    if confidences:

        average_confidence = (
            sum(confidences)
            / len(confidences)
        )

    else:

        average_confidence = 0.0

    raw_text = " ".join(
        words
    )

    return (
        raw_text,
        average_confidence,
        len(words)
    )


# =========================================================
# OCR with line preservation
# =========================================================

def run_tesseract(
    image,
    config: str
):
    """
    Run Tesseract while preserving its natural line breaks.
    """

    try:

        raw_text = pytesseract.image_to_string(
            image,
            lang="eng",
            config=config
        )

    except Exception as error:

        return {
            "text": "",
            "confidence": 0.0,
            "word_count": 0,
            "error": str(error)
        }

    # Clean the text while preserving actual newlines.

    cleaned_text = clean_ocr_text(
        raw_text
    )

    # Obtain confidence information from the same image.

    _, confidence, word_count = (
        calculate_ocr_confidence(
            image,
            config
        )
    )

    return {
        "text": cleaned_text,
        "confidence": round(
            confidence,
            2
        ),
        "word_count": word_count,
        "error": None
    }


# =========================================================
# Select the best OCR result
# =========================================================

def select_best_result(
    results: list
):
    """
    Select the most useful OCR result.

    We consider:
    - confidence
    - amount of readable text
    - number of words
    """

    valid_results = []

    for result in results:

        text = result.get(
            "text",
            ""
        )

        if not text:

            continue

        confidence = result.get(
            "confidence",
            0
        )

        word_count = result.get(
            "word_count",
            0
        )

        character_count = len(
            text
        )

        # A simple quality score.
        #
        # Confidence is the strongest signal.
        # Text length and word count provide supporting
        # information so an empty/high-confidence result
        # does not automatically win.

        quality_score = (
            confidence * 0.70
            + min(
                character_count / 5,
                100
            ) * 0.20
            + min(
                word_count * 2,
                50
            ) * 0.10
        )

        result["quality_score"] = round(
            quality_score,
            2
        )

        valid_results.append(
            result
        )

    if not valid_results:

        return {
            "text": "",
            "confidence": 0.0,
            "word_count": 0,
            "quality_score": 0.0,
            "method": "none"
        }

    # Select the result with the highest calculated score.

    return max(
        valid_results,
        key=lambda item: item[
            "quality_score"
        ]
    )


# =========================================================
# Main OCR function
# =========================================================

def extract_text_from_image(
    image_bytes: bytes
) -> dict:
    """
    Main OCR entry point used by ScamScan.

    The function:
        1. Loads the image.
        2. Creates several preprocessing versions.
        3. Runs multiple Tesseract configurations.
        4. Selects the strongest result.
        5. Returns clean readable text.
    """

    try:

        # -------------------------------------------------
        # Load uploaded image.
        # -------------------------------------------------

        image = load_image_from_bytes(
            image_bytes
        )

        # -------------------------------------------------
        # Create multiple preprocessing variants.
        # -------------------------------------------------

        processed_images = (
            create_preprocessed_images(
                image
            )
        )

        # Store all OCR attempts.

        results = []

        # -------------------------------------------------
        # OCR configurations.
        # -------------------------------------------------
        #
        # PSM 6:
        # Assumes a relatively uniform block of text.
        #
        # PSM 11:
        # Sparse text. Useful for documents where text
        # is distributed across different regions.
        #
        # PSM 3:
        # Automatic page segmentation.
        # -------------------------------------------------

        configurations = [
            "--oem 3 --psm 6",
            "--oem 3 --psm 11",
            "--oem 3 --psm 3",
        ]

        # -------------------------------------------------
        # Run OCR on every preprocessing version.
        # -------------------------------------------------

        for method_name, processed_image in (
            processed_images
        ):

            for config in configurations:

                result = run_tesseract(
                    processed_image,
                    config
                )

                # Ignore failed OCR attempts.

                if not result.get(
                    "error"
                ):

                    result["method"] = (
                        f"{method_name} | {config}"
                    )

                    results.append(
                        result
                    )

        # -------------------------------------------------
        # Choose the strongest result.
        # -------------------------------------------------

        best_result = select_best_result(
            results
        )

        # -------------------------------------------------
        # Final text cleanup.
        # -------------------------------------------------

        final_text = clean_ocr_text(
            best_result.get(
                "text",
                ""
            )
        )

        # -------------------------------------------------
        # Count characters and words.
        # -------------------------------------------------

        character_count = len(
            final_text
        )

        word_count = len(
            final_text.split()
        )

        # -------------------------------------------------
        # Return structured OCR result.
        # -------------------------------------------------

        return {
            "success": True,

            "text": final_text,

            "character_count": (
                character_count
            ),

            "word_count": word_count,

            "confidence": (
                best_result.get(
                    "confidence",
                    0.0
                )
            ),

            "ocr_quality_score": (
                best_result.get(
                    "quality_score",
                    0.0
                )
            ),

            "method": (
                best_result.get(
                    "method",
                    "unknown"
                )
            ),

            "engine": "Tesseract OCR",

            "engine_version": (
                TESSERACT_VERSION
            ),

            "note": (
                "OCR output is an automated "
                "text-extraction result and "
                "may contain recognition errors."
            )
        }

    except Exception as error:

        # -------------------------------------------------
        # Return a controlled error instead of crashing
        # the complete forensic scan.
        # -------------------------------------------------

        return {
            "success": False,

            "text": "",

            "character_count": 0,

            "word_count": 0,

            "confidence": 0.0,

            "ocr_quality_score": 0.0,

            "method": "failed",

            "engine": "Tesseract OCR",

            "engine_version": (
                TESSERACT_VERSION
            ),

            "error": str(error)
        }