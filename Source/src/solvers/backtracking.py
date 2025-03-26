from typing import Dict, List, Optional, Tuple

from models import Island
from utils import (
    get_adjacent_islands,
    identify_islands,
    is_fully_connected,
    is_valid_bridge,
)


def backtracking_solver(
    grid: List[List[int]],
) -> Optional[Dict[Tuple[Island, Island], int]]:
    islands = identify_islands(grid)
    remaining = {island: island.num for island in islands}
    solution = {}

    def backtrack(current_bridges: Dict[Tuple[Island, Island], int]) -> bool:
        if all(v == 0 for v in remaining.values()) and is_fully_connected(
            current_bridges, islands
        ):
            return True
        for island in islands:
            if remaining[island] == 0:
                continue
            for neighbor in get_adjacent_islands(island, islands, grid):
                if (island, neighbor) in current_bridges or (
                    neighbor,
                    island,
                ) in current_bridges:
                    continue
                for count in [1, 2]:
                    if count > remaining[island] or count > remaining[neighbor]:
                        continue
                    if is_valid_bridge(island, neighbor, current_bridges, grid):
                        current_bridges[(island, neighbor)] = count
                        remaining[island] -= count
                        remaining[neighbor] -= count
                        if backtrack(current_bridges):
                            return True
                        del current_bridges[(island, neighbor)]
                        remaining[island] += count
                        remaining[neighbor] += count
        return False

    if backtrack(solution):
        return solution
    return None
