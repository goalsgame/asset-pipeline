import numpy as np
import scipy.ndimage as ndi
import typing as t

import core.logging as logging

logger = logging.get_logger(__name__)


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


def analyze_image_channels(image: np.ndarray) -> t.List[bool]:
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
                             downsample_factor: int = 4, threshold: int = 127,
                             channel_mapping: t.Tuple[int] = (0, 1, 2, 3)) -> np.ndarray | None:
    """
    Computes a multi-channel Signed Distance Field (SDF) from a given image.

    This function analyzes each channel of an image to determine if it contains meaningful information.
    If only one channel is relevant, it computes a single-channel SDF. Otherwise, it computes an SDF
    for each relevant channel and combines them into a 4-channel output.

    :param img_array: Input image as a NumPy array in RGBA format (shape: HxWx4, dtype: uint8).
    :param max_rel_distance: Maximum relative distance for SDF computation (0-1 range).
    :param downsample_factor: Factor by which the image is downsampled before computing SDF.
    :param threshold: Threshold value for detecting edges in the input image.
    :param channel_mapping: A list defining how the channels should be reordered in the output (default is [0, 1, 2, 3] for BGRA).
    :return: Computed multi-channel SDF image (shape: new_H x new_W x 4) or None if input is invalid.
    """

    # Validate input
    if img_array.ndim != 3 or img_array.shape[2] != 4:
        logger.warning("Invalid image array: Expected an HxWx4 NumPy array.")
        return None

    height, width, channels = img_array.shape

    # Calculate new dimensions after downsampling
    new_height = height // downsample_factor
    new_width = width // downsample_factor

    # Analyze which channels have meaningful content
    channels_have_content = analyze_image_channels(img_array)
    channel_count = sum(channels_have_content)

    if channel_count == 0:
        logger.warning("No significant content detected in any channel. Returning None.")
        return None

    # Single-channel SDF computation
    elif channel_count == 1:
        idx = channels_have_content.index(True)
        logger.debug(f"Single-channel SDF computation for channel {idx}.")
        return compute_sdf(img_array[:, :, idx], max_rel_distance, downsample_factor, threshold)

    # Multi-channel SDF computation
    output_sdf = np.zeros((new_height, new_width, 4), dtype=np.uint8)
    for idx, has_content in enumerate(channels_have_content):
        if not has_content:
            continue
        logger.debug(f"Multi-channel SDF computation for channel {idx}...")
        mapped_idx = channel_mapping[idx]
        output_sdf[..., mapped_idx] = compute_sdf(img_array[:, :, idx], max_rel_distance, downsample_factor, threshold)

    return output_sdf








