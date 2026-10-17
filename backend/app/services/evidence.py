from pathlib import Path
from uuid import uuid4


# This directory stores generated forensic evidence images.
# It is created inside the backend app folder.

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent / "outputs"
)


# Create the outputs directory automatically if it does not exist.
# parents=True creates missing folders when necessary.
# exist_ok=True prevents an error if the folder already exists.

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def save_evidence_image(
    image_bytes: bytes,
    prefix: str
) -> str:

    # image_bytes contains the generated ELA, edge,
    # or heatmap image in binary format.

    if not image_bytes:
        raise ValueError(
            "Cannot save empty evidence image"
        )

    # We don't want to create an empty JPG file.
    # This check catches processing problems early.

    unique_id = uuid4().hex

    # UUID generates a unique identifier.
    # This prevents images from different scans
    # from accidentally replacing each other.

    filename = f"{prefix}_{unique_id}.jpg"

    # The prefix tells us what type of evidence this is.
    # Example:
    # ela_abc123.jpg
    # edges_abc123.jpg
    # heatmap_abc123.jpg

    file_path = OUTPUT_DIR / filename

    # Combine the output folder with the generated filename.

    file_path.write_bytes(
        image_bytes
    )

    # Write the generated image bytes to the JPG file.

    if not file_path.exists():
        raise IOError(
            "Evidence image could not be saved"
        )

    # Make sure the file was actually created successfully.

    return filename

    # Return only the filename.
    # scan.py uses this filename to create the frontend URL.