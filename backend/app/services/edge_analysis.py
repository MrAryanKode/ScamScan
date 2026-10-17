import cv2
import numpy as np


def perform_edge_analysis(image_bytes: bytes):
    # image_bytes contains the original uploaded image.
    # OpenCV needs this data in NumPy format before processing.

    try:
        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        # frombuffer converts the raw image bytes into an array.
        # uint8 is used because image pixels normally use values
        # between 0 and 255.

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        # imdecode converts the byte array into an OpenCV image.
        # IMREAD_COLOR tells OpenCV to read the image in color.

        if image is None:
            raise ValueError(
                "Unable to read the uploaded image"
            )

        # If OpenCV cannot decode the image, we stop processing.
        # This prevents errors later in the analysis.

        gray_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # We convert the image into grayscale.
        # Edge detection mainly needs brightness changes,
        # so color information is not required.

        blurred_image = cv2.GaussianBlur(
            gray_image,
            (5, 5),
            0
        )

        # Gaussian blur reduces small random noise.
        # This prevents tiny unwanted details from becoming edges.

        edges = cv2.Canny(
            blurred_image,
            threshold1=50,
            threshold2=150
        )

        # Canny detects strong changes in brightness.
        # These changes usually occur around text, objects
        # and boundaries in an image.

        edge_pixel_count = int(
            np.count_nonzero(edges)
        )

        # count_nonzero tells us how many pixels were detected
        # as edges in the image.

        total_pixels = edges.shape[0] * edges.shape[1]

        # This calculates the total number of pixels
        # present in the edge image.

        edge_density = (
            edge_pixel_count / total_pixels
        ) * 100

        # Edge density tells us what percentage of the image
        # consists of detected edge pixels.

        success, encoded_image = cv2.imencode(
            ".jpg",
            edges
        )

        # We convert the black-and-white edge image into JPEG
        # so that our FastAPI backend can send it to the frontend.

        if not success:
            raise ValueError(
                "Unable to encode edge image"
            )

        # If JPEG encoding fails, we stop and report the problem.

        return {
            "image": encoded_image.tobytes(),
            "edge_pixel_count": edge_pixel_count,
            "edge_density": round(edge_density, 2),
            "width": image.shape[1],
            "height": image.shape[0]
        }

        # We return both the edge image and useful numerical data.
        # The risk engine will later use these values.

    except Exception as error:
        # Any unexpected processing error is converted into
        # a simple message that our API can handle.

        raise ValueError(
            f"Edge analysis failed: {str(error)}"
        )