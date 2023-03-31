import time
from contextlib import contextmanager

@contextmanager
def timeit(message : str):
    now = time.perf_counter()
    try:
        yield
    finally:
        print(f'{message} : {time.perf_counter() - now}s')