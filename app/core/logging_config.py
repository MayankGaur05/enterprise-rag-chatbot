import sys

from loguru import logger

_configured = False

def setup_logging(log_level:str = "INFO"):
    """
    Set up logging configuration using loguru.
    This function configures the logger to output logs to stdout with a specified log level 
    and format.
    """
    global _configured 
    if _configured:
         return logger

    logger.remove()  # Remove the default logger
    logger.add(
         sys.stdout,
         level=log_level.upper(),
         format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}",
         enqueue=False,
         backtrace=False,
         diagnose=False
    )
    _configured = True
    return logger
    