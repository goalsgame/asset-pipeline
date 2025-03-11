from pathlib import Path

from PySide6.QtGui import QImage

PROCESSING_PATHS = [
    (Path(r'y:\Common\Textures\Brands\Source'), Path(r'y:\Common\Textures\Brands\Export'))
]

OUTPUT_FILE_POSTFIXES = {
    QImage.Format_Grayscale8: '_H',
    QImage.Format_ARGB32: '_U',
}

OUTPUT_FILE_EXT = '.png'

SVG_RENDERING_RESOLUTION = 4096
SDF_RESOLUTION = 512