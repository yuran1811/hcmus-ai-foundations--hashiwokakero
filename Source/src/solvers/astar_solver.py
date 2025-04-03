from __types import Grid
from utils import (
    check_hashi,
    encode_hashi,
    extract_solution,
    generate_output,
    validate_solution,
)
import heapq
import traceback
from collections import defaultdict
import copy

def compute_heuristic(cnf, assignment, var_index_map):
    h = 0
    for clause in cnf.clauses:
        all_assigned = True
        clause_satisfied = False
        for lit in clause:
            var = abs(lit)
            idx = var_index_map[var]
            val = assignment[idx]
            if val is None:
                all_assigned = False
                break
            else:
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_satisfied = True
                    break
        if all_assigned and not clause_satisfied:
            h += 1
    return h

def clause_status(clause, assignment, var_index_map):
    unassigned = []
    for lit in clause:
        var = abs(lit)
        idx = var_index_map[var]
        val = assignment[idx]
        if val is None:
            unassigned.append((var, lit))
        else:
            if (lit > 0 and val) or (lit < 0 and not val):
                return 'satisfied'
    if not unassigned:
        return 'conflict'
    return unassigned

def unit_propagate(assignment, cnf, var_index_map):
    changed = True
    while changed:
        changed = False
        for clause in cnf.clauses:
            status = clause_status(clause, assignment, var_index_map)
            if status == 'conflict':
                return None
            elif isinstance(status, list) and len(status) == 1:
                # unit clause: force the only unassigned literal.
                var, lit = status[0]
                idx = var_index_map[var]
                # Determine forced value.
                forced_value = (lit > 0)
                if assignment[idx] is None:
                    assignment[idx] = forced_value
                    changed = True
    return assignment

def is_complete_assignment(assignment):
    return all(val is not None for val in assignment)

def check_full_assignment(cnf, assignment, var_index_map):
    for clause in cnf.clauses:
        clause_satisfied = False
        for lit in clause:
            var = abs(lit)
            idx = var_index_map[var]
            val = assignment[idx]
            if (lit > 0 and val) or (lit < 0 and not val):
                clause_satisfied = True
                break
        if not clause_satisfied:
            return False
    return True

def expand_state(cnf, assignment, level, variables, var_index_map, var_to_clauses):
    next_states = []
    current_var = variables[level]
    idx = var_index_map[current_var]
    for value in [False, True]:
        new_assignment = assignment[:]  # shallow copy of the list
        new_assignment[idx] = value
        # Run unit propagation
        propagated = unit_propagate(new_assignment, cnf, var_index_map)
        if propagated is not None:
            next_states.append((level + 1, propagated))
    return next_states

def solve_with_astar(grid: Grid):
    try:
        cnf, edge_vars, islands, _ = encode_hashi(grid, use_pysat=True)

        if not islands:
            if check_hashi([], []):
                return generate_output(grid, [], [])
            else:
                return ""

        if not hasattr(cnf, 'clauses') or not cnf.clauses:
            print("Error: CNF object does not contain clauses.")
            return ""

        var_freq = {}
        for clause in cnf.clauses:
            for lit in clause:
                var = abs(lit)
                var_freq[var] = var_freq.get(var, 0) + 1

        variables = sorted(var_freq.keys(), key=lambda v: -var_freq[v])
        print(f"Total unique variables in clauses: {len(variables)}")
        print(f"Total clauses: {len(cnf.clauses)}")
    

        var_index_map = {var: i for i, var in enumerate(variables)}

        var_to_clauses = defaultdict(list)
        for clause in cnf.clauses:
            for lit in clause:
                var_to_clauses[abs(lit)].append(clause)

        initial_assignment = [None] * len(variables)
        initial_assignment = unit_propagate(initial_assignment, cnf, var_index_map)
        if initial_assignment is None:
            print("Initial unit propagation found a conflict.")
            return ""

        initial_level = sum(1 for x in initial_assignment if x is not None)
        counter = 0  # tie-breaker counter for heap ordering
        initial_f = initial_level + compute_heuristic(cnf, initial_assignment, var_index_map)
        open_list = []
        heapq.heappush(open_list, (initial_f, initial_level, counter, initial_assignment))
        nodes_expanded = 0

        while open_list:
            f, level, _, assignment = heapq.heappop(open_list)
            nodes_expanded += 1

            if is_complete_assignment(assignment):
                if check_full_assignment(cnf, assignment, var_index_map):
                    print(f"\nFound a satisfying complete assignment after expanding {nodes_expanded:,} nodes.")
                    model = [var if assignment[var_index_map[var]] else -var for var in variables]
                    if validate_solution(islands, edge_vars, model):
                        print("Satisfying assignment passed validation.")
                        hashi_solution = extract_solution(model, edge_vars)
                        if check_hashi(islands, hashi_solution):
                            print("Solution extracted and passed final check_hashi.")
                            return generate_output(grid, islands, hashi_solution)
                        else:
                            print("Warning: Solution failed final check_hashi despite passing CNF validation.")
                continue

            for new_level, new_assignment in expand_state(cnf, assignment, level, variables, var_index_map, var_to_clauses):
                h_value = compute_heuristic(cnf, new_assignment, var_index_map)
                new_f = new_level + h_value
                counter += 1
                heapq.heappush(open_list, (new_f, new_level, counter, new_assignment))

            if nodes_expanded % 100000 == 0:
                print(f"Expanded {nodes_expanded:,} nodes so far...", end="\r")

        print(f"\nExpanded all nodes ({nodes_expanded:,}) without finding a valid solution.")
        return ""

    except KeyboardInterrupt:
        print("\n> Terminating...")
        return ""
    except AttributeError:
        print("\nError: encode_hashi might not have returned a CNF object with '.clauses'. Check return type.")
        return ""
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        print(traceback.format_exc())
        return ""
