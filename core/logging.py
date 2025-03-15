import typing as t
import logging

# Define log level type for type hints
LogLevel = t.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logging(
        level: LogLevel = "INFO",
        format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> None:
    """
    Configure the root logger with console output at the specified level.
    Call this once at the start of your application.

    Args:
        level: Root logging level
        format_str: Format for log messages
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with formatter
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format_str))
    root_logger.addHandler(handler)

    logging.debug("Logging configured")  # This will show if level is DEBUG


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