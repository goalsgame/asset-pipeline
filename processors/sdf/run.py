import config
from core.logger import setup_logging, get_logger
from processor import process_sdf


def main() -> None:
    setup_logging(level="DEBUG")
    logger = get_logger(__name__)

    process_sdf()

if __name__ == "__main__":
    main()