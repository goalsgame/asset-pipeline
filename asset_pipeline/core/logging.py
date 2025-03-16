import typing as t
import logging

# Define log level type for type hints
LogLevel = t.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

def setup_logging(level: LogLevel = "INFO",) -> None:
    """
    Configure the root logger with console output at the specified level.
    Call this once at the start of your application.

    :param level: Root logging level
    :return:
    """
    log_level = LOG_LEVELS.get(level, logging.INFO)

    # Select log format
    format_str = "[%(levelname)s] %(message)s" if log_level > logging.DEBUG else "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with formatter
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format_str))
    root_logger.addHandler(handler)

    logging.debug("Logging configured")


def get_logger(name: str, level: t.Optional[LogLevel] = None) -> logging.Logger:
    """
    Get a logger with the specified name and optional level.

    Args:
        name: Logger name (typically __name__ for module loggers)
        level: Optional level override for this specific logger

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if level:
        logger.setLevel(getattr(logging, level))
    return logger