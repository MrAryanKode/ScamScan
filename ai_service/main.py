
"""
ScamScan pretrained AI image detection service.

This service runs independently from the main backend.
The model score is an investigative signal, not proof.
"""

from contextlib import asynccontextmanager
from io import BytesIO

import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from transformers import ViTForImageClassification, ViTImageProcessor

# Pretrained model hosted on Hugging Face.
MODEL_ID = "buildborderless/CommunityForensics-DeepfakeDet-ViT"

# Use the NVIDIA GPU when available; otherwise use CPU.
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# These variables are populated when the service starts.
processor = None
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model once when the API starts."""
    global processor, model

    print(f"Loading model: {MODEL_ID}")
    print(f"Selected device: {DEVICE}")

    # Download model files on first run if not already cached.
    processor = ViTImageProcessor.from_pretrained(MODEL_ID)
    model = ViTForImageClassification.from_pretrained(MODEL_ID)

    # Move model weights to the selected device and enable inference mode.
    model.to(DEVICE)
    model.eval()

    print("ScamScan AI model loaded successfully.")

    yield

    # Release references when the service shuts down.
    model = None
    processor = None


app = FastAPI(
    title="ScamScan AI Detection Service",
    description="Pretrained image analysis service for ScamScan.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def health_check():
    """Check whether the prediction service is available."""
    return {
        "service": "ScamScan AI Detection",
        "status": "success",
        "model": MODEL_ID,
        "device": DEVICE,
        "model_loaded": model is not None,
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Run pretrained-model inference on an uploaded image."""

    if model is None or processor is None:
        raise HTTPException(
            status_code=503,
            detail="AI model has not finished loading.",
        )

    # Read the uploaded image and validate its format.
    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        )

    width, height = image.size

    try:
        # Apply the image preprocessing defined by the model.
        inputs = processor(images=image, return_tensors="pt")

        # Move input tensors to the same device as the model.
        inputs = {
            name: tensor.to(DEVICE)
            for name, tensor in inputs.items()
        }

        # Run inference without calculating gradients.
        with torch.inference_mode():
            outputs = model(**inputs)
            logits = outputs.logits

            # This model uses a single logit and sigmoid output.
            fake_probability = torch.sigmoid(logits).reshape(-1)[0].item()

        # Return a score separately from any final authenticity verdict.
        return {
            "status": "success",
            "model": MODEL_ID,
            "device": DEVICE,
            "processor": type(processor).__name__,
            "raw_output": logits.detach().cpu().tolist(),
            "output_shape": list(logits.shape),
            "image_size": {
                "width": width,
                "height": height,
            },
            "fake_image_score": round(fake_probability, 6),
            "score_type": "sigmoid-derived model score",
            "interpretation": (
                "Preliminary model signal only. This score is not a "
                "calibrated probability and does not prove an image "
                "is AI-generated or authentic. Document-specific "
                "performance has not yet been validated."
            ),
        }

    except HTTPException:
        raise
    except Exception as exc:
        # Log details in the server terminal for debugging.
        print(f"Prediction failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Model inference failed. Check the AI service terminal.",
        )
