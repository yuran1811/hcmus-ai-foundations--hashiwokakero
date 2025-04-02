from __types import Grid
from utils import (
    check_hashi,
    encode_hashi,
    extract_solution,
    generate_output,
    validate_solution,
)
import itertools 
import heapq
import math


def solve_with_astar(grid: Grid): # Đổi tên hàm
    """
    Giải Hashi bằng cách encode thành CNF và giải CNF bằng A* search,
    giữ nguyên coding style.
    """
    def solve_hashi():
        """
        Hàm nội bộ: Encode Hashi, chạy A* để tìm model CNF, validate/extract.
        """
        # === Các hàm phụ trợ cho A* trên CNF ===

        def _get_variables_from_cnf(cnf_clauses):
            """Lấy danh sách các biến duy nhất (dương) từ các mệnh đề CNF."""
            variables: Set[Variable] = set()
            for clause in cnf_clauses:
                for literal in clause:
                    variables.add(abs(literal))
            return sorted(list(variables))

        def _calculate_heuristic(assignment, cnf_clauses):
            """
            Heuristic h(n): Đếm số mệnh đề CHƯA được thỏa mãn bởi assignment hiện tại.
            Một mệnh đề chưa được thỏa mãn nếu không có literal nào đúng.
            """
            unsatisfied_count = 0
            for clause in cnf_clauses:
                is_satisfied = False
                all_literals_assigned_false = True 
                for literal in clause:
                    if literal in assignment: 
                        is_satisfied = True
                        break
                    elif -literal in assignment:
                        continue 
                    else: 
                        all_literals_assigned_false = False

                if not is_satisfied:
                    unsatisfied_count += 1

            return unsatisfied_count

        def _check_full_assignment_sat(assignment, all_vars, cnf_clauses):
             """Kiểm tra xem một assignment ĐẦY ĐỦ có thỏa mãn CNF không."""
             if not all(var in assignment or -var in assignment for var in all_vars):
                 return False # Not a full assignment

             for clause in cnf_clauses:
                 satisfied = False
                 for literal in clause:
                     if literal in assignment:
                         satisfied = True
                         break
                 if not satisfied:
                     return False 
             return True 

        try:

            cnf_clauses: List[Clause]
            if hasattr(cnf_obj, 'clauses'):
                cnf_clauses = cnf_obj.clauses
            elif isinstance(cnf_obj, list):
                cnf_clauses = cnf_obj
            else:
                print("Error: Unexpected CNF format from encode_hashi.")
                return [],[]

            if not islands: return [], [] 
            if not cnf_clauses and islands:
                 if check_hashi(islands, []): return [], islands
                 else: return [], []

            all_variables = set(_get_variables_from_cnf(cnf_clauses))
            if not all_variables and not cnf_clauses: 
                 if check_hashi(islands, []): return [], islands
                 else: return [], [] 


            print(f"A* on CNF: {len(all_variables)} variables, {len(cnf_clauses)} clauses.")

            # Initial State
            initial_assignment: PartialAssignment = frozenset()
            initial_unassigned: FrozenSet[Variable] = frozenset(all_variables)
            start_state: State = (initial_assignment, initial_unassigned)

            # Priority Queue: (f_cost, g_cost, state)
            initial_h = _calculate_heuristic(initial_assignment, cnf_clauses)
            open_set = [(initial_h, 0, start_state)] # f = g(0) + h
            heapq.heapify(open_set)

            g_score: Dict[State, int] = {start_state: 0}

        except Exception as e:
            import traceback
            print(f"Error during A* initialization or encoding: {e}")
            print(traceback.format_exc())
            return [], []

        processed_states = 0
        while open_set:
            f_cost, current_g_cost, current_state = heapq.heappop(open_set)
            processed_states += 1

            if processed_states % 1000 == 0:
                 print(f"\rA* processed {processed_states} states. Open set size: {len(open_set)}...", end="")

            current_assignment, current_unassigned = current_state

            if not current_unassigned: # Assign all variables
                # Heuristic h(n) = 0 -> goal 
                if _calculate_heuristic(current_assignment, cnf_clauses) == 0:
                    print(f"\nPotential goal state found after {processed_states} states.")
                        # Chuyển PartialAssignment (frozenset) sang Model (list)
                        model: Model = list(current_assignment)

                        # Validate và Extract (giống các phiên bản trước)
                        if validate_solution(islands, edge_vars, model):
                            print("Model passed validation.")
                            hashi_solution = extract_solution(model, edge_vars)
                            if check_hashi(islands, hashi_solution):
                                print("Solution extracted and passed final check_hashi.")
                                return hashi_solution, islands # THÀNH CÔNG!
                else: # Heuristic != 0 -> not goal
                     pass

            if current_unassigned: 
                var_to_assign = min(current_unassigned)
                remaining_unassigned = current_unassigned - {var_to_assign}

                #Create neighbors by assigning True/False to var_to_assign
                for assign_value in [True, False]:
                    literal_to_add = var_to_assign if assign_value else -var_to_assign

                    neighbor_assignment = current_assignment.union({literal_to_add})
                    neighbor_state: State = (neighbor_assignment, remaining_unassigned)
                    neighbor_g_cost = current_g_cost + 1 # Gán thêm 1 biến

                    # if there is no g_score or the new g_cost is less than the existing one
                    if neighbor_state not in g_score or neighbor_g_cost < g_score[neighbor_state]:
                        g_score[neighbor_state] = neighbor_g_cost
                        h_cost = _calculate_heuristic(neighbor_assignment, cnf_clauses)
                        f_cost_neighbor = neighbor_g_cost + h_cost
                        heapq.heappush(open_set, (f_cost_neighbor, neighbor_g_cost, neighbor_state))

        print("\nA* search on CNF completed without finding a valid solution.")
        return [], []

    try:
      sol, islands_data = solve_hashi()
    except KeyboardInterrupt:
       print("\n> terminating A*...")
       return ""
    except Exception as e:
       import traceback
       print(f"\nAn unexpected error occurred during A* execution: {e}")
       print(traceback.format_exc())
       return ""


    if not sol or not islands_data or not check_hashi(islands_data, sol):
        print("Final check failed or no solution found by A* on CNF.")
        return ""

    print("Generating final output from A* CNF solution.")
    return generate_output(grid, islands_data, sol)