"""Methods to measure execution time
"""
import logging
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def timeit(msg: str, level=logging.DEBUG):
    """Allows wrapping execution of the code in a context manager that measures execution time"""
    now = time.perf_counter()
    try:
        yield
    finally:
        logger.log(level=level, msg=f"{msg}: {time.perf_counter() - now}s")
