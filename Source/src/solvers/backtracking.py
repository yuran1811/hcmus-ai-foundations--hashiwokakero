import traceback
from collections import Counter

from __types import Grid
from utils import (
    check_hashi,
    encode_hashi,
    extract_solution,
    generate_output,
    validate_solution,
)


def unit_propagate(clauses: list[list[int]], assignment: dict[int, bool]):
    changed = True
    while changed:
        changed = False
        new_clauses: list[list[int]] = []
        for clause in clauses:
            unassigned_lits: list[int] = []
            satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    if (lit > 0 and assignment[var]) or (
                        lit < 0 and not assignment[var]
                    ):
                        satisfied = True
                        break
                else:
                    unassigned_lits.append(lit)

            if satisfied:
                continue

            if not unassigned_lits:
                return None, None  # Conflict

            if len(unassigned_lits) == 1:
                unit_lit = unassigned_lits[0]
                var = abs(unit_lit)
                value = unit_lit > 0
                if var in assignment and assignment[var] != value:
                    return None, None  # Conflict

                if var not in assignment:
                    assignment[var] = value
                    changed = True
            else:
                new_clauses.append(unassigned_lits)
        clauses = new_clauses

    return clauses, assignment


def forward_check(clauses: list[list[int]], assignment: dict[int, bool]):
    for clause in clauses:
        all_assigned = True
        clause_satisfied = False
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                all_assigned = False
            else:
                if (lit > 0 and assignment[var]) or (lit < 0 and not assignment[var]):
                    clause_satisfied = True
                    break
        if all_assigned and not clause_satisfied:
            return False
    return True


def solve_with_backtracking(grid: Grid):
    cnf, edge_vars, islands, _ = encode_hashi(grid, use_pysat=True)
    if not islands or not cnf.clauses:
        return [], []

    variables: list[int] = sorted(
        set(abs(lit) for clause in cnf.clauses for lit in clause)
    )
    var_count = Counter(abs(lit) for clause in cnf.clauses for lit in clause)
    variables.sort(key=lambda v: -var_count[v])

    def backtrack(
        index: int,
        assignment: dict[int, bool] | None,
        clauses: list[list[int]] | None,
        learned_clauses: list[list[int]],
    ) -> dict[int, bool]:
        clauses, assignment = unit_propagate(clauses or [], assignment or {})
        if clauses is None or assignment is None:
            return {}

        if not forward_check(clauses, assignment):
            return {}

        if index == len(variables):
            return assignment

        var = variables[index]
        if var in assignment:
            return backtrack(index + 1, assignment, clauses, learned_clauses)

        for value in [True, False]:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            result = backtrack(
                index + 1, new_assignment, clauses[:], learned_clauses[:]
            )
            if result:
                return result

            # CDCL: Learn a new clause from the conflict.
            conflict_clause: list[int] = []
            for lit in clauses:
                for variable in lit:
                    if abs(variable) in new_assignment:
                        if (variable > 0 and not new_assignment[abs(variable)]) or (
                            variable < 0 and new_assignment[abs(variable)]
                        ):
                            conflict_clause.append(-variable)
            if conflict_clause:
                learned_clauses.append(conflict_clause)
                clauses.append(conflict_clause)

        return {}

    try:
        model_assignment = backtrack(0, {}, cnf.clauses[:], [])
        if model_assignment is None:
            print("No satisfying assignment found.")
            return ""

        model = [var if model_assignment.get(var, False) else -var for var in variables]

        if validate_solution(islands, edge_vars, model):
            sol = extract_solution(model, edge_vars)
            if check_hashi(islands, sol):
                return generate_output(grid, islands, sol)

            # print("Warning: Extracted solution failed final check_hashi.")
        else:
            # print("Validation of the assignment failed.")
            pass
    except KeyboardInterrupt:
        print("\n> Terminating...")
        return ""
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print(traceback.format_exc())
        return ""

    return ""
