from PySide6.QtCore import QRectF
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from pathlib import Path
import typing as t
import numpy as np
import math

import asset_pipeline.core.logging as logging

logger = logging.get_logger(__name__)


def nearest_power_of_2(n: float, threshold: float = 0.05) -> int:
    """
    Rounds n to a power-of-2 value.

    If n is within a relative 'threshold' of the lower power-of-2, return the lower value.
    Otherwise, return the next higher power-of-2.
    """
    if n <= 0:
        return 0
    lower = 2 ** math.floor(math.log2(n))
    higher = 2 ** math.ceil(math.log2(n))
    # If the gap between n and lower is small relative to lower, stick with lower.
    return lower if (n - lower) / lower < threshold else higher


def calculate_render_dimensions(svg_bounds: t.Tuple[float, float],
                                max_resolution: int,
                                margin: float
                               ) -> t.Tuple[t.Tuple[int, int], t.Tuple[float, float, float, float]]:
    """
    Determines the optimal power-of-2 texture size and the largest render rectangle
    within it, preserving the SVG aspect ratio with a consistent margin.

    Parameters:
        svg_bounds (tuple): (svg_width, svg_height) - The original SVG dimensions.
        max_resolution (int): The maximum allowed size for the texture's dominant dimension.
        margin (float): Relative margin (0.0 to 0.5), expressed as a fraction of the dominant texture dimension.

    Returns:
        tuple: (texture_size, render_rect) where:
               - texture_size is (width, height) in power-of-2 dimensions.
               - render_rect is (x_offset, y_offset, render_width, render_height).
    """
    svg_width, svg_height = svg_bounds
    svg_ratio = svg_width / svg_height

    if svg_width >= svg_height:
        # Use the nearest power-of-2 that does not exceed max_resolution for width.
        texture_width = nearest_power_of_2(max_resolution)
        abs_margin = texture_width * margin
        render_width = texture_width - 2 * abs_margin
        render_height = render_width / svg_ratio
        # For the non-dominant height, snap to a power-of-2
        texture_height = nearest_power_of_2(render_height + 2 * abs_margin)
    else:
        texture_height = nearest_power_of_2(max_resolution)
        abs_margin = texture_height * margin
        render_height = texture_height - 2 * abs_margin
        render_width = render_height * svg_ratio
        texture_width = nearest_power_of_2(render_width + 2 * abs_margin)

    offset_x = (texture_width - render_width) / 2
    offset_y = (texture_height - render_height) / 2

    return (texture_width, texture_height), (offset_x, offset_y, render_width, render_height)


def svg_to_image(svg_path: t.Union[str, Path], max_resolution: int = 512, margin:float=0.1) -> t.Optional[QImage]:
    """
    Convert an SVG file to a QImage with specified dimensions.

    Creates a transparent QImage and renders the SVG content onto it.

    Args:
        svg_path: Path to the SVG file as a string or Path object
        max_resolution:
        margin:

    Returns:
        QImage: The rendered image if successful, None otherwise
    """

    # Create SVG renderer
    renderer = QSvgRenderer(str(svg_path) if isinstance(svg_path, Path) else svg_path)
    svg_size = renderer.defaultSize()

    texture_size, render_rect = calculate_render_dimensions((svg_size.width(), svg_size.height()), max_resolution, margin)

    # Create a blank transparent image
    image = QImage(texture_size[0], texture_size[1], QImage.Format_ARGB32)
    image.fill(0)  # Fill with transparency (0 = fully transparent)

    # Set up the painter for the image
    painter = QPainter(image)

    # Render SVG to image if valid
    if renderer.isValid():
        renderer.render(painter, QRectF(*render_rect))
        painter.end()
        logger.debug(f"SVG converted successfully: {svg_path}")
        return image
    else:
        painter.end()
        logger.error(f"Failed to load SVG from {svg_path}")
        return None


def image_to_numpy(image: QImage) -> np.ndarray:
    """
    Convert a QImage to a numpy array.

    :param image: Input QImage object
    :return: Numpy array with shape (height, width, 4) in BGRA format
    """

    # Ensure the QImage is in the format of 32-bit ARGB (4 channels)
    image = image.convertToFormat(QImage.Format_ARGB32)

    # QImage's bits() returns a memoryview in PySide6
    buffer = image.constBits()

    # Get size and create numpy array
    buffer_size = image.sizeInBytes()

    # Create a copy of the data
    img_array = np.array(buffer[:buffer_size], dtype=np.uint8).reshape(
        image.height(), image.width(), 4)

    # Note: the format is actually BGRA in memory
    return img_array


def numpy_to_image(img_array: np.ndarray) -> QImage | None:
    """
    Converts a NumPy array to a QImage.

    :param img_array: Input image as a NumPy array in Grayscale or BGRA format.
    :return: Corresponding QImage object if successful, otherwise None.
    """

    # Ensure array is contiguous and uint8
    img_array = np.ascontiguousarray(img_array).astype(np.uint8)

    # Grayscale image
    if len(img_array.shape) == 2:
        height, width = img_array.shape
        logger.debug(f"Converting grayscale image ({width}x{height}) to QImage.")
        return QImage(img_array.data, width, height, width, QImage.Format_Grayscale8)

    # BGRA image
    elif len(img_array.shape) == 3 and img_array.shape[2] == 4:
        height, width, channels = img_array.shape
        logger.debug(f"Converting BGRA image ({width}x{height}) to QImage.")
        return QImage(img_array.data, width, height, width * channels, QImage.Format_ARGB32)

    # Unsupported format
    logger.warning(f"Unsupported array format: shape {img_array.shape}, dtype {img_array.dtype}")
    return None
