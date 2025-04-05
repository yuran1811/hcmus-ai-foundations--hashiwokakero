type Coor = tuple[int, int]
type PairII = Coor
type Grid = list[list[int]]
type Island = tuple[int, int, int, int]  # (idx, row, col, degree)
type Edge = tuple[Coor, Coor]  # ((r1, c1), (r2, c2))
type EdgeExtend = tuple[int, int, Coor, Coor]  # (idx1, idx2, (r1, c1), (r2, c2))
type Incident = dict[int, list[tuple[int, int]]]
