import numpy as np
import struct

import asset_pipeline.core.logging as logging

logger = logging.get_logger(__name__)


def save_dds_from_mipmaps(mipmaps, filename):
    """
    Save a list of numpy arrays as an uncompressed 32-bit RGBA DDS file.

    Each element in 'mipmaps' represents one mip level, with mipmaps[0] as the main image.
    Each array must have shape (height, width, 4) and dtype=np.uint8.
    This function checks that each mip level's dimensions are exactly half (or 1 when minimal)
    of the previous level.

    :param mipmaps: list of numpy.ndarray, each of shape (H, W, 4) with dtype np.uint8.
    :param filename: output file path.
    :raises ValueError: if any of the arrays do not conform to the expected shape/dtype.
    """
    if not mipmaps:
        raise ValueError("Mipmaps list is empty.")

    # Validate each mip level.
    for i, arr in enumerate(mipmaps):
        if not isinstance(arr, np.ndarray):
            raise ValueError(f"Mip level {i} is not a numpy array.")
        if arr.ndim != 3 or arr.shape[2] != 4:
            raise ValueError(f"Mip level {i} must have shape (H, W, 4), got {arr.shape}.")
        if arr.dtype != np.uint8:
            raise ValueError(f"Mip level {i} must have dtype np.uint8, got {arr.dtype}.")

    # Verify dimensions: each mip level must be half the size of the previous one.
    base_h, base_w, _ = mipmaps[0].shape
    expected_h, expected_w = base_h, base_w
    for i in range(1, len(mipmaps)):
        expected_h = max(1, expected_h // 2)
        expected_w = max(1, expected_w // 2)
        actual_h, actual_w, _ = mipmaps[i].shape
        if (actual_h, actual_w) != (expected_h, expected_w):
            raise ValueError(
                f"Mip level {i} has incorrect dimensions. Expected ({expected_h}, {expected_w}) "
                f"but got ({actual_h}, {actual_w})."
            )

    mip_count = len(mipmaps)

    # DDS header values for an uncompressed 32-bit RGBA texture.
    magic = b'DDS '
    header_size = 124
    # Flags: (DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_MIPMAPCOUNT | DDSD_PITCH)
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x8
    pitch = base_w * 4  # bytes per scanline for 32-bit RGBA
    reserved1 = (0,) * 11  # 11 reserved DWORDs

    # Pixel format (DDS_PIXELFORMAT structure, 32 bytes)
    pf_size = 32
    pf_flags = 0x41  # DDPF_RGB (0x40) | DDPF_ALPHAPIXELS (0x1)
    pf_fourcc = 0  # No compression
    pf_rgb_bit_count = 32
    pf_r_bitmask = 0x00FF0000
    pf_g_bitmask = 0x0000FF00
    pf_b_bitmask = 0x000000FF
    pf_a_bitmask = 0xFF000000
    # Pack the pixel format into a 32-byte string.
    pixel_format = struct.pack(
        '<IIIIIIII',
        pf_size, pf_flags, pf_fourcc, pf_rgb_bit_count,
        pf_r_bitmask, pf_g_bitmask, pf_b_bitmask, pf_a_bitmask
    )

    # Caps: DDSCAPS_TEXTURE | DDSCAPS_COMPLEX | DDSCAPS_MIPMAP
    caps1 = 0x1000 | 0x8 | 0x400000
    caps2 = caps3 = caps4 = 0
    reserved2 = 0

    # Use a single call to struct.pack. The format string:
    # '<7I11I32s5I' expects:
    # - 7 DWORDs: header_size, flags, base_h, base_w, pitch, depth (0), mip_count.
    # - 11 DWORDs: reserved1.
    # - 1 32-byte string: pixel_format.
    # - 5 DWORDs: caps1, caps2, caps3, caps4, reserved2.
    header = struct.pack(
        '<7I11I32s5I',
        header_size, flags, base_h, base_w, pitch, 0, mip_count,
        *reserved1,
        pixel_format,
        caps1, caps2, caps3, caps4, reserved2
    )

    # Write DDS file: magic + header + all mip levels data.
    with open(filename, 'wb') as f:
        f.write(magic)
        f.write(header)
        for mip in mipmaps:
            f.write(mip.tobytes())
    logger.debug(f"DDS file '{filename}' written successfully with {mip_count} mip levels.")


def test_save_dds():
    """
    Create a test mipmap chain with 5 levels.

    Each mip level is filled with a unique solid color for easy visual verification:
      - Mip 0: Red (256x256)
      - Mip 1: Green (128x128)
      - Mip 2: Blue (64x64)
      - Mip 3: Yellow (32x32)
      - Mip 4: Magenta (16x16)
    Then save the chain to a DDS file.
    """
    base_w, base_h = 256, 256
    mip_levels = []
    colors = [
        [255, 0, 0, 255],  # red
        [0, 255, 0, 255],  # green
        [0, 0, 255, 255],  # blue
        [255, 255, 0, 255],  # yellow
        [255, 0, 255, 255]  # magenta
    ]

    current_w, current_h = base_w, base_h
    for i, color in enumerate(colors):
        # Create an array filled with the given color.
        mip = np.full((current_h, current_w, 4), color, dtype=np.uint8)
        mip_levels.append(mip)
        # Update dimensions for the next mip level.
        current_w = max(1, current_w // 2)
        current_h = max(1, current_h // 2)

    # Save the DDS file with the list of mipmaps.
    save_dds_from_mipmaps(mip_levels, "test_mips.dds")
