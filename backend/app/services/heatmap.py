import cv2
import numpy as np


def perform_heatmap_analysis(image_bytes: bytes):
    # image_bytes contains the original uploaded image.
    # We convert these bytes into an image that OpenCV can process.

    try:
        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        # NumPy converts the raw image bytes into an array.
        # uint8 is the standard data type for image pixel values.

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        # imdecode converts the NumPy array into an OpenCV image.
        # IMREAD_COLOR loads the image with its color information.

        if image is None:
            raise ValueError(
                "Unable to read the uploaded image"
            )

        # If OpenCV cannot read the image, we stop processing
        # instead of continuing with an invalid image.

        gray_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # Heatmap analysis works mainly with intensity differences.
        # Therefore, we first convert the image to grayscale.

        blurred_image = cv2.GaussianBlur(
            gray_image,
            (7, 7),
            0
        )

        # Gaussian blur reduces very small random variations.
        # This makes the heatmap more stable and easier to interpret.

        difference = cv2.absdiff(
            gray_image,
            blurred_image
        )

        # absdiff calculates the difference between the original
        # grayscale image and its blurred version.
        # Strong differences indicate regions with more local detail.

        normalized = cv2.normalize(
            difference,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        # We normalize the difference values between 0 and 255.
        # This makes the values suitable for creating a heatmap.

        heatmap = cv2.applyColorMap(
            normalized,
            cv2.COLORMAP_JET
        )

        # applyColorMap converts the intensity information into
        # a color visualization that is easier for humans to inspect.

        success, encoded_image = cv2.imencode(
            ".jpg",
            heatmap
        )

        # The generated heatmap is encoded as JPEG.
        # This allows FastAPI to send it to the frontend.

        if not success:
            raise ValueError(
                "Unable to encode heatmap image"
            )

        # Calculate the average intensity of the heatmap.
        # This provides a simple numerical measurement of image activity.

        mean_intensity = float(
            np.mean(normalized)
        )

        # Find the strongest intensity detected in the image.

        maximum_intensity = int(
            np.max(normalized)
        )

        # Count pixels that have relatively high intensity.
        # These pixels represent areas with stronger local differences.

        high_activity_pixels = int(
            np.sum(normalized > 180)
        )

        # Calculate how much of the image contains high-activity pixels.

        total_pixels = normalized.shape[0] * normalized.shape[1]

        high_activity_ratio = (
            high_activity_pixels / total_pixels
        ) * 100

        # The ratio tells us what percentage of the image
        # contains stronger local differences.

        return {
            "image": encoded_image.tobytes(),
            "mean_intensity": round(mean_intensity, 2),
            "maximum_intensity": maximum_intensity,
            "high_activity_ratio": round(
                high_activity_ratio,
                2
            ),
            "width": image.shape[1],
            "height": image.shape[0]
        }

        # We return the heatmap image together with numerical
        # evidence that can later be used by our risk engine.

    except Exception as error:
        # Any unexpected processing error is converted into
        # a clear error message for the API.

        raise ValueError(
            f"Heatmap analysis failed: {str(error)}"
        )