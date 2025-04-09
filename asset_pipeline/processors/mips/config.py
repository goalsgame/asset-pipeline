from pathlib import Path
import dataclasses as dc
import typing as t

import asset_pipeline.core.datafiles.serialization as ser
import asset_pipeline.core.logging as logging

logger = logging.get_logger(__name__)

OUTPUT_FILE_EXT = '.dds'
OUTPUT_FILE_PREFIX = 'T_'


@dc.dataclass(frozen=True)
class ProcessingPaths:
    source_dir: Path
    output_dir: Path


@dc.dataclass(frozen=True)
class MipsProcessorConfig:
    """SDF processor configuration data"""
    processing_paths: t.List[ProcessingPaths]
    version: int = 1


def save_config(config: MipsProcessorConfig, config_path: t.Union[str, Path]) -> Path:
    """
    Save config to a file.

    :param config: Mips Processor config object to save
    :param config_path: Path to the config file
    :returns: Path to the saved config file
    """

    config_dict = ser.serialize_dataclass(config)
    ser.save_json(config_dict, config_path)
    logger.debug(f"Saved metadata file: {config_path}")
    return config_path


def load_config(config_path: t.Union[str, Path]) -> MipsProcessorConfig:
    """
    Load config from a file.

    :param config_path: Path to the config file
    :returns: Mips Processor config object
    """

    config_dict = ser.load_json(config_path)
    return ser.deserialize_dataclass(MipsProcessorConfig, config_dict)
