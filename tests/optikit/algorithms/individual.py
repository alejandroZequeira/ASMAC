import random

class Individual:
    def __init__(self, n_var, bounds):
        self.n_var = n_var
        self.bounds = bounds
        self.x = [random.uniform(*bounds[i]) for i in range(n_var)]
        self.f = None

    def evaluate(self, problem_func):
        self.f = problem_func(self.x)

    def copy(self):
        clone = Individual(self.n_var, self.bounds)
        clone.x = self.x[:]
        clone.f = self.f[:]
        return clone
