import functools
import time
import tracemalloc
from enum import Enum
from typing import Callable

from __types import Grid


class Criteria(Enum):
    TIME = (1, "solving time", "time (ms)")
    MEMORY = (2, "peak memory", "memory (KB)")


def profile(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_time = time.perf_counter()

        ret = func(*args, **kwargs)
        result: str = ret if ret else ""

        elapsed_time = time.perf_counter() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return result, elapsed_time, current, peak

    return wrapper


@profile
def benchmark(solver_func, grid: Grid):
    return solver_func(grid)
