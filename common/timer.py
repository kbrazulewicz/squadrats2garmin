import logging
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def timeit(msg: str, level=logging.DEBUG):
    now = time.perf_counter()
    try:
        yield
    finally:
        logger.log(level=level, msg=f'{msg} : {time.perf_counter() - now}s')