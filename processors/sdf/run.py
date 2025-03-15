import core.logging as logging
import processors.sdf.processor as processor


def main() -> None:
    logging.setup_logging(level="DEBUG")
    logger = logging.get_logger(__name__)

    processor.process_sdf()

if __name__ == "__main__":
    main()