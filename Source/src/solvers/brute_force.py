import itertools
import traceback

from __types import Grid
from utils import (
    check_hashi,
    encode_hashi,
    extract_solution,
    generate_output,
    validate_solution,
)


def solve_with_bruteforce(grid: Grid):
    """
    Solve Hashi by encoding it into a CNF and then solving the CNF using brute-force,
    based on the provided code. This improved version uses a precomputed variable-to-index
    mapping to avoid recreating a dictionary for each assignment.
    """

    def solve_hashi():
        try:
            cnf, edge_vars, islands, _ = encode_hashi(grid, use_pysat=True)
            if not islands or not cnf.clauses:
                return [], []

            # Retrieve unique variables from the CNF and sort them.
            variables = sorted(
                set(abs(lit) for clause in cnf.clauses for lit in clause)
            )
            # Precompute a mapping from variable to its index in the tuple.
            var_to_index = {var: idx for idx, var in enumerate(variables)}

            total_combinations = 2 ** len(variables)
            # print(f"Total unique variables in clauses: {len(variables)}")
            # print(f"Total clauses: {len(cnf.clauses)}")
            # print(f"Total combinations to check: {total_combinations:,}")

            if len(variables) > 22:
                print(
                    f"[warning] - {len(variables)} variables ({total_combinations:,} combinations) is likely too large for brute-force."
                )

            counter = 0
            # Iterate over each possible assignment represented as a tuple of booleans.
            for assignment_tuple in itertools.product(
                [False, True], repeat=len(variables)
            ):
                counter += 1

                if counter % 100000 == 0 or counter == total_combinations:
                    # print(
                    #     f"\rChecked {counter:,}/{total_combinations:,} assignments...",
                    #     end="",
                    # )
                    pass

                satisfied = True
                # Evaluate each clause using the assignment tuple and the precomputed mapping.
                for clause in cnf.clauses:
                    clause_satisfied = False
                    for lit in clause:
                        var = abs(lit)
                        # Lookup the boolean value for the variable.
                        val = assignment_tuple[var_to_index[var]]
                        if (lit > 0 and val) or (lit < 0 and not val):
                            clause_satisfied = True
                            break
                    if not clause_satisfied:
                        satisfied = False
                        break

                if satisfied:
                    # print(f"\nFound a satisfying assignment after {counter:,} checks.")
                    # Construct the model as a list using the assignment tuple.
                    model = [
                        var if assignment_tuple[var_to_index[var]] else -var
                        for var in variables
                    ]

                    if validate_solution(islands, edge_vars, model):
                        # print("Satisfying assignment passed validation.")
                        hashi_solution = extract_solution(model, edge_vars)
                        if check_hashi(islands, hashi_solution):
                            # print("Solution extracted and passed final check_hashi.")
                            return hashi_solution, islands
                        else:
                            # print(
                            #     "[warning] - Solution failed final check_hashi despite satisfying CNF and validation."
                            # )
                            pass

            # print(
            #     f"\nChecked all {total_combinations:,} assignments, no valid solution found."
            # )

        except KeyboardInterrupt:
            print("\n> terminating...")
            return [], []
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print(traceback.format_exc())
            return [], []

        return [], []

    sol, islands = solve_hashi()
    if not sol or not islands or not check_hashi(islands, sol):
        return ""

    return generate_output(grid, islands, sol)
