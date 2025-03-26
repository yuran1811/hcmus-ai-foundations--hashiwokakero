from solvers.pysat_solver import solve_with_pysat
from utils import parse_input


def dev():
    print("dev")


def solve():
    grid = parse_input("data/input/input-00.txt")
    solution = solve_with_pysat(grid)
    print(solution)


def main() -> int:
    print("main")
    return 0
