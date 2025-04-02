from __types import Grid
from utils import (
    check_hashi,
    encode_hashi,
    extract_solution,
    generate_output,
    validate_solution,
)
import itertools
import traceback


def solve_with_bruteforce(grid: Grid):
    """
    Giải Hashi bằng cách encode thành CNF (một lần) và giải CNF bằng brute-force,
    dựa trên code do người dùng cung cấp.
    """
    def solve_hashi():
        try:
            cnf, edge_vars, islands, _ = encode_hashi(grid, use_pysat=True)

            if not islands:
                if check_hashi([], []):
                    return [], []  
                else:
                    return [], []  

            if not hasattr(cnf, 'clauses') or not cnf.clauses:
                print("Error: CNF object does not contain clauses.")
                return [], []

            variables = sorted(set(abs(lit) for clause in cnf.clauses for lit in clause))

            print(f"Total unique variables in clauses: {len(variables)}")
            print(f"Total clauses: {len(cnf.clauses)}")

            total_combinations = 2 ** len(variables)
            print(f"Total combinations to check: {total_combinations:,}")

            if len(variables) > 22:
                print(f"Warning: {len(variables)} variables ({total_combinations:,} combinations) is likely too large for brute-force.")

            counter = 0
            for assignment_tuple in itertools.product([False, True], repeat=len(variables)):
                counter += 1

                if counter % 100000 == 0 or counter == total_combinations:
                    print(f"\rChecked {counter:,}/{total_combinations:,} assignments...", end="")

                assignment = dict(zip(variables, assignment_tuple))

                satisfied = all(
                    any(
                        (lit > 0 and assignment.get(abs(lit), False)) or
                        (lit < 0 and not assignment.get(abs(lit), False))
                        for lit in clause
                    )
                    for clause in cnf.clauses
                )

                if satisfied:
                    print(f"\nFound a satisfying assignment after {counter:,} checks.")

                    model = [var if assignment.get(var, False) else -var for var in variables]

                    if validate_solution(islands, edge_vars, model):
                        print("Satisfying assignment passed validation.")
                        hashi_solution = extract_solution(model, edge_vars)

                        if check_hashi(islands, hashi_solution):
                            print("Solution extracted and passed final check_hashi.")
                            return hashi_solution, islands
                        else:
                            print("Warning: Solution failed final check_hashi despite satisfying CNF and validation.")

            print(f"\nChecked all {total_combinations:,} assignments, no valid solution found.")

        except KeyboardInterrupt:
            print("\n> Terminating...")
            return [], []
        except AttributeError:
            print("\nError: encode_hashi might not have returned a CNF object with '.clauses'. Check return type.")
            return [], []
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print(traceback.format_exc())
            return [], []

        return [], []

    sol, islands = solve_hashi()

    if not sol or not islands or not check_hashi(islands, sol):
        print("Final check failed or no solution found.")
        return ""

    print("Generating final output.")
    return generate_output(grid, islands, sol)