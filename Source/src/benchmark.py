import functools
import time
import tracemalloc
from typing import Callable

from __types import Grid
from solvers import solve_with_astar, solve_with_bruteforce, solve_with_pysat
from utils import get_input_path, parse_input, time_convert


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
    result: str = solver_func(grid)
    return result is not None


if __name__ == "__main__":
    grids = [
        *[("7x7", parse_input(get_input_path(7, i + 1))) for i in range(5)],
        *[("9x9", parse_input(get_input_path(9, i + 1))) for i in range(5)],
        *[("11x11", parse_input(get_input_path(11, i + 1))) for i in range(5)],
        *[("13x13", parse_input(get_input_path(13, i + 1))) for i in range(5)],
        *[("17x17", parse_input(get_input_path(17, i + 1))) for i in range(5)],
        *[("20x20", parse_input(get_input_path(20, i + 1))) for i in range(5)],
    ]

    for name, grid in grids:
        print(f"[testing] {name}:")

        # PySAT
        solved_pysat, t, _, _ = benchmark(solve_with_pysat, grid)
        print(f"PySAT: {time_convert(t)} | Solved: {solved_pysat}")

        # A*
        solved_astar, t, _, _ = benchmark(solve_with_astar, grid)
        print(f"A*: {time_convert(t)} | Solved: {solved_astar}")

        # Backtracking (only for small grids)
        if name == "7x7":
            solved_bt, t, _, _ = benchmark(solve_with_bruteforce, grid)
            print(f"Backtracking: {time_convert(t)} | Solved: {solved_bt}")
