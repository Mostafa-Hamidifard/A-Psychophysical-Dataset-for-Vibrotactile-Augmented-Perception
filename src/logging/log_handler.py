import logging
import config


def setup_logging():
    logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")


def log_message(message):
    logging.info(message)
