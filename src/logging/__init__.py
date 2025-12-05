# src/logging/__init__.py
from .log_handler import setup_logging, log_message

setup_logging()

# Now you can do:
# from src.logging import log_message
# log_message("This is a log message")
