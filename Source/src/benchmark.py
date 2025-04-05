import os
from typing import Callable

import matplotlib.pyplot as plt

from constants.path import FIG_DIR, OUT_DIR
from solvers import (
    solve_with_astar,
    solve_with_backtracking,
    solve_with_bruteforce,
    solve_with_pysat,
)
from utils import (
    Criteria,
    benchmark,
    byte_convert,
    get_project_toml_data,
    parse_args,
    tests_prepare,
    time_convert,
    with_export_output,
    with_metrics,
)

TEST_SETS = [3, 5, 7, 9, 11, 13, 17, 20]
SOLVERS: list[tuple[str, Callable, list[int], bool]] = [
    ("pysat", solve_with_pysat, TEST_SETS[:], True),
    ("astar", solve_with_astar, TEST_SETS[:6], False),
    ("backtracking", solve_with_backtracking, TEST_SETS[:], False),
    ("bruteforce", solve_with_bruteforce, TEST_SETS[:0], False),
]
SOLVER_COUNT = len(SOLVERS)
PASSED_COUNT = [0] * SOLVER_COUNT


def visualize(
    plot_data: dict[str, list[tuple[str, float, float, bool]]], criteria: Criteria
):
    data = list(plot_data.items())

    num_col = 2
    num_row = len(TEST_SETS) // num_col + len(TEST_SETS) % num_col
    _, axs = plt.subplots(num_row, num_col, figsize=(5 * num_col, 3 * num_row))

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
        ri = i // num_col
        ci = i % num_col

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
    __toml = get_project_toml_data()
    args = parse_args(
        prog=__toml["name"],
        desc=__toml["description"],
        wrappers=[with_metrics, with_export_output],
    )

    plot_data: dict[str, list[tuple[str, float, float, bool]]] = {}

    print("+ Testing")
    tests = tests_prepare(TEST_SETS)
    failed_tests = {name: [] for name, _, _, _ in SOLVERS}
    for test_name, _, grid in tests:
        print(f"  > exec: {test_name}")
        plot_data[test_name] = []

        for i, (algo, solver, size, with_export) in enumerate(SOLVERS):
            if len(size) == 0 or not any(
                test_name.startswith(f"{_}x{_}") for _ in size
            ):
                plot_data[test_name].append((algo, 0, 0, False))
                continue

            sol, t, _, peak_mem = benchmark(solver, grid)
            is_solved = bool(sol)

            if not is_solved:
                failed_tests[algo].append(test_name)
            else:
                if args.export and with_export:
                    map = test_name.split("/")[0]
                    test_idx = test_name.split("/")[1].split("-")[1]
                    out_file = os.path.join(OUT_DIR, map, algo, f"output-{test_idx}")
                    os.makedirs(
                        os.path.join(OUT_DIR, map, algo),
                        exist_ok=True,
                    )

                    with open(out_file, "w") as f:
                        f.write("\n".join([" ".join(x) for x in sol]))
                        pass

            plot_data[test_name].append((algo, t * 1000, peak_mem / 1024, is_solved))
            PASSED_COUNT[i] += is_solved

            print(
                f"    | {algo[:5]}: {is_solved}\t{time_convert(t)},{byte_convert(peak_mem)}"
            )

    print("\n+ Summary")
    for i, (algo, solver, size, _) in enumerate(SOLVERS):
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

    if args.metrics:
        print("\n+ Plotting")
        visualize(plot_data, Criteria.TIME)
        visualize(plot_data, Criteria.MEMORY)
