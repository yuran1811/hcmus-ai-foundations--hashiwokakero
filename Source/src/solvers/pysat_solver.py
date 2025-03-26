from typing import Any, Dict, List, Optional, Tuple

from pysat.solvers import Glucose4

from models import Bridge
from utils import CNFGenerator, identify_islands


def decode_solution(
    model: List[int], bridge_vars: Dict[Tuple[Bridge, int], int]
) -> Dict[Bridge, int]:
    solution: Dict[Bridge, int] = {}
    for var in model:
        if var > 0:  # Check only positive assignments
            for (bridge, count), var_id in bridge_vars.items():
                if var_id == var:
                    solution[bridge] = count
    return solution


def solve_with_pysat(grid: List[List[int]]) -> Optional[Dict[Bridge, int]]:
    islands = identify_islands(grid)
    cnf_gen = CNFGenerator(islands, grid)
    cnf_gen.generate()  # Generates CNF with bridge variables

    solver = Glucose4()
    solver.append_formula(cnf_gen.cnf)

    if solver.solve():
        model: Any = solver.get_model()
        return decode_solution(model, cnf_gen.bridge_vars)
    return None
