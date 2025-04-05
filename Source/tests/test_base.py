from utils.base import edge_orientation, edges_cross, get_islands


def test_get_islands():
    grid = [[1, 0, 2], [0, 0, 0], [3, 0, 4]]
    assert get_islands(grid) == [(0, 0, 0, 1), (1, 0, 2, 2), (2, 2, 0, 3), (3, 2, 2, 4)]


def test_edge_orientation():
    assert edge_orientation((0, 0, (0, 0), (0, 1))) == "h"
    assert edge_orientation((0, 0, (0, 0), (1, 0))) == "v"
    assert edge_orientation((0, 0, (0, 0), (1, 1))) == "other"


def test_edge_cross():
    assert edges_cross((0, 1, (0, 1), (2, 1)), (2, 3, (1, 0), (1, 2)))
    assert not edges_cross((0, 1, (0, 1), (2, 1)), (1, 2, (2, 1), (1, 2)))
