import logging
import os
from logging.handlers import RotatingFileHandler


def configure_logging():
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'system.log')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5)
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)
