from typing import List

from pysat.formula import CNF
from pysat.pb import PBEnc

from models import Bridge, Island
from utils import is_crossing


class CNFGenerator:
    def __init__(self, islands: List[Island], grid: List[List[int]]):
        self.islands = islands
        self.grid = grid
        self.rows, self.cols = len(grid), len(grid[0])
        self.cnf = CNF()
        self.bridge_vars = {}  # Maps (bridge, count) to variable ID

    def _is_valid_horizontal(self, a: Island, b: Island) -> bool:
        y_min, y_max = sorted([a.y, b.y])
        for y in range(y_min + 1, y_max):
            if self.grid[a.x][y] != 0:
                return False
        return True

    def _is_valid_vertical(self, a: Island, b: Island) -> bool:
        x_min, x_max = sorted([a.x, b.x])
        for x in range(x_min + 1, x_max):
            if self.grid[x][a.y] != 0:
                return False
        return True

    def _add_bridge_variable(self, bridge: Bridge, count: int) -> int:
        key = (bridge, count)
        if key not in self.bridge_vars:
            var = len(self.bridge_vars) + 1
            self.bridge_vars[key] = var
        return self.bridge_vars[key]

    def _get_all_possible_bridges(self) -> List[Bridge]:
        bridges = []
        for i in range(len(self.islands)):
            for j in range(i + 1, len(self.islands)):
                a = self.islands[i]
                b = self.islands[j]
                if a.x == b.x and self._is_valid_horizontal(a, b):
                    bridges.append(Bridge(a, b, "horizontal"))
                elif a.y == b.y and self._is_valid_vertical(a, b):
                    bridges.append(Bridge(a, b, "vertical"))
        return bridges

    def _get_adjacent_bridges(self, island: Island) -> List[Bridge]:
        adjacent = []
        for bridge in self._get_all_possible_bridges():
            if bridge.start == island or bridge.end == island:
                adjacent.append(bridge)
        return adjacent

    def generate(self):
        # Step 1: Add mutual exclusion clauses
        for bridge in self._get_all_possible_bridges():
            var1 = self._add_bridge_variable(bridge, 1)
            var2 = self._add_bridge_variable(bridge, 2)
            self.cnf.append([-var1, -var2])  # ¬single ∨ ¬double

        # Step 2: Enforce island bridge counts using PB constraints
        for island in self.islands:
            adjacent_bridges = self._get_adjacent_bridges(island)
            lits, weights = [], []
            for bridge in adjacent_bridges:
                var_single = self.bridge_vars.get((bridge, 1), None)
                var_double = self.bridge_vars.get((bridge, 2), None)
                if var_single:
                    lits.append(var_single)
                    weights.append(1)
                if var_double:
                    lits.append(var_double)
                    weights.append(2)
            if lits:
                clauses = PBEnc.equals(lits, weights, island.num, encoding=0)
                for clause in clauses:
                    self.cnf.append(clause)

        # Step 3: Add no-crossing clauses
        horizontal = [
            b for b in self._get_all_possible_bridges() if b.direction == "horizontal"
        ]
        vertical = [
            b for b in self._get_all_possible_bridges() if b.direction == "vertical"
        ]
        for h_bridge in horizontal:
            for v_bridge in vertical:
                if is_crossing(h_bridge, v_bridge):
                    h_single = self.bridge_vars.get((h_bridge, 1), None)
                    h_double = self.bridge_vars.get((h_bridge, 2), None)
                    v_single = self.bridge_vars.get((v_bridge, 1), None)
                    v_double = self.bridge_vars.get((v_bridge, 2), None)
                    if h_single and v_single:
                        self.cnf.append([-h_single, -v_single])
                    if h_single and v_double:
                        self.cnf.append([-h_single, -v_double])
                    if h_double and v_single:
                        self.cnf.append([-h_double, -v_single])
                    if h_double and v_double:
                        self.cnf.append([-h_double, -v_double])
