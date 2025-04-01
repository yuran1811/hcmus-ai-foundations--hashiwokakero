def test_dsu():
    from classes import DSU

    dsu = DSU(5)
    for v in range(5):
        dsu.merge(0, v)

    assert dsu.f[0] == -5 and all(dsu.f[i] == 0 for i in range(1, 5))
