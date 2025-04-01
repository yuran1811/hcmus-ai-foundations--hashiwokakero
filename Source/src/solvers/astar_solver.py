from __types import Grid
from utils import encode_hashi


def solve_with_astar(grid: Grid):
    cnf, edge_vars, islands, var_counter = encode_hashi(grid)
