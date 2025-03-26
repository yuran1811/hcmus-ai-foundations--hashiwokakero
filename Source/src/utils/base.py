from typing import Dict, List, Tuple

from models import Bridge, Island


def parse_input(file_path: str) -> List[List[int]]:
    with open(file_path, "r") as f:
        return [[int(num) for num in line.strip().split(", ")] for line in f]


def format_output(
    grid: List[List[int]], solution: Dict[Tuple[Island, Island], int]
) -> List[List[str]]:
    rows = len(grid)
    cols = len(grid[0])
    print(rows, cols)
    output = [[str(cell) if cell > 0 else "0" for cell in row] for row in grid]

    for (a, b), count in solution.items():
        if a.x == b.x:  # Horizontal bridge
            for y in range(min(a.y, b.y) + 1, max(a.y, b.y)):
                symbol = "-" if count == 1 else "="
                output[a.x][y] = symbol
        else:  # Vertical bridge
            for x in range(min(a.x, b.x) + 1, max(a.x, b.x)):
                symbol = "|" if count == 1 else "$"
                output[x][a.y] = symbol
    return output


def identify_islands(grid: List[List[int]]) -> List[Island]:
    islands = []
    for i, row in enumerate(grid):
        for j, num in enumerate(row):
            if num > 0:
                islands.append(Island(x=i, y=j, num=num))
    return islands


def get_adjacent_islands(
    island: Island, all_islands: List[Island], grid: List[List[int]]
) -> List[Island]:
    adjacent = []
    # Check left
    for y in range(island.y - 1, -1, -1):
        cell = grid[island.x][y]
        if cell > 0:
            adj = next((i for i in all_islands if i.x == island.x and i.y == y), None)
            if adj:
                adjacent.append(adj)
                break
    # Check right, up, down similarly...
    return adjacent


def is_fully_connected(
    bridges: Dict[Tuple[Island, Island], int], islands: List[Island]
) -> bool:
    if not bridges:
        return False
    visited = set()
    start = next(iter(bridges.keys()))[0]
    stack = [start]

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        for (a, b), count in bridges.items():
            if a == current and b not in visited:
                stack.append(b)
            elif b == current and a not in visited:
                stack.append(a)
    return len(visited) == len(islands)


def is_valid_bridge(
    a: Island,
    b: Island,
    existing_bridges: Dict[Tuple[Island, Island], int],
    grid: List[List[int]],
) -> bool:
    # Check if islands are aligned horizontally or vertically
    if a.x != b.x and a.y != b.y:
        return False

    # Check for intermediate islands/bridges
    if a.x == b.x:  # Horizontal bridge
        min_y, max_y = sorted([a.y, b.y])
        for y in range(min_y + 1, max_y):
            if grid[a.x][y] != 0:  # Blocked by island
                return False
            # Check for existing vertical bridges crossing this path
            for (other_a, other_b), count in existing_bridges.items():
                if other_a.y == y or other_b.y == y:
                    return False
    else:  # Vertical bridge
        min_x, max_x = sorted([a.x, b.x])
        for x in range(min_x + 1, max_x):
            if grid[x][a.y] != 0:  # Blocked by island
                return False
            # Check for existing horizontal bridges crossing this path
            for (other_a, other_b), count in existing_bridges.items():
                if other_a.x == x or other_b.x == x:
                    return False

    return True


def is_crossing(h_bridge: Bridge, v_bridge: Bridge) -> bool:
    # Horizontal bridge spans (x, y1) to (x, y2)
    hx = h_bridge.start.x
    hy1, hy2 = sorted([h_bridge.start.y, h_bridge.end.y])

    # Vertical bridge spans (x1, y) to (x2, y)
    vy = v_bridge.start.y
    vx1, vx2 = sorted([v_bridge.start.x, v_bridge.end.x])

    # Check if bridges intersect at (hx, vy)
    return (hy1 <= vy <= hy2) and (vx1 <= hx <= vx2)


def count_connected_components(
    bridges: Dict[Tuple[Island, Island], int], islands: List[Island]
) -> int:
    visited = set()
    components = 0
    for island in islands:
        if island not in visited:
            stack = [island]
            components += 1
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                for (a, b), _ in bridges.items():
                    if a == current and b not in visited:
                        stack.append(b)
                    elif b == current and a not in visited:
                        stack.append(a)
    return components
