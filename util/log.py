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


def before(func):
    """Record log message when entering a function

    Do not use this along with `after`, instead using `trace`.
    """
    def wrapper(*args, **kwargs):
        logger.debug('enter ' + func.__module__ + '.' + func.__name__)
        result = func(*args, **kwargs)
        return result
    return wrapper


def after(func):
    """Record log message when leaving a function

    Do not use this along with `before`, instead using `trace`.
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug('leave ' + func.__module__ + '.' + func.__name__)
        return result
    return wrapper


def trace(func):
    """Record log message when entering and leaving a function"""
    def wrapper(*args, **kwargs):
        logger.debug('enter ' + func.__module__ + '.' + func.__name__)
        result = func(*args, **kwargs)
        logger.debug('leave ' + func.__module__ + '.' + func.__name__)
        return result
    return wrapper
