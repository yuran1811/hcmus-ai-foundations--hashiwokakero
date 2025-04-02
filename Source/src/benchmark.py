import functools
import os
import time
import tracemalloc
from enum import Enum
from typing import Callable

import matplotlib.pyplot as plt

from __types import Grid
from constants.path import INP_DIR
from solvers import (
    solve_with_astar,
    solve_with_backtracking,
    solve_with_bruteforce,
    solve_with_pysat,
)
from utils import byte_convert, parse_input, time_convert

TEST_SETS = [7, 9, 11]


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
    return bool(solver_func(grid))


def tests_prepare():
    _: list[tuple[str, str, Grid]] = []
    for s in TEST_SETS:
        size = f"{s}x{s}"
        dir = os.path.join(INP_DIR, size)
        if not os.path.exists(dir):
            os.makedirs(dir)

        for inp_file in sorted(os.listdir(dir)):
            path = os.path.join(dir, inp_file)
            _.append((f"{size}/{inp_file}", path, parse_input(path)))
    return _


def visualize(
    plot_data: dict[str, list[tuple[str, float, float, bool]]], criteria: Criteria
):
    data = list(plot_data.items())

    _, axs = plt.subplots(2, 3, figsize=(15, 10))

    x_values = [
        x for x in sorted([x for x, _ in data], key=lambda x: int(x.split("x")[0]))
    ]
    x_bars = [x.split("/")[1].split(".")[0].split("-")[1] for x in x_values]
    y_data: dict[str, list[list]] = {}

    for test_inp, values in data:
        algos, times, mems, solved = zip(*values)

        # Convert to appropriate types
        algos = list(algos)
        solved = [bool(s) for s in solved]

        if test_inp not in y_data:
            y_data[test_inp] = [[] for _ in range(4)]

        for k in range(4):
            y_data[test_inp][k].extend([algos[k], times[k], mems[k], solved[k]])

    y_values = sorted(
        [y for y in y_data.items()], key=lambda x: int(x[0].split("x")[0])
    )

    last_from = 0
    for i, size in enumerate(TEST_SETS):
        ri = i // 3
        ci = i % 3

        y_bar = [v for k, v in y_values if k.startswith(f"{size}x{size}")]
        axs[ri][ci].plot(
            x_bars[last_from : last_from + len(y_bar)],
            [y[0][criteria.value[0]] for y in y_bar],
            "o-",
            [y[1][criteria.value[0]] for y in y_bar],
            "*--",
            [y[2][criteria.value[0]] for y in y_bar],
            "d:",
            [y[3][criteria.value[0]] for y in y_bar],
            "s-",
            label="",
            markersize=6,
        )
        axs[ri][ci].set_xlabel("input")
        axs[ri][ci].set_ylabel(criteria.value[2])
        axs[ri][ci].set_title(f"Map {size}x{size} {criteria.value[1]}")

        last_from += len(y_bar)

    plt.tight_layout()
    # plt.suptitle("Group Title")
    plt.show()


if __name__ == "__main__":
    solved_count = [0] * 4
    solvers: list[tuple[str, Callable, list[int]]] = [
        ("pysat", solve_with_pysat, []),
        ("astar", solve_with_astar, []),
        ("backtracking", solve_with_backtracking, [7]),
        ("bruteforce", solve_with_bruteforce, [7]),
    ]

    plot_data: dict[str, list[tuple[str, float, float, bool]]] = {}

    print("+ Testing")
    tests = tests_prepare()
    for name, path, grid in tests:
        print(f"  > exec: {name}")
        plot_data[name] = []

        for i, (algo, solver, size) in enumerate(solvers):
            if size and name.startswith(f"{size}x{size}"):
                continue

            solved, t, _, peak_mem = benchmark(solver, grid)
            plot_data[name].append((algo, t * 1000, peak_mem / 1024, bool(solved)))
            solved_count[i] += bool(solved)

            print(
                f"    | {algo[:5]}: {bool(solved)}\t{time_convert(t)},{byte_convert(peak_mem)}"
            )

    print("\n+ Summary")
    for i, (algo, solver, _) in enumerate(solvers):
        print(
            f"  | {algo}: {solved_count[i]}/{len(tests)} ({100 * solved_count[i] / len(tests)}%)"
        )

    print("\n+ Plotting")
    visualize(plot_data, Criteria.TIME)
    visualize(plot_data, Criteria.MEMORY)
