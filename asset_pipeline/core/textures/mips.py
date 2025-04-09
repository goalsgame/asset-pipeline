import math
from PySide6.QtGui import QImage
import asset_pipeline.core.textures.qt_image as qt_image
import asset_pipeline.core.textures.dds as dds

def get_num_mips(width, height):
    """
    Calculate the number of mip levels for given base dimensions.
    """
    return int(math.log2(max(width, height))) + 1

def get_coord_for_mip(base_x, base_width, base_height, mip_index):
    """
    Given a base position and size, return the coordinates of a specific mip level.
    Each mip is placed sequentially in the X direction.
    """
    w = max(base_width >> mip_index, 1)
    h = max(base_height >> mip_index, 1)
    x0 = base_x
    x1 = x0 + w
    y0 = 0
    y1 = h
    return (x0, y0, x1, y1), w  # Return new width to update x offset

def get_all_mipmap_coordinates(atlas_width, atlas_height):
    """
    Compute all mipmap slice coordinates in a single row layout.
    """
    base_width = atlas_width // 2
    base_height = atlas_height
    num_mips = get_num_mips(max(base_width, 1), max(base_height, 1))

    coords = []
    x_offset = 0
    for mip in range(num_mips):
        coord, w = get_coord_for_mip(x_offset, base_width, base_height, mip)
        coords.append(coord)
        x_offset += w
    return coords


def get_mipmap_slices(image):
    """
    Given an image (as a NumPy array), extract and return the mipmap slices according
    to the computed coordinates.

    Parameters:
        image (np.ndarray): The input image array. The image shape should be (height, width[, channels]).

    Returns:
        List[np.ndarray]: A list of image slices as NumPy arrays.
    """
    atlas_height, atlas_width = image.shape[:2]
    coords = get_all_mipmap_coordinates(atlas_width, atlas_height)
    slices = [image[y0:y1, x0:x1] for (x0, y0, x1, y1) in coords]
    return slices



img = QImage(r'y:\Test\Export\T_HatchingPattern_Mips_H.png')
print(img)
img_array = qt_image.image_to_numpy(img)
mip_slices = get_mipmap_slices(img_array)
dds.save_dds_from_mipmaps(mip_slices, r'y:\Test\Export\T_HatchingPattern_Mips_H.dds')
