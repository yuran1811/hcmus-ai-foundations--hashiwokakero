from __types import Grid
from utils import (
    check_hashi,
    encode_hashi,
    extract_solution,
    generate_output,
    validate_solution,
)
import traceback

def solve_with_backtracking(grid: Grid):
    """
    Solves the Hashiwokakero puzzle by encoding it into CNF using encode_hashi,
    then using backtracking (a recursive search) to find a satisfying assignment.
    
    Once an assignment is found, the solution is extracted and validated.
    """

    def solve_hashi_backtrack():
        try:
            # Encode the puzzle into CNF.
            # use_pysat=False means we use our own CNF encoding rather than PySAT's encoders.
            cnf, edge_vars, islands, _ = encode_hashi(grid, use_pysat=True)

            if not islands:
                # No islands means there's nothing to solve.
                if check_hashi([], []):
                    return [], []
                else:
                    return [], []

            if not hasattr(cnf, 'clauses') or not cnf.clauses:
                print("Error: CNF object does not contain clauses.")
                return [], []

            # Collect all unique variables used in the CNF.
            variables = sorted(set(abs(lit) for clause in cnf.clauses for lit in clause))
            print(f"Total unique variables in clauses: {len(variables)}")
            print(f"Total clauses: {len(cnf.clauses)}")
            num_vars = len(variables)

            # Recursive backtracking function.
            def backtrack(index, assignment):
                # If we've assigned all variables, check if every clause is satisfied.
                if index == len(variables):
                    for clause in cnf.clauses:
                        # Clause is satisfied if at least one literal evaluates True.
                        if not any((lit > 0 and assignment[abs(lit)]) or (lit < 0 and not assignment[abs(lit)])
                                   for lit in clause):
                            return None  # A clause is unsatisfied.
                    return assignment

                var = variables[index]
                # Try both True and False assignments for the current variable.
                for value in [True, False]:
                    assignment[var] = value

                    # Early conflict detection: check all clauses that are fully assigned.
                    conflict = False
                    for clause in cnf.clauses:
                        # Determine if all literals in the clause have an assignment.
                        all_assigned = True
                        clause_satisfied = False
                        for lit in clause:
                            v = abs(lit)
                            if v not in assignment:
                                all_assigned = False
                                break
                            else:
                                if (lit > 0 and assignment[v]) or (lit < 0 and not assignment[v]):
                                    clause_satisfied = True
                                    break
                        if all_assigned and not clause_satisfied:
                            conflict = True
                            break

                    if not conflict:
                        result = backtrack(index + 1, assignment)
                        if result is not None:
                            return result

                # Backtrack: remove assignment for this variable.
                if var in assignment:
                    del assignment[var]
                return None

            model_assignment = backtrack(0, {})
            if model_assignment is None:
                print("No satisfying assignment found.")
                return [], []

            # Build the model list: if variable is True, include it as positive; else negative.
            model = [var if model_assignment.get(var, False) else -var for var in variables]

            # Validate the assignment using your utility functions.
            if validate_solution(islands, edge_vars, model):
                print("Satisfying assignment passed validation.")
                hashi_solution = extract_solution(model, edge_vars)
                if check_hashi(islands, hashi_solution):
                    print("Solution extracted and passed final check_hashi.")
                    return hashi_solution, islands
                else:
                    print("Warning: Solution failed final check_hashi despite validation.")
            else:
                print("Validation of the assignment failed.")

        except KeyboardInterrupt:
            print("\n> Terminating...")
            return [], []
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print(traceback.format_exc())
            return [], []

        return [], []

    sol, islands = solve_hashi_backtrack()

    if not sol or not islands or not check_hashi(islands, sol):
        print("Final check failed or no solution found.")
        return ""

    print("Generating final output.")
    return generate_output(grid, islands, sol)

