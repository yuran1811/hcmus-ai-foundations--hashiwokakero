import os
import re
import tomllib

from pysat.card import CardEnc
from pysat.card import EncType as CardEncType
from pysat.formula import CNF
from pysat.pb import EncType as PBEncType
from pysat.pb import PBEnc

from __types import Edge, EdgeExtend, Grid, Incident, Island, PairII
from classes import DSU
from constants.path import INP_DIR, ROOT_DIR


def time_convert(time: float) -> str:
    if time < 1:
        return f"{time * 1000:.2f} ms"
    return f"{time:.2f} s"


def byte_convert(num: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num < 1024:
            return f"{num:.2f} {unit}"
        num /= 1024.0

    return f"{num:.2f} PB"


def get_project_toml_data() -> dict:
    try:
        with open(os.path.join(ROOT_DIR, "pyproject.toml"), "rb") as f:
            return tomllib.load(f)["project"]
    except FileNotFoundError:
        return {}


def get_input_path(size: int = 7, idx: int = 1) -> str:
    if size not in [7, 9, 11, 13, 17, 20] or idx < 1:
        raise ValueError(
            f"Invalid input size {size} or index {idx}. Size must be one of [7, 9, 11, 13, 17, 20] and index must be >= 1."
        )

    return os.path.join(INP_DIR, f"{size}x{size}", f"input-{idx:02d}.txt")


def in_bounds(r: int, c: int, nrows: int, ncols: int):
    return 0 <= r < nrows and 0 <= c < ncols


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


def prettify_output(output: list[list[str]]):
    if output:
        [print(" ".join(x)) for x in output]


def get_islands(grid: Grid):
    islands: list[Island] = []
    for r, row in enumerate(grid):
        for c, _ in enumerate(row):
            if _:
                islands.append((len(islands), r, c, _))
    return islands


def potential_edges(grid: Grid, islands: list[Island]):
    nrows, ncols = len(grid), len(grid[0])
    island_from_pos = {(r, c): idx for (idx, r, c, _) in islands}

    edges: dict[PairII, Edge] = {}
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for idx, r, c, _ in islands:
        for dr, dc in directions:
            rr, cc = r + dr, c + dc

            while in_bounds(rr, cc, nrows, ncols):
                if grid[rr][cc]:
                    other_idx = island_from_pos.get((rr, cc))
                    if other_idx and other_idx != idx:
                        key = (min(idx, other_idx), max(idx, other_idx))
                        if key not in edges:
                            edges[key] = ((r, c), (rr, cc))
                    break

                rr += dr
                cc += dc
    return edges


def edge_orientation(edge: EdgeExtend):
    (_, _, (r1, c1), (r2, c2)) = edge
    if r1 == r2:
        return "h"
    if c1 == c2:
        return "v"
    return "other"


def edge_span(edge: EdgeExtend):
    (_, _, (r1, c1), (r2, c2)) = edge
    return (min(r1, r2), max(r1, r2), min(c1, c2), max(c1, c2))


def edges_cross(e1: EdgeExtend, e2: EdgeExtend):
    if e1[0] == e2[0] or e1[0] == e2[1] or e1[1] == e2[0] or e1[1] == e2[1]:
        return False

    o1 = edge_orientation(e1)
    o2 = edge_orientation(e2)
    if {o1, o2} != {"h", "v"}:
        return False

    if o1 == "v":
        e1, e2 = e2, e1

    e1_span = edge_span(e1)
    e2_span = edge_span(e2)
    r = e1_span[0]  # row of the horizontal edge
    c = e2_span[2]  # column of the vertical edge
    cmin, cmax = e1_span[2], e1_span[3]
    rmin, rmax = e2_span[0], e2_span[1]
    return (rmin < r < rmax) and (cmin < c < cmax)


def check_hashi(islands: list[Island], sol: list[tuple[int, int, int]]):
    mst = DSU(len(islands))

    for i, j, _ in sol:
        mst.merge(i, j)

    root = mst.root(0)
    for i in range(1, len(islands)):
        if mst.root(i) != root:
            return False

    return True


def validate_solution(
    islands: list[Island], edge_vars: dict[PairII, PairII], model: list[int]
):
    sol = extract_solution(model, edge_vars)
    return check_hashi(islands, sol)


def extract_solution(model: list[int], edge_vars: dict[PairII, PairII]):
    solution: list[tuple[int, int, int]] = []

    model = [_ for _ in model if _ > 0]
    for (i, j), (vx, vd) in edge_vars.items():
        use_x = vx in model
        use_d = vd in model

        count = (use_x or use_d) + use_d
        if count > 0:
            solution.append((i, j, count))

    return solution


def encode_pbequal(lits: list[int], weights: list[int], k: int, top_id: int):
    def next_var():
        nonlocal top_id
        top_id += 1
        return top_id

    clauses: list[list[int]] = []

    n = len(lits)
    if n == 0:
        return [[1], [-1]] if k else []

    s = [{} for _ in range(n + 1)]
    s[0][0] = next_var()
    clauses.append([s[0][0]])

    for i in range(1, n + 1):
        x_i = lits[i - 1]
        a_i = weights[i - 1]
        s_prev = s[i - 1]
        s_curr = {}

        # Iterate over achievable sums from the previous step
        for prev_sum in s_prev:
            aux_prev = s_prev[prev_sum]

            # Case 1: x_i is False (sum remains prev_sum)
            if prev_sum not in s_curr:
                s_curr[prev_sum] = next_var()
            aux_false = s_curr[prev_sum]
            clauses.append([-aux_prev, x_i, aux_false])  # ~aux_prev → (x_i ∨ aux_false)

            # Case 2: x_i is True (sum increases by a_i)
            new_sum = prev_sum + a_i
            if new_sum not in s_curr:
                s_curr[new_sum] = next_var()
            aux_true = s_curr[new_sum]
            clauses.append([-aux_prev, -x_i, aux_true])  # ~aux_prev → (~x_i ∨ aux_true)

        for sum_val in s_curr:
            for other_sum in s_curr:
                if sum_val != other_sum:
                    clauses.append([-s_curr[sum_val], -s_curr[other_sum]])
        s[i] = s_curr

    # Final constraint: sum after processing all variables must equal k
    if k not in s[n]:
        return [[1], [-1]]  # Unsatisfiable if k is unreachable

    clauses.append([s[n][k]])  # Enforce final sum = k

    # Ensure no other sums are active in the final step
    for sum_val in s[n]:
        if sum_val != k:
            clauses.append([-s[n][sum_val]])

    return clauses


def encode_hashi(
    grid: Grid,
    pbenc: int = PBEncType.bdd,
    cardenc: int = CardEncType.mtotalizer,
    *,
    use_pysat: bool = False,
):
    islands = get_islands(grid)
    n_islands = len(islands)

    island_incident: Incident = {idx: [] for idx in range(n_islands)}
    pot_edges = potential_edges(grid, islands)
    edge_vars: dict[PairII, PairII] = {}

    cnf = CNF()
    var_counter = 1

    """[[Phase 1]]"""
    # Add variables for edges (vx: single bridge, vd: double bridge)
    for edge in pot_edges:
        edge_vars[edge] = (var_counter, var_counter + 1)
        var_counter += 2
    max_edge_vars_counter = var_counter

    # At most one bridge type per edge (can be 0 when not using the edge)
    for vx, vd in edge_vars.values():
        cnf.append([-vx, -vd])

    """[[Phase 2]]"""
    # Populate incident edges (generate the adj list for each island)
    for (i, j), (vx, vd) in edge_vars.items():
        island_incident[i].extend([vx, vd])
        island_incident[j].extend([vx, vd])

    # Degree constraints
    for idx, _, _, degree in islands:
        lits = island_incident[idx]
        weights = [[2, 1][x & 1] for x in lits]
        if not lits and degree:
            print(f"[unsat]: no edges for island {idx}")
            cnf.append([])
            continue

        if use_pysat:
            clauses = PBEnc.equals(
                lits,
                weights,
                degree,
                var_counter,
                encoding=pbenc,
            ).clauses
        else:
            clauses = encode_pbequal(lits, weights, degree, var_counter)

        cnf.extend(clauses)
        var_counter = max(
            var_counter,
            max(abs(_) if _ else 1 for c in clauses for _ in c) if clauses else 1,
        )

    """[[Phase 3]]"""
    # Cross-handling (no crossing bridges)
    edges_list = [(*k, *v) for k, v in pot_edges.items()]
    for i in range(len(edges_list)):
        for j in range(i + 1, len(edges_list)):
            ei, ej = edges_list[i], edges_list[j]
            if edges_cross(ei, ej):
                (vx1, vd1), (vx2, vd2) = edge_vars[ei[:2]], edge_vars[ej[:2]]
                for v1, v2 in [(vx1, vx2), (vx1, vd2), (vd1, vx2), (vd1, vd2)]:
                    cnf.append([-v1, -v2])

    """[[Phase 4]]"""
    # At least one bridge per island => at least n-1 edges
    if use_pysat:
        _ = CardEnc.atleast(
            [x for x in range(1, max_edge_vars_counter)],
            bound=n_islands - 1,
            top_id=var_counter,
            encoding=cardenc,
        )
        # cnf.extend(_)
    else:
        pass

    return cnf, edge_vars, islands, var_counter
