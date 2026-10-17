from PIL import Image, ImageChops, ImageEnhance
from io import BytesIO


def perform_ela(image_bytes: bytes, quality: int = 90):
    # image_bytes contains the original uploaded image.
    # quality decides how strongly we recompress the image.

    try:
        original_image = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

        # We open the image directly from memory.
        # RGB gives us a standard format for pixel comparison.

        compressed_buffer = BytesIO()

        # This temporary memory object will contain
        # our recompressed JPEG image.

        original_image.save(
            compressed_buffer,
            format="JPEG",
            quality=quality
        )

        # We save another JPEG copy of the image.
        # JPEG compression can create small pixel differences.

        compressed_buffer.seek(0)

        # Move the memory pointer back to the beginning
        # so that PIL can read the compressed image.

        compressed_image = Image.open(
            compressed_buffer
        ).convert("RGB")

        # Now we have two images:
        # 1. Original image
        # 2. Recompressed image

        difference_image = ImageChops.difference(
            original_image,
            compressed_image
        )

        # ImageChops compares both images pixel by pixel.
        # Different pixels become brighter in the difference image.

        enhanced_image = ImageEnhance.Brightness(
            difference_image
        ).enhance(10)

        # Small differences can be difficult to see.
        # We increase their brightness to make suspicious regions
        # easier for humans to inspect.

        result_buffer = BytesIO()

        # We create another memory object for the final ELA image.

        enhanced_image.save(
            result_buffer,
            format="JPEG"
        )

        # The ELA result is saved as a JPEG image in memory.
        # We don't need to permanently save it here.

        result_buffer.seek(0)

        # Move the pointer to the beginning of the result.

        return result_buffer.getvalue()

        # Return the final ELA image as raw bytes.
        # The API can send these bytes directly to the frontend.

    except Exception as error:
        # If anything goes wrong during ELA processing,
        # return a clear error instead of crashing silently.

        raise ValueError(
            f"ELA analysis failed: {str(error)}"
        )