import argparse
import core.logging as logging
import processors.sdf.processor as processor


def main() -> None:
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="SDF Processor")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    log_level:logging.LogLevel = "DEBUG" if args.debug else "INFO"
    logging.setup_logging(level=log_level)
    logger = logging.get_logger(__name__)

    processor.process_sdf()

if __name__ == "__main__":
    main()