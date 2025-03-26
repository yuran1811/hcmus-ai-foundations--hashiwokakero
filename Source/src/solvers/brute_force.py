from itertools import product
from typing import Dict, List, Optional, Tuple

from models import Island
from utils import identify_islands, is_fully_connected, is_valid_bridge


def brute_force_solver(
    grid: List[List[int]],
) -> Optional[Dict[Tuple[Island, Island], int]]:
    islands = identify_islands(grid)
    pairs = [(i, j) for i in islands for j in islands if i != j]
    max_bridges = 2  # At most 2 bridges per pair

    # Generate all possible bridge combinations
    for bridge_counts in product(range(max_bridges + 1), repeat=len(pairs)):
        solution = {}
        remaining = {island: island.num for island in islands}
        valid = True

        for idx, (a, b) in enumerate(pairs):
            count = bridge_counts[idx]
            if count > 0:
                if not is_valid_bridge(a, b, solution, grid):
                    valid = False
                    break
                solution[(a, b)] = count
                remaining[a] -= count
                remaining[b] -= count
                if remaining[a] < 0 or remaining[b] < 0:
                    valid = False
                    break

        if (
            valid
            and all(v == 0 for v in remaining.values())
            and is_fully_connected(solution, islands)
        ):
            return solution
    return None
