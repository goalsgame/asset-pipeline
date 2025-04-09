from pathlib import Path
from PySide6.QtGui import QImage, QPainter
import typing as t
import time

import asset_pipeline.core.textures.qt_image as qt_image
import asset_pipeline.core.textures.mips as mips
import asset_pipeline.core.textures.dds as dds
import asset_pipeline.core.datafiles.metadata as metadata
import asset_pipeline.core.logging as logging
import asset_pipeline.processors.mips.config as cfg


logger = logging.get_logger(__name__)


def mips_to_dds(img_path: t.Union[str, Path], output_dir: t.Union[str, Path]) -> t.Union[Path, None]:
    """
    Converts an image file to a DDS file with mipmap layers.

    @param img_path: Path to the source image file
    @param output_dir: Target directory for the generated DDS file
    @return: Path to the created DDS file if successful, None if any error occurs
    """

    # Convert input paths to Path objects
    img_path = Path(img_path)
    output_dir = Path(output_dir)

    # Load source image
    img = QImage(str(img_path))  # QImage requires string path
    if img.isNull():
        logger.error(f"Failed to load image at path: {img_path}")
        return None

    img_array = qt_image.image_to_numpy(img)
    mip_slices = mips.get_mipmap_slices(img_array)
    logger.debug(f" Number of mip slices: {len(mip_slices)}")


    output_path = output_dir / (img_path.stem + cfg.OUTPUT_FILE_EXT)
    dds.save_dds_from_mipmaps(mip_slices, output_path)

    return output_path


def process_mips(config: cfg.MipsProcessorConfig) -> None:

    for paths in config.processing_paths:
        logger.info(f'Scanning source asset directory: {paths.source_dir}')

        if not paths.source_dir.is_dir():
            logger.warning(f"Invalid directory: {paths.source_dir}")
            continue

        svg_files = list(paths.source_dir.glob("*.png"))
        logger.info(f"Found {len(svg_files)} PNG assets")

        # Identify new and modified assets, count them, and store them in pending_files for processing.
        pending_files = []
        status_counts = {metadata.AssetStatus.NEW: 0, metadata.AssetStatus.MODIFIED: 0}
        for texture_path in svg_files:
            status = metadata.get_asset_status(texture_path)
            if status in status_counts:
                status_counts[status] += 1
                pending_files.append(texture_path)

        if not pending_files:
            logger.info(f"No new or modified assets found. All files are already up to date.")
            continue

        logger.info(f"Detected {status_counts[metadata.AssetStatus.NEW]} new assets, "
                    f"{status_counts[metadata.AssetStatus.MODIFIED]} modified assets.")
        for texture_path in pending_files:
            logger.info(f"Processing: {texture_path}")

            start_time = time.perf_counter()
            exported_path = mips_to_dds(texture_path, paths.output_dir)
            elapsed_time = time.perf_counter() - start_time
            logger.info(f"Saved: {exported_path} ({elapsed_time:.2f}s)")

            metadata.refresh_metadata(texture_path, exported_files=[exported_path])

        logger.info(f"Exported texture files to: {paths.output_dir}")
