from PIL import Image
from io import BytesIO


def load_image(image_bytes: bytes):
    # This function receives the uploaded image as raw bytes.
    # Bytes are the actual binary data of the image file.

    try:
        image = Image.open(BytesIO(image_bytes))

        # We load the image from memory instead of creating
        # a temporary file on the computer.

        image.load()

        # load() forces PIL to completely read the image.
        # This helps us detect corrupted or invalid image files.

        return image

    except Exception as error:
        # If PIL cannot open the image, we raise a clear error.
        # The API can later convert this into a user-friendly message.

        raise ValueError(
            f"Unable to process image: {str(error)}"
        )


def convert_to_rgb(image: Image.Image):
    # Different images can use different color formats such as
    # RGBA, grayscale or palette-based images.

    # RGB gives us a standard three-channel image:
    # Red, Green and Blue.

    return image.convert("RGB")


def convert_to_grayscale(image: Image.Image):
    # Grayscale removes color information from the image.
    # Each pixel then represents brightness from dark to light.

    # This is useful for operations such as edge detection
    # and some OCR preprocessing techniques.

    return image.convert("L")


def get_image_information(image: Image.Image):
    # The size property gives us the width and height
    # of the uploaded image in pixels.

    width, height = image.size

    # We also collect the image format if PIL knows it.
    # Some processed images may not have a format value.

    image_format = image.format

    # Return the basic information in a dictionary.
    # This dictionary can later be included in our scan result.

    return {
        "width": width,
        "height": height,
        "format": image_format
    }


def prepare_image(image_bytes: bytes):
    # This is the main helper function used by other services.
    # It loads the image and prepares a standard RGB version.

    image = load_image(image_bytes)

    # Convert the original image into RGB.
    # We keep the original dimensions and do not resize it.

    rgb_image = convert_to_rgb(image)

    # Collect useful information about the image.
    # This information will be displayed in the final report.

    information = get_image_information(image)

    return rgb_image, information