class DSU:
    def __init__(self, n: int):
        self.n = n
        self.f = [-1] * (n + 1)  # Using 1-based indexing

    def root(self, u: int):
        if self.f[u] < 0:
            return u

        self.f[u] = self.root(self.f[u])
        return self.f[u]

    def merge(self, u: int, v: int):
        u = self.root(u)
        v = self.root(v)
        if u == v:
            return False

        if self.f[u] > self.f[v]:
            u, v = v, u
        self.f[u] += self.f[v]
        self.f[v] = u
        return True
