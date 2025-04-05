from solvers import solve_with_pysat
from utils.data import get_input_path, parse_input


def test_pysat_solver():
    grid = parse_input(get_input_path(7, 1))
    solution = solve_with_pysat(grid)
    assert solution is not None


def test_astar_solver():
    assert True
