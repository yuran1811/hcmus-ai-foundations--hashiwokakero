import os
import re
import tomllib

from __types import Grid, Island
from constants.path import INP_DIR, ROOT_DIR


def get_project_toml_data() -> dict:
    try:
        with open(os.path.join(ROOT_DIR, "pyproject.toml"), "rb") as f:
            return tomllib.load(f)["project"]
    except FileNotFoundError:
        return {}


def get_input_path(size: int = 7, idx: int = 1) -> str:
    if size not in [3, 5, 7, 9, 11, 13, 17, 20] or idx < 1:
        raise ValueError(
            f"Invalid input size {size} or index {idx}. Size must be one of [3, 5, 7, 9, 11, 13, 17, 20] and index must be >= 1."
        )

    return os.path.join(INP_DIR, f"{size}x{size}", f"input-{idx:02d}.txt")


def parse_input(file_path: str):
    with open(file_path, "r") as f:
        lines = f.read().strip().split("\n")
        grid: Grid = []
        for line in lines:
            line = re.sub(r"\s+", "", line)  # Correctly remove all whitespace
            row = list(map(int, line.split(",")))
            grid.append(row)
        return grid


def generate_output(grid: Grid, islands: list[Island], sol: list[tuple[int, int, int]]):
    output = [["0" if cell == 0 else str(cell) for cell in row] for row in grid]
    for i, j, count in sol:
        a = next((r, c, deg) for (idx, r, c, deg) in islands if idx == i)
        b = next((r, c, deg) for (idx, r, c, deg) in islands if idx == j)

        if a[0] == b[0]:  # Horizontal
            y_min, y_max = sorted([a[1], b[1]])
            symbol = "-" if count == 1 else "="
            for y in range(y_min + 1, y_max):
                output[a[0]][y] = symbol
        else:  # Vertical
            x_min, x_max = sorted([a[0], b[0]])
            symbol = "|" if count == 1 else "$"
            for x in range(x_min + 1, x_max):
                output[x][a[1]] = symbol
    return output


def tests_prepare(test_sets: list[int]):
    _: list[tuple[str, str, Grid]] = []
    for s in test_sets:
        size = f"{s}x{s}"
        dir = os.path.join(INP_DIR, size)
        if not os.path.exists(dir):
            os.makedirs(dir)

        for inp_file in sorted(os.listdir(dir)):
            path = os.path.join(dir, inp_file)
            _.append((f"{size}/{inp_file}", path, parse_input(path)))
    return _
