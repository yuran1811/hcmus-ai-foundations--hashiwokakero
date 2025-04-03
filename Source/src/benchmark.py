import functools
import os
import time
import tracemalloc
from enum import Enum
from typing import Callable

import matplotlib.pyplot as plt

from __types import Grid
from constants.path import FIG_DIR, INP_DIR
from solvers import (
    solve_with_astar,
    solve_with_backtracking,
    solve_with_bruteforce,
    solve_with_pysat,
)
from utils import byte_convert, parse_input, time_convert

TEST_SETS = [7, 9, 11, 13, 17, 20]
SOLVERS: list[tuple[str, Callable, list[int]]] = [
    ("pysat", solve_with_pysat, TEST_SETS),
    ("astar", solve_with_astar, TEST_SETS[:0]),
    ("backtracking", solve_with_backtracking, TEST_SETS[:4]),
    ("bruteforce", solve_with_bruteforce, TEST_SETS[:0]),
]
SOLVER_COUNT = len(SOLVERS)
PASSED_COUNT = [0] * SOLVER_COUNT


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
            y_data[test_inp] = [[] for _ in range(SOLVER_COUNT)]

        for k in range(SOLVER_COUNT):
            y_data[test_inp][k].extend([algos[k], times[k], mems[k], solved[k]])

    y_values = sorted(
        [y for y in y_data.items()], key=lambda x: int(x[0].split("x")[0])
    )

    last_from = 0
    for i, size in enumerate(TEST_SETS):
        ri = i // 3
        ci = i % 3

        y_bar = [v for k, v in y_values if k.startswith(f"{size}x{size}")]
        x_bar = x_bars[last_from : last_from + len(y_bar)]
        markers = ["o-", "*--", "d:", "s-"]

        for k in range(len(y_bar[0])):
            if any([not y[k][criteria.value[0]] for y in y_bar]):
                continue

            axs[ri][ci].plot(
                x_bar,
                [y[k][criteria.value[0]] for y in y_bar],
                markers[k],
                label=y_bar[0][k][0],
                markersize=6,
            )
        axs[ri][ci].set_xlabel("input")
        axs[ri][ci].set_ylabel(criteria.value[2])
        axs[ri][ci].set_title(f"Map {size}x{size} {criteria.value[1]}")
        axs[ri][ci].legend(loc="lower right", fontsize=8)

        last_from += len(y_bar)

    plt.tight_layout()
    # plt.suptitle("Group Title")
    # plt.show()

    saved_filename = f"benchmark-{"_".join(criteria.value[1].split(" "))}.png"
    saved_file = os.path.join(FIG_DIR, saved_filename)
    plt.savefig(saved_file, format="png")
    print(
        f"  > saved: {saved_file}",
    )


if __name__ == "__main__":
    plot_data: dict[str, list[tuple[str, float, float, bool]]] = {}

    print("+ Testing")
    tests = tests_prepare()
    failed_tests = {name: [] for name, _, _ in SOLVERS}
    for name, path, grid in tests:
        print(f"  > exec: {name}")
        plot_data[name] = []

        for i, (algo, solver, size) in enumerate(SOLVERS):
            if len(size) == 0 or not any(name.startswith(f"{_}x{_}") for _ in size):
                plot_data[name].append((algo, 0, 0, False))
                continue

            solved, t, _, peak_mem = benchmark(solver, grid)
            plot_data[name].append((algo, t * 1000, peak_mem / 1024, bool(solved)))
            if not bool(solved):
                failed_tests[algo].append(name)
            PASSED_COUNT[i] += bool(solved)

            print(
                f"    | {algo[:5]}: {bool(solved)}\t{time_convert(t)},{byte_convert(peak_mem)}"
            )

    print("\n+ Summary")
    for i, (algo, solver, size) in enumerate(SOLVERS):
        used_tests = (
            [x for x in tests if any([x[0].startswith(f"{_}x{_}") for _ in size])]
            if size
            else []
        )
        if len(used_tests):
            print(
                f"  | {algo}: {PASSED_COUNT[i]}/{len(used_tests)} - {(100 * PASSED_COUNT[i] / len(used_tests)):.2f}%",
                f"(failed on: {",".join([f"'{x}'" for x in failed_tests[algo]])})"
                if len(failed_tests[algo])
                else "",
            )

    print("\n+ Plotting")
    visualize(plot_data, Criteria.TIME)
    visualize(plot_data, Criteria.MEMORY)
