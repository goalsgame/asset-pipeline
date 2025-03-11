import logging
from pathlib import Path
from typing import List

import numpy as np
import scipy.ndimage as ndi
from PySide6.QtGui import QImage

# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



def compute_sdf(channel: np.ndarray, max_relative_distance: float = 0.1,
                downsample_factor: int = 4, threshold: int = 127) -> np.ndarray:
    """
    Compute a signed distance field from a grayscale channel and downsample it.

    Computes the distance transform for both inside and outside of the object defined
    by the binary threshold of the channel, then creates a signed distance field.
    The resulting SDF is downsampled for efficiency.

    Args:
        channel: Input grayscale channel as a 2D numpy array
        max_relative_distance: Maximum distance to consider in the distance field relative to texture size
        downsample_factor: Factor by which to downsample the resulting distance field
        threshold: Threshold value for binarizing the channel (0-255)

    Returns:
        np.ndarray: Downsampled signed distance field as a uint8 array
    """
    # Ensure the input is 2D
    if len(channel.shape) > 2:
        raise ValueError("Channel must be a 2D grayscale array")

    # Binarize the channel to remove anti-aliasing
    binary_mask = np.where(channel >= threshold, 255, 0).astype(np.uint8)

    # Dimensions calculation
    height, width = binary_mask.shape
    new_height = height // downsample_factor
    new_width = width // downsample_factor

    max_distance = max_relative_distance * max(height, width)

    # Calculate distance transforms at full resolution
    interior_distance = ndi.distance_transform_edt(binary_mask)  # Foreground (inside object)
    exterior_distance = ndi.distance_transform_edt(255 - binary_mask)  # Background (outside object)

    # Compute signed distance field at full resolution
    sdf = np.clip(interior_distance - exterior_distance, -max_distance, max_distance)

    # Use NumPy's advanced indexing for efficient downsampling
    downsampled_sdf = sdf[:height, :width].reshape(
        new_height, downsample_factor, new_width, downsample_factor).mean(axis=(1, 3))

    # Normalize to range [0, 255]
    normalized_sdf = 255 * (downsampled_sdf + max_distance) / (2 * max_distance)

    return normalized_sdf.astype(np.uint8)


def analyze_image_channels(image: np.ndarray) -> List[bool]:
    """
    Analyze an image to determine which channels have meaningful content.

    A channel is considered to have content if it has sufficient variation in pixel values.
    Channels that are uniform (all pixels have the same value) are considered empty.

    Args:
        image: Input image array with shape (height, width, channels)

    Returns:
        List[bool]: List indicating which channel has content
    """

    height, width, channels = image.shape

    # Initialize result with all channels empty
    channel_has_content = [True] * channels

    # Check each channel for content
    for channel_idx in range(channels):
        channel_data = image[:, :, channel_idx]

        # Check if channel is uniform (all pixels have the same value)
        min_val = np.min(channel_data)
        max_val = np.max(channel_data)

        if min_val == max_val:
            # Channel is uniform, consider it empty
            logger.debug(f"Image channel {channel_idx} is uniform with value {min_val}")
            channel_has_content[channel_idx] = False
            continue

    return channel_has_content


def compute_multichannel_sdf(img_array: np.ndarray, max_rel_distance: float = 0.1,
                             downsample_factor: int = 4, threshold: int = 127) -> np.ndarray:

    height, width, channels = img_array.shape

    # Calculate new dimensions after downsampling
    new_height = height // downsample_factor
    new_width = width // downsample_factor


    # Analyze which channels have meaningful content
    channel_content = analyze_image_channels(img_array)

    # Compute SDF for meaningful channels
    channels_sdf = []
    for idx, has_content in enumerate(channel_content):
        if not has_content:
            continue
        channel_sdf = compute_sdf(img_array[:, :, idx], max_rel_distance, downsample_factor, threshold)
        channels_sdf.append(channel_sdf)

    if len(channels_sdf) == 0:
        # No meaningful channels - return empty grayscale
        logger.warning("No channels have significant information")
        return np.zeros((new_height, new_width), dtype=np.uint8)

    if len(channels_sdf) == 1:
        logger.debug(f"Only channel has information, returning grayscale SDF")
        return channels_sdf[0]

    channels_number = max(len(channels_sdf), 3)
    output = np.zeros((new_height, new_width, channels_number), dtype=np.uint8)

    for idx, channel_sdf in enumerate(channels_sdf):
        output[..., idx] = channel_sdf

    return output


def save_image_array(distance_field: np.ndarray, filepath: Path) -> bool:
    """
    Save a distance field as an image with format determined by the array dimensions.

    Automatically determines the appropriate image format based on the array shape:
    - 2D array (h,w) → Grayscale image
    - 3D array with 3 channels (h,w,3) → RGB image
    - 3D array with 4 channels (h,w,4) → RGBA image

    Args:
        distance_field: NumPy array containing the distance field(s)
        filepath: Path where the image should be saved

    Returns:
        bool: True if the image was saved successfully, False otherwise

    Raises:
        ValueError: If the input array has an unsupported shape
    """
    # Ensure array is contiguous and uint8
    array = np.ascontiguousarray(distance_field).astype(np.uint8)

    # Determine image format based on array dimensions
    if len(array.shape) == 2:
        # 2D array - Grayscale
        height, width = array.shape
        qimage = QImage(array.data, width, height, width, QImage.Format_Grayscale8)
        logger.info(f"Saving grayscale image with dimensions {width}x{height}")

    elif len(array.shape) == 3 and array.shape[2] == 3:
        # 3D array with 3 channels - RGB
        height, width, _ = array.shape
        qimage = QImage(array.data, width, height, width * 3, QImage.Format_RGB888)
        logger.info(f"Saving RGB image with dimensions {width}x{height}")

    elif len(array.shape) == 3 and array.shape[2] == 4:
        # 3D array with 4 channels - RGBA/ARGB
        height, width, _ = array.shape

        # Convert to QImage's expected memory format (BGRA for ARGB32)
        bgra = np.zeros_like(array)
        bgra[..., 0] = array[..., 3]  # B = B (or A for ARGB)
        bgra[..., 1] = array[..., 2]  # G = G
        bgra[..., 2] = array[..., 1]  # R = R
        bgra[..., 3] = array[..., 0]  # A = A (or B for ARGB)

        qimage = QImage(bgra.data, width, height, width * 4, QImage.Format_ARGB32)
        logger.info(f"Saving RGBA image with dimensions {width}x{height}")

    else:
        raise ValueError(f"Unsupported array shape: {array.shape}. Must be (h,w), (h,w,3), or (h,w,4)")

    # Save the image to a file
    success = qimage.save(str(filepath))

    if success:
        logger.info(f"Successfully saved image to {filepath}")
    else:
        logger.error(f"Failed to save image to {filepath}")

    return success






