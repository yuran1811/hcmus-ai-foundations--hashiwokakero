from pysat.solvers import Glucose42

from __types import Grid
from utils import (
    check_hashi,
    encode_hashi,
    extract_solution,
    generate_output,
    validate_solution,
)


def solve_with_pysat(grid: Grid):
    def solve_hashi():
        for pbenc in range(7):
            for cardenc in range(10):
                try:
                    cnf, edge_vars, islands, _ = encode_hashi(
                        grid, pbenc, cardenc, use_pysat=True
                    )
                    with Glucose42(bootstrap_with=cnf) as solver:
                        # print(f"solve with\n  pbenc: {pbenc}\n  cardenc: {cardenc}")
                        while solver.solve():
                            model = solver.get_model()
                            num_clauses = solver.nof_clauses()
                            if not model or (
                                num_clauses and num_clauses > len(cnf.clauses)
                            ):
                                break

                            if validate_solution(islands, edge_vars, model):
                                return extract_solution(model, edge_vars), islands

                            solver.add_clause([-x for x in model])
                except KeyboardInterrupt:
                    print("> terminating...")
                    return [], []
                except Exception:
                    continue

        return [], []

    sol, islands = solve_hashi()
    if not sol or not check_hashi(islands, sol):
        return ""

    return generate_output(grid, islands, sol)
