import config
from core.logger import setup_logging, get_logger
from processor import process_svg


def main() -> None:
    setup_logging(level="DEBUG")
    logger = get_logger(__name__)

    for source_dir, output_dir in config.PROCESSING_PATHS:
        logger.info(f'Processing source directory {source_dir}')

        if not source_dir.is_dir():
            logger.warning(f"Given source path {source_dir} is not a valid directory")
            continue

        svg_files = list(source_dir.glob("*.svg"))

        for svg_path in svg_files:
            output_path = output_dir / (svg_path.stem + config.OUTPUT_FILE_POSTFIX + config.OUTPUT_FILE_EXT)
            process_svg(svg_path, output_path, 0.1, config.SVG_RENDERING_RESOLUTION, config.SDF_RESOLUTION)

if __name__ == "__main__":
    main()