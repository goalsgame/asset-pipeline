from pathlib import Path
from PySide6.QtGui import QImage
import dataclasses as dc
import typing as t

import asset_pipeline.core.datafiles.serialization as ser
import asset_pipeline.core.logging as logging

logger = logging.get_logger(__name__)


SDF_CHANNEL_MAPPING = (0, 1, 2, 3)  # BGRA -> BGRA

OUTPUT_FILE_EXT = '.png'
OUTPUT_FILE_PREFIX = 'T_'
OUTPUT_FILE_POSTFIXES = {
    QImage.Format_Grayscale8: '_SDF',
    QImage.Format_ARGB32: '_MSDF',
}

METADATA_EXTENSION = ".gsam"


@dc.dataclass(frozen=True)
class ProcessingPaths:
    source_dir: Path
    output_dir: Path

@dc.dataclass(frozen=True)
class SdfProcessorConfig:
    """SDF processor configuration data"""
    processing_paths: t.List[ProcessingPaths]
    svg_rasterization_size: int = 4096
    max_output_size: int = 512
    max_relative_distance: float = 0.03
    version: int = 1


def save_config(config: SdfProcessorConfig, config_path: t.Union[str, Path]) -> Path:
    """
    Save config to a file.

    :param config: SDF Processor config object to save
    :param config_path: Path to the config file
    :returns: Path to the saved config file
    """

    config_dict = ser.serialize_dataclass(config)
    ser.save_json(config_dict, config_path)
    logger.debug(f"Saved metadata file: {config_path}")
    return config_path


def load_config(config_path: t.Union[str, Path]) -> SdfProcessorConfig:
    """
    Load config from a file.

    :param config_path: Path to the config file
    :returns: SDF Processor config object
    """

    config_dict = ser.load_json(config_path)
    return ser.deserialize_dataclass(SdfProcessorConfig, config_dict)
