import copy
import traceback

from __types import Grid
from utils import (
    check_hashi,
    encode_hashi,
    extract_solution,
    generate_output,
    validate_solution,
)


def dpll(clauses, assignment):
    """
    A simplified DPLL algorithm.

    Parameters:
      clauses: list of clauses (each clause is a list of ints)
      assignment: dict mapping variable -> True/False (partial assignment)

    Returns:
      A complete satisfying assignment (dict) or None if unsat.
    """
    # 1. Unit Propagation.
    new_clauses, new_assignment = unit_propagate(clauses, assignment)
    if new_clauses is None:
        return None  # Conflict found.

    # 2. Pure Literal Elimination.
    pure = {}
    for clause in new_clauses:
        for lit in clause:
            var = abs(lit)
            if var in new_assignment:
                continue
            # If first time seeing var, record its polarity.
            if var not in pure:
                pure[var] = lit > 0
            else:
                # If the polarity differs, mark as non-pure.
                if pure[var] != (lit > 0):
                    pure[var] = None
    # Assign pure literals.
    for var, val in pure.items():
        if val is not None and var not in new_assignment:
            new_assignment[var] = val

    # 3. Check if every clause is satisfied.
    satisfied_all = True
    for clause in new_clauses:
        if not any(
            (lit > 0 and new_assignment.get(abs(lit), False))
            or (lit < 0 and not new_assignment.get(abs(lit), False))
            for lit in clause
        ):
            satisfied_all = False
            break
    if satisfied_all:
        return new_assignment

    # 4. Check for conflict: any clause is fully assigned and unsatisfied.
    for clause in new_clauses:
        if all(abs(lit) in new_assignment for lit in clause):
            if not any(
                (lit > 0 and new_assignment[abs(lit)])
                or (lit < 0 and not new_assignment[abs(lit)])
                for lit in clause
            ):
                return None

    # 5. Choose an unassigned variable.
    all_vars = set(abs(lit) for clause in new_clauses for lit in clause)
    unassigned = list(all_vars - set(new_assignment.keys()))
    if not unassigned:
        return new_assignment
    # Simple heuristic: choose the smallest unassigned variable.
    chosen = min(unassigned)

    # 6. Recurse with chosen variable assigned True and then False.
    for value in [True, False]:
        assignment_copy = new_assignment.copy()
        assignment_copy[chosen] = value
        result = dpll(new_clauses, assignment_copy)
        if result is not None:
            return result
    return None


def unit_propagate(clauses, assignment):
    """
    Performs unit propagation on a copy of the clause list and assignment.
    Returns (new_clauses, new_assignment) or (None, None) if a conflict is detected.
    """
    changed = True
    new_assignment = assignment.copy()
    new_clauses = copy.deepcopy(clauses)

    while changed:
        changed = False
        updated_clauses = []
        for clause in new_clauses:
            unassigned_lits = []
            satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in new_assignment:
                    if (lit > 0 and new_assignment[var]) or (
                        lit < 0 and not new_assignment[var]
                    ):
                        satisfied = True
                        break
                else:
                    unassigned_lits.append(lit)
            if satisfied:
                continue
            if not unassigned_lits:
                return None, None  # Conflict: clause unsatisfied.
            if len(unassigned_lits) == 1:
                # Unit clause: force assignment.
                unit_lit = unassigned_lits[0]
                var = abs(unit_lit)
                value = unit_lit > 0
                if var in new_assignment and new_assignment[var] != value:
                    return None, None  # Conflict.
                if var not in new_assignment:
                    new_assignment[var] = value
                    changed = True
            updated_clauses.append(unassigned_lits)
        new_clauses = updated_clauses
    return new_clauses, new_assignment


def solve_with_backtracking(grid: Grid):
    """
    Solves the Hashiwokakero puzzle by repeatedly calling the DPLL solver
    until a fully satisfied (including connectivity) solution is found.
    """
    try:
        cnf_wrapper, edge_vars, islands, variable_map = encode_hashi(
            grid, use_pysat=True
        )
        if not islands:
            return ([], []) if check_hashi([], []) else ""
        if not hasattr(cnf_wrapper, "clauses") or not cnf_wrapper.clauses:
            # print("Error: CNF object does not contain clauses.")
            return ""

        clauses = [list(clause) for clause in cnf_wrapper.clauses]
        all_vars = set()
        for clause in clauses:
            for lit in clause:
                all_vars.add(abs(lit))
        ordered_vars = sorted(list(all_vars))  # Ensure consistent ordering

        while True:
            model_assignment = dpll(clauses, {})
            if model_assignment is None:
                # print("No satisfying connected assignment found.")
                return ""

            model = [
                var if model_assignment.get(var, False) else -var
                for var in ordered_vars
            ]

            if validate_solution(islands, edge_vars, model):
                hashi_solution = extract_solution(model, edge_vars)
                if check_hashi(islands, hashi_solution):
                    return generate_output(grid, islands, hashi_solution)
                else:
                    # Add a blocking clause to prevent finding the same assignment again
                    blocking_clause = [-lit for lit in model]
                    clauses.append(blocking_clause)
            else:
                blocking_clause = [-lit for lit in model]
                clauses.append(blocking_clause)

    except KeyboardInterrupt:
        print("\n> terminating...")
        return ""
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        traceback.print_exc()
        return ""
    return ""
