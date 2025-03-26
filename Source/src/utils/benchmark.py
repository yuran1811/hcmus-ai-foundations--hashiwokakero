import time

from solvers import backtracking_solver, solve_with_astar, solve_with_pysat
from utils import parse_input


def benchmark(solver_func, grid):
    start = time.time()
    result = solver_func(grid)
    end = time.time()
    return end - start, result is not None


if __name__ == "__main__":
    grid_sizes = [
        ("7x7", parse_input("inputs/input-07.txt")),
        ("9x9", parse_input("inputs/input-09.txt")),
        ("11x11", parse_input("inputs/input-11.txt")),
    ]

    for name, grid in grid_sizes:
        print(f"Testing {name}:")

        # PySAT
        time_pysat, solved_pysat = benchmark(solve_with_pysat, grid)
        print(f"PySAT: {time_pysat:.2f}s | Solved: {solved_pysat}")

        # A*
        time_astar, solved_astar = benchmark(solve_with_astar, grid)
        print(f"A*: {time_astar:.2f}s | Solved: {solved_astar}")

        # Backtracking (only for small grids)
        if name == "7x7":
            time_bt, solved_bt = benchmark(backtracking_solver, grid)
            print(f"Backtracking: {time_bt:.2f}s | Solved: {solved_bt}")
