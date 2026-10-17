def calculate_risk(
    ela_score: float,
    edge_score: float,
    heatmap_score: float,
    ocr_text_length: int
):
    # We receive the results produced by our different
    # forensic analysis modules.

    # Each analysis gives us a different signal.
    # No single signal should decide whether an image is fake.

    ela_weight = 0.35
    edge_weight = 0.30
    heatmap_weight = 0.25
    ocr_weight = 0.10

    # These weights decide how much each signal contributes
    # to the final preliminary risk score.

    ocr_score = 0

    # OCR normally does not prove image manipulation.
    # We only use it as a small supporting signal.

    if ocr_text_length == 0:
        ocr_score = 20

    # If no text is detected, we give a small score.
    # This does NOT mean the image is fake.

    elif ocr_text_length < 20:
        ocr_score = 10

    # Very little detected text gets a smaller supporting score.

    else:
        ocr_score = 0

    # We combine all analysis scores using their weights.

    risk_score = (
        (ela_score * ela_weight)
        + (edge_score * edge_weight)
        + (heatmap_score * heatmap_weight)
        + (ocr_score * ocr_weight)
    )

    # Make sure the final score stays between 0 and 100.

    risk_score = max(
        0,
        min(100, risk_score)
    )

    # Convert the numerical score into an easy-to-understand
    # risk category for the frontend and final report.

    if risk_score < 30:
        risk_level = "Low Risk"

    elif risk_score < 60:
        risk_level = "Medium Risk"

    else:
        risk_level = "High Risk"

    # Return the final score and risk category.
    # These values will later be stored in Supabase.

    return {
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level
    }