from pathlib import Path
from PySide6.QtGui import QImage


PROCESSING_PATHS = [
    (Path(r'y:\Common\Textures\Brands\FigmaAssets'), Path(r'y:\Common\Textures\Brands\Export'))
]

SVG_RENDERING_RESOLUTION = 4096

SDF_RESOLUTION = 512
SDF_RELATIVE_DISTANCE = 0.03
SDF_CHANNEL_MAPPING = (0, 1, 2, 3)  # BGRA -> BGRA

OUTPUT_FILE_EXT = '.png'
OUTPUT_FILE_PREFIX = 'T_'
OUTPUT_FILE_POSTFIXES = {
    QImage.Format_Grayscale8: '_SDF',
    QImage.Format_ARGB32: '_MSDF',
}