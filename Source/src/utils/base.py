import itertools

from pysat.card import EncType as CardEncType
from pysat.formula import CNF
from pysat.pb import EncType as PBEncType
from pysat.pb import PBEnc

from __types import Edge, EdgeExtend, Grid, Incident, Island, PairII
from classes import DSU


def in_bounds(r: int, c: int, nrows: int, ncols: int):
    return 0 <= r < nrows and 0 <= c < ncols


def update_var_counter(var_counter: int, clauses: list[list[int]]):
    return max(
        var_counter,
        max(abs(_) if _ else 1 for c in clauses for _ in c) if clauses else 1,
    )


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


def edge_span(edge: EdgeExtend):
    (_, _, (r1, c1), (r2, c2)) = edge
    return (min(r1, r2), max(r1, r2), min(c1, c2), max(c1, c2))


def edge_orientation(edge: EdgeExtend):
    (_, _, (r1, c1), (r2, c2)) = edge
    if r1 == r2:
        return "h"
    if c1 == c2:
        return "v"
    return "other"


def check_hashi(islands: list[Island], sol: list[tuple[int, int, int]]):
    mst = DSU(len(islands))

    degs = [0] * len(islands)
    for i, j, w in sol:
        mst.merge(i, j)
        degs[i] += w
        degs[j] += w

    root = mst.root(0)
    for i in range(len(islands)):
        if mst.root(i) != root or degs[i] != islands[i][3]:
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


def comb(n: int, k: int, lits: list[int]):
    clauses: set[frozenset[int]] = set()
    for state in range(2**n):
        sum = 0
        true_pos = []
        for i in range(n):
            x = (state >> i) & 1
            w = 1 + (i & 1)
            sum += w * x

            if x:
                true_pos.append(i)

        valid = True
        for i in range(0, len(true_pos) - 1):
            if true_pos[i + 1] - true_pos[i] == 1 and true_pos[i] & 1 == 0:
                valid = False
                break

        if valid and sum == k:
            x = ""
            for i in range(n):
                x += str((state >> i) & 1)
            clauses.add(frozenset([lits[_] for _ in true_pos]))

    return [list(x) for x in list(clauses)]


def dnf_to_cnf(dnf: list[list[int]], top_id: int):
    # Tseytin transformation
    cnf: list[list[int]] = []

    for c in dnf:
        # This is equivalent to: (¬new_var ∨ lit1) ∧ (¬new_var ∨ lit2) ∧ ... ∧ (¬new_var ∨ litn) ∧ (new_var ∨ ¬lit1 ∨ ¬lit2 ∨ ... ∨ ¬litn)
        for _ in c:
            cnf.append([-top_id, _])
        cnf.append([top_id] + [-_ for _ in c])

        top_id += 1

    return cnf


def dnf_to_cnf_minimized(dnf: list[list[int]], top_id: int):
    cnf: list[list[int]] = dnf_to_cnf(dnf, top_id)
    aux_vars = list(range(top_id, top_id + len(dnf)))
    aux_cnf = dnf_to_cnf([aux_vars], aux_vars[-1] + 1)
    cnf.extend([[-lit for lit in c] for c in aux_cnf])

    return cnf


# equiv
def vars_in_dnf(dnf: list[list[int]]):
    return set(abs(_) for clause in dnf for _ in clause)


def evaluate_dnf(dnf: list[list[int]], assignment: dict[int, bool]):
    # A DNF formula is true if at least one clause is true.
    for clause in dnf:
        # Each clause (a conjunction of literals) is true if all its literals are true.
        if all(
            (assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)])
            for lit in clause
        ):
            return True
    return False


def assignment_to_clause(assignment: dict[int, bool]):
    clause: list[int] = []
    for var, value in assignment.items():
        # For the clause to be false, every literal must be false.
        # So if var=True in the assignment, then literal -var is false only if var is True.
        # Thus the clause is: (¬var if value True, else var)
        clause.append(-var if value else var)
    return clause


def subsumption_minimization(clauses):
    """
    Remove any clause that is subsumed by another.
    That is, if clause A is a superset of clause B, then A is redundant.
    Both A and B are lists of literals.
    """
    minimized = []
    for i, A in enumerate(clauses):
        Aset = set(A)
        subsumed = False
        for j, B in enumerate(clauses):
            if i != j:
                Bset = set(B)
                if Aset.issuperset(Bset):
                    # If A is a superset of B, then A is redundant.
                    subsumed = True
                    break
        if not subsumed:
            minimized.append(sorted(A))
    # Remove duplicates and sort clauses for consistency
    unique = []
    for cl in minimized:
        if cl not in unique:
            unique.append(cl)
    return unique


def dnf_to_cnf_equiv(dnf):
    """
    Convert a DNF (list of lists of literals) to a CNF that is logically equivalent.
    This is done by:
      1. Determining the set of all variables.
      2. Enumerating all assignments that make the DNF false.
      3. For each falsifying assignment, generate a clause that "blocks" that assignment.
         (A clause is false exactly on that assignment.)
      4. Minimize the resulting set of clauses by subsumption elimination.
    Returns a list of CNF clauses (each clause itself a list of literals).
    """
    variables = sorted(vars_in_dnf(dnf))
    assignments = list(itertools.product([False, True], repeat=len(variables)))
    blocking_clauses = []
    for values in assignments:
        assign = dict(zip(variables, values))
        # If the DNF evaluates to False on this assignment, then the CNF must block it.
        if not evaluate_dnf(dnf, assign):
            clause = assignment_to_clause(assign)
            blocking_clauses.append(clause)

    # Perform a simple subsumption elimination to remove redundant clauses.
    cnf = subsumption_minimization(blocking_clauses)
    return cnf


# equiv


def encode_degree_constraints(
    islands: list[Island],
    island_incident: Incident,
    edge_vars: dict[PairII, tuple[int, int]],
    top_id: int,
):
    clauses: set[frozenset[int]] = set()
    var_counter = top_id

    for island in islands:
        idx, r, c, degree = island
        adjacents = island_incident.get(idx, [])

        # Rule 1: Single adjacent edge must match degree
        if len(adjacents) == 2:
            adj_id, _ = adjacents[0]
            edge = (min(idx, adj_id), max(idx, adj_id))
            if edge not in edge_vars:
                continue

            s_var, d_var = edge_vars[edge]
            if degree == 1:
                clauses.add(frozenset([s_var]))
                clauses.add(frozenset([-d_var]))
            elif degree == 2:
                clauses.add(frozenset([d_var]))
                clauses.add(frozenset([-s_var]))
            else:
                clauses.add(frozenset([s_var, d_var]))
                clauses.add(frozenset([-s_var, -d_var]))

        # Rule 2: Degree 1 islands must connect to islands with degree >=2
        elif degree == 1:
            for adj_id, _ in adjacents:
                edge = (min(idx, adj_id), max(idx, adj_id))
                s_var, d_var = edge_vars[edge]
                clauses.add(frozenset([-d_var]))

                if islands[adj_id][3] == 1:
                    clauses.add(frozenset([-s_var]))

        # Rule 3: Degree 2 do not connect to degree 2 with double
        elif degree == 2:
            for adj_id, _ in adjacents:
                edge = (min(idx, adj_id), max(idx, adj_id))
                s_var, d_var = edge_vars[edge]

                if islands[adj_id][3] == 2:
                    clauses.add(frozenset([-d_var]))

        # Rule 4: Degree 8 requires all edges to have double bridges
        elif degree == 8:
            for adj_id, _ in adjacents:
                edge = (min(idx, adj_id), max(idx, adj_id))
                s_var, d_var = edge_vars[edge]
                clauses.add(frozenset([d_var]))
                clauses.add(frozenset([-s_var]))

        # Rule 5: Degree 7 needs at least one bridge per direction
        elif degree == 7:
            for adj_id, _ in adjacents:
                edge = (min(idx, adj_id), max(idx, adj_id))
                s_var, d_var = edge_vars[edge]
                clauses.add(frozenset([s_var, d_var]))  # At least one bridge

        # Rule 6: Degree 6 with three adjacent edges
        elif degree == 6 and len(adjacents) == 3:
            for adj_id, _ in adjacents:
                edge = (min(idx, adj_id), max(idx, adj_id))
                s_var, d_var = edge_vars[edge]
                clauses.add(frozenset([d_var]))
                clauses.add(frozenset([-s_var]))

        # General case: Sum of bridges equals degree (simplified)
        else:
            adjacents = [adj for adj in adjacents if islands[adj[0]][3]]
            dnf = comb(
                len(adjacents),
                degree,
                [v for _, v in adjacents],
            )
            # cnf = dnf_to_cnf_equiv(dnf)
            cnf = dnf_to_cnf_minimized(dnf, var_counter)

            var_counter = update_var_counter(var_counter, cnf)
            cnf_set = set(frozenset(sorted(c)) for c in cnf)
            for c in cnf_set:
                cnf.append(list(c))
            for c in cnf:
                clauses.add(frozenset(c))

            # print(
            #     f"island - {island[0]},",
            #     len(dnf),
            #     len(cnf_set),
            #     "\n",
            #     dnf,
            #     "\n",
            #     [list(s) for s in list(cnf_set)],
            #     "\n",
            # )

    return [list(_) for _ in list(clauses)]


def encode_pbequal(lits: list[int], weights: list[int], k: int, top_id: int):
    def next_var():
        nonlocal top_id
        top_id += 1
        return top_id

    clauses: list[list[int]] = []

    n = len(lits)
    if n == 0:
        return [[1], [-1]] if k != 0 else []

    s = [{} for _ in range(n + 1)]
    s[0][0] = next_var()
    clauses.append([s[0][0]])

    for i in range(1, n + 1):
        x_i = lits[i - 1]
        a_i = weights[i - 1]
        s_prev = s[i - 1]
        s_curr = {}

        if a_i == 0:
            for prev_sum in s_prev:
                aux_prev = s_prev[prev_sum]
                new_sum = prev_sum
                if new_sum not in s_curr:
                    s_curr[new_sum] = next_var()
                aux_new = s_curr[new_sum]
                clauses.append([-aux_prev, aux_new])
        else:
            for prev_sum in s_prev:
                aux_prev = s_prev[prev_sum]
                # Case 1: x_i is False
                if prev_sum not in s_curr:
                    s_curr[prev_sum] = next_var()
                aux_false = s_curr[prev_sum]
                clauses.append([-aux_prev, x_i, aux_false])
                # Case 2: x_i is True
                new_sum = prev_sum + a_i
                if new_sum not in s_curr:
                    s_curr[new_sum] = next_var()
                aux_true = s_curr[new_sum]
                clauses.append([-aux_prev, -x_i, aux_true])

        # Add mutual exclusion clauses for s_curr
        sums = sorted(s_curr.keys())
        for idx in range(len(sums)):
            for jdx in range(idx + 1, len(sums)):
                clauses.append([-s_curr[sums[idx]], -s_curr[sums[jdx]]])

        s[i] = s_curr

    # Final constraint
    if k not in s[n]:
        return [[1], [-1]]  # Unsatisfiable

    clauses.append([s[n][k]])

    return clauses


def encode_hashi(
    grid: Grid,
    pbenc: int = PBEncType.bdd,
    cardenc: int = CardEncType.mtotalizer,
    *,
    use_pysat: bool = False,
    use_self_pbenc: bool = False,
) -> tuple[CNF, dict[PairII, PairII], list[Island], int]:
    islands = get_islands(grid)
    n_islands = len(islands)
    island_incident: Incident = {idx: [] for idx in range(n_islands)}

    pot_edges = potential_edges(grid, islands)
    edges_list = [(*k, *v) for k, v in pot_edges.items()]
    edge_vars: dict[PairII, PairII] = {}

    cnf = CNF()
    var_counter = 1

    """[[Phase 1]]"""
    # Add variables for edges (vx: single bridge, vd: double bridge)
    for edge in pot_edges:
        edge_vars[edge] = (var_counter, var_counter + 1)
        var_counter += 2

    # At most one bridge type per edge (can be 0 when not using the edge)
    for vx, vd in edge_vars.values():
        cnf.append([-vx, -vd])

    """[[Phase 2]]"""
    # Populate incident edges (generate the adj list for each island)
    for (i, j), (vx, vd) in edge_vars.items():
        island_incident[i].extend([(j, vx), (j, vd)])
        island_incident[j].extend([(i, vx), (i, vd)])

    # Island degree rules
    deg_rules: set[frozenset[int]] = set()
    for island in islands:
        idx, _, _, degree = island
        adjacents = island_incident.get(idx, [])

        # Rule 1: Single adjacent edge must match degree
        if len(adjacents) == 2:
            adj_id, _ = adjacents[0]
            edge = (min(idx, adj_id), max(idx, adj_id))
            if edge not in edge_vars:
                continue

            s_var, d_var = edge_vars[edge]
            if degree == 1:
                deg_rules.add(frozenset([s_var]))
                deg_rules.add(frozenset([-d_var]))
            elif degree == 2:
                deg_rules.add(frozenset([d_var]))
                deg_rules.add(frozenset([-s_var]))
            else:
                deg_rules.add(frozenset([s_var, d_var]))
                deg_rules.add(frozenset([-s_var, -d_var]))

        # Rule 2: Degree 1 islands must connect to islands with degree >=2
        elif degree == 1:
            for adj_id, _ in adjacents:
                edge = (min(idx, adj_id), max(idx, adj_id))
                s_var, d_var = edge_vars[edge]
                deg_rules.add(frozenset([-d_var]))

                if islands[adj_id][3] == 1:
                    deg_rules.add(frozenset([-s_var]))

        # Rule 3: Degree 2 do not connect to degree 2 with double
        elif degree == 2:
            for adj_id, _ in adjacents:
                edge = (min(idx, adj_id), max(idx, adj_id))
                s_var, d_var = edge_vars[edge]

                if islands[adj_id][3] == 2:
                    deg_rules.add(frozenset([-d_var]))

        # Rule 4: Degree 8 requires all edges to have double bridges
        elif degree == 8:
            for adj_id, _ in adjacents:
                edge = (min(idx, adj_id), max(idx, adj_id))
                s_var, d_var = edge_vars[edge]
                deg_rules.add(frozenset([d_var]))
                deg_rules.add(frozenset([-s_var]))

        # Rule 5: Degree 7 needs at least one bridge per direction
        elif degree == 7:
            for adj_id, _ in adjacents:
                edge = (min(idx, adj_id), max(idx, adj_id))
                s_var, d_var = edge_vars[edge]
                deg_rules.add(frozenset([s_var, d_var]))  # At least one bridge

        # Rule 6: Degree 6 with three adjacent edges
        elif degree == 6 and len(adjacents) == 3:
            for adj_id, _ in adjacents:
                edge = (min(idx, adj_id), max(idx, adj_id))
                s_var, d_var = edge_vars[edge]
                deg_rules.add(frozenset([d_var]))
                deg_rules.add(frozenset([-s_var]))
    for _ in deg_rules:
        cnf.append(list(_))

    # Degree constraints
    if use_pysat:
        for idx, _, _, degree in islands:
            lits = [v for _, v in island_incident[idx]]
            weights = [[2, 1][x & 1] for x in lits]
            if not lits and degree:
                print(f"[unsat]: no edges for island {idx}")
                cnf.append([])
                continue

            clauses = (
                PBEnc.equals(
                    lits,
                    weights,
                    degree,
                    var_counter,
                    encoding=pbenc,
                ).clauses
                if not use_self_pbenc
                else encode_pbequal(
                    lits,
                    weights,
                    degree,
                    var_counter,
                )
            )
            cnf.extend(clauses)
            var_counter = update_var_counter(var_counter, clauses)
    else:
        clauses = encode_degree_constraints(
            islands, island_incident, edge_vars, var_counter
        )
        cnf.extend(clauses)
        var_counter = update_var_counter(var_counter, clauses)

    """[[Phase 3]]"""
    # Cross-handling (no crossing bridges)
    for i in range(len(edges_list) - 1):
        for j in range(i + 1, len(edges_list)):
            ei, ej = edges_list[i], edges_list[j]
            if edges_cross(ei, ej):
                (vx1, vd1), (vx2, vd2) = edge_vars[ei[:2]], edge_vars[ej[:2]]
                for v1, v2 in [(vx1, vx2), (vx1, vd2), (vd1, vx2), (vd1, vd2)]:
                    cnf.append([-v1, -v2])

    """[[Phase 4]]"""
    # Connectivity constraints
    if use_pysat:
        # At least one bridge per island => at least n-1 edges
        # from pysat.card import CardEnc
        # cnf.extend(
        #     CardEnc.atleast(
        #         [x + 1 for x in range(2 * len(islands))],
        #         bound=n_islands - 1,
        #         top_id=var_counter,
        #         encoding=cardenc,
        #     )
        # )
        pass
    else:
        pass

    return cnf, edge_vars, islands, var_counter
