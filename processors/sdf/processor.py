from pathlib import Path
import typing as t
import time

import core.qt_image as qt_image
import core.metadata as metadata
import core.logging as logging
import processors.sdf.converter as converter
import processors.sdf.config as config

logger = logging.get_logger(__name__)


def svg_to_sdf(svg_path: t.Union[str, Path], output_dir: t.Union[str, Path],
               rel_distance: float, svg_resolution: int, sdf_resolution: int) -> t.Union[Path, None]:
    """
    Converts an SVG file to a signed distance field (SDF) and saves the output.

    :param svg_path: Path to the input SVG file.
    :param output_dir: Directory where the generated SDF image will be saved.
    :param rel_distance: Relative distance parameter for SDF computation.
    :param svg_resolution: Resolution to render the SVG before SDF conversion.
    :param sdf_resolution: Target resolution for the final SDF output.
    """

    img = qt_image.svg_to_image(svg_path, svg_resolution, rel_distance)
    img_array = qt_image.image_to_numpy(img)
    sdf_array = converter.compute_multichannel_sdf(img_array, rel_distance, svg_resolution//sdf_resolution,
                                                   channel_mapping=config.SDF_CHANNEL_MAPPING)

    # Convert SDF to QImage
    sdf_image = qt_image.numpy_to_image(sdf_array)
    if sdf_image is None:
        logger.warning(f"Failed to convert SDF array to image for: {svg_path}")
        return None

    # Determine output filename
    file_postfix = config.OUTPUT_FILE_POSTFIXES[sdf_image.format()]
    output_path = output_dir / (config.OUTPUT_FILE_PREFIX + svg_path.stem + file_postfix + config.OUTPUT_FILE_EXT)

    # Save the final image
    if not sdf_image.save(str(output_path)):
        logger.error(f"Failed to save SDF image: {output_path}")

    return output_path


def process_sdf() -> None:
    """
    Processes all files from configured source directories, converting them to SDF format.
    """
    for source_dir, output_dir in config.PROCESSING_PATHS:
        logger.info(f'Scanning source asset directory: {source_dir}')

        if not source_dir.is_dir():
            logger.warning(f"Invalid directory: {source_dir}")
            continue

        svg_files = list(source_dir.glob("*.svg"))
        logger.info(f"Found {len(svg_files)} SVG assets")

        # Identify new and modified assets, count them, and store them in pending_files for processing.
        pending_files = []
        status_counts = {metadata.AssetStatus.NEW: 0, metadata.AssetStatus.MODIFIED: 0}
        for svg_path in svg_files:
            status = metadata.get_asset_status(svg_path)
            if status in status_counts:
                status_counts[status] += 1
                pending_files.append(svg_path)

        if not pending_files:
            logger.info(f"No new or modified assets found. All files are already up to date.")
            continue

        logger.info(f"Detected {status_counts[metadata.AssetStatus.NEW]} new assets, "
                    f"{status_counts[metadata.AssetStatus.MODIFIED]} modified assets.")
        for svg_path in pending_files:
            logger.info(f"Processing: {svg_path}")

            start_time = time.perf_counter()
            exported_path = svg_to_sdf(svg_path, output_dir, config.SDF_RELATIVE_DISTANCE,
                       config.SVG_RENDERING_RESOLUTION, config.SDF_RESOLUTION)
            elapsed_time = time.perf_counter() - start_time
            logger.info(f"Saved: {exported_path} ({elapsed_time:.2f}s)")

            metadata.refresh_metadata(svg_path, exported_files=[exported_path])

        logger.info(f"Exported SDF files to: {output_dir}")