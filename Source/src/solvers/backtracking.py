from __types import Grid
from utils import encode_hashi


def solve_with_backtracking(grid: Grid):
    cnf, _, _, var_counter = encode_hashi(grid)

    variables = list(range(1, var_counter))
    assignment = {_: False for _ in variables}
    clause_list = [tuple(_) for _ in cnf.clauses]  # Convert clauses to tuples

    # Precompute for each variable the clauses it appears in
    var_to_clauses = {_: [] for _ in variables}
    for idx, clause in enumerate(clause_list):
        for lit in clause:
            var = abs(lit)
            var_to_clauses[var].append(idx)

    # Pure literal elimination
    pure = {}
    for var in variables:
        pos = any(
            lit > 0 for clause in clause_list for lit in clause if abs(lit) == var
        )
        neg = any(
            lit < 0 for clause in clause_list for lit in clause if abs(lit) == var
        )

        if pos and not neg:
            pure[var] = True
        elif neg and not pos:
            pure[var] = False
    for var, val in pure.items():
        assignment[var] = val

    # Remove satisfied clauses and update clause_list
    new_clauses = []
    for clause in clause_list:
        clause_satisfied = False
        new_clause = []
        for lit in clause:
            var = abs(lit)
            if assignment[var] is not None:
                if (lit > 0 and assignment[var]) or (lit < 0 and not assignment[var]):
                    clause_satisfied = True
                    break
            else:
                new_clause.append(lit)
        if not clause_satisfied:
            new_clauses.append(new_clause)
    clause_list = new_clauses

    # Check for empty clause (unsatisfiable)
    if any(len(clause) == 0 for clause in clause_list):
        return None

    # Heuristic: Variables in remaining clauses sorted by frequency
    freq = {var: 0 for var in variables if assignment[var] is None}
    for clause in clause_list:
        for lit in clause:
            var = abs(lit)
            if var in freq:
                freq[var] += 1
    remaining_vars = sorted(freq.keys(), key=lambda x: (-freq[x], x))

    def unit_propagate(assignment):
        new_assignments = []
        while True:
            unit_found = False
            for clause in clause_list:
                if not clause:
                    return False  # Empty clause found
                unassigned = []
                clause_satisfied = False
                for lit in clause:
                    var = abs(lit)
                    val = assignment[var]
                    if val is not None:
                        if (lit > 0 and val) or (lit < 0 and not val):
                            clause_satisfied = True
                            break
                    else:
                        unassigned.append(lit)
                if clause_satisfied:
                    continue
                if len(unassigned) == 0:
                    return False  # Conflict
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    var = abs(lit)
                    required = lit > 0
                    if assignment[var] is None:
                        assignment[var] = required
                        new_assignments.append(var)
                        unit_found = True
                    elif assignment[var] != required:
                        return False  # Conflict
            if not unit_found:
                break
        return new_assignments

    def backtrack(index):
        if index >= len(remaining_vars):
            return {k: v for k, v in assignment.items() if v is not None}

        var = remaining_vars[index]
        if assignment[var] is not None:
            return backtrack(index + 1)

        for value in [True, False]:
            original_assignment = assignment.copy()
            assignment[var] = value
            new_assignments = unit_propagate(assignment.copy())
            if new_assignments is False:
                assignment.update(original_assignment)
                continue

            result = backtrack(index + 1)
            if result is not None:
                return result
            # Undo assignments
            assignment.update(original_assignment)

        return None

    # Check if initial assignment already caused conflict
    if any(not len(clause) for clause in clause_list):
        return None

    backtrack(0)

    model = [k for k, v in assignment.items() if v]
    if not model:
        print("> unsolvable.")
        return ""

    return ""
