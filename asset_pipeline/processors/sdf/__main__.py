from pathlib import Path
import argparse
import asset_pipeline.core.logging as logging
import asset_pipeline.processors.sdf.processor as processor
import asset_pipeline.processors.sdf.config as cfg


def main() -> None:

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="SDF Processor")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    log_level: logging.LogLevel = "DEBUG" if args.debug else "INFO"
    logging.setup_logging(level=log_level)
    logger = logging.get_logger(__name__)

    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    config = cfg.load_config(config_path)
    logger.debug(f"Loaded config: {config}")

    processor.process_sdf(config)

if __name__ == "__main__":
    main()