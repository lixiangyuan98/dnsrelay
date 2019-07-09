"""Logging"""
import logging
from .opt import parsed_args


_log_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
}

_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] [%(threadName)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
_handler = logging.StreamHandler()
_handler.setFormatter(_formatter)

logger = logging.getLogger()
logger.setLevel(_log_level[parsed_args.log_level])
logger.addHandler(_handler)
