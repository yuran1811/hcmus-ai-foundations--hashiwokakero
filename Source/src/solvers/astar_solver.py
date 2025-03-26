import heapq
from typing import Dict, List, Optional, Tuple

from models import Island
from utils import (
    count_connected_components,
    get_adjacent_islands,
    identify_islands,
    is_fully_connected,
    is_valid_bridge,
)


class AStarState:
    def __init__(
        self, bridges: Dict[Tuple[Island, Island], int], remaining: Dict[Island, int]
    ):
        self.bridges = (
            bridges  # Maps (start, end) island pairs to bridge count (1 or 2)
        )
        self.remaining = remaining  # Tracks remaining bridges needed per island
        self.cost = sum(self.bridges.values())  # Current number of bridges placed
        self.heuristic = self._compute_heuristic()

    def _compute_heuristic(self) -> float:
        # Heuristic 1: Total remaining bridges divided by 2
        total_remaining = sum(self.remaining.values()) / 2

        # Heuristic 2: Number of disconnected island groups
        connected_groups = count_connected_components(
            self.bridges, list(self.remaining.keys())
        )
        disconnect_penalty = connected_groups * 2  # Penalize disconnection

        return total_remaining + disconnect_penalty

    @property
    def priority(self) -> float:
        return self.cost + self.heuristic

    def __lt__(self, other: "AStarState") -> bool:
        return self.priority < other.priority


def solve_with_astar(
    grid: List[List[int]],
) -> Optional[Dict[Tuple[Island, Island], int]]:
    islands = identify_islands(grid)
    remaining = {island: island.num for island in islands}
    initial_state = AStarState(bridges={}, remaining=remaining)

    heap = []
    heapq.heappush(heap, initial_state)
    visited = set()

    while heap:
        current_state = heapq.heappop(heap)

        # Check if all islands are satisfied and connected
        if all(v == 0 for v in current_state.remaining.values()):
            if is_fully_connected(current_state.bridges, islands):
                return current_state.bridges

        # Generate next states by adding bridges
        for island in islands:
            if current_state.remaining[island] == 0:
                continue
            neighbors = get_adjacent_islands(island, islands, grid)
            for neighbor in neighbors:
                # direction = "horizontal" if island.x == neighbor.x else "vertical"

                if is_valid_bridge(island, neighbor, current_state.bridges, grid):
                    for count in [1, 2]:
                        if (
                            count > current_state.remaining[island]
                            or count > current_state.remaining[neighbor]
                        ):
                            continue
                        new_bridges = current_state.bridges.copy()
                        new_bridges[(island, neighbor)] = count
                        new_remaining = current_state.remaining.copy()
                        new_remaining[island] -= count
                        new_remaining[neighbor] -= count
                        new_state = AStarState(new_bridges, new_remaining)
                        state_key = frozenset(new_bridges.items())
                        if state_key not in visited:
                            visited.add(state_key)
                            heapq.heappush(heap, new_state)
    return None
