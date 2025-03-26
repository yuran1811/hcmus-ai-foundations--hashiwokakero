from src.solvers.astar_solver import solve_with_astar
from src.solvers.pysat_solver import solve_with_pysat
from src.utils import parse_input


def test_pysat_solver_simple():
    grid = parse_input("inputs/input-01.txt")
    solution = solve_with_pysat(grid)
    assert solution is not None


def test_astar_solver_simple():
    grid = [[0, 2, 0], [2, 0, 2], [0, 2, 0]]
    solution = solve_with_astar(grid)
    assert solution == ""
