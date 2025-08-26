from .individual import Individual
from .utils import init_weights, get_neighbors, scalarizing_chebyshev
import random
from axo import Axo, axo_method

class MOEAD(Axo):
    def __init__(self, problem_func, n_var, bounds, n_gen=100, n_sub=100, T=20 , *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.problem_func = problem_func
        self.n_var = n_var
        self.bounds = bounds
        self.n_gen = n_gen
        self.n_sub = n_sub
        self.T = T

        self.weights = init_weights(n_sub)
        self.neighbors = get_neighbors(self.weights, T)
        self.population = [Individual(n_var, bounds) for _ in range(n_sub)]
        for ind in self.population:
            ind.evaluate(problem_func)

        self.z = [min([ind.f[i] for ind in self.population]) for i in range(2)]

    @axo_method
    def moea(self,**kwargs):
        for gen in range(self.n_gen):
            for i in range(self.n_sub):
                P = self.neighbors[i]
                p1, p2 = random.sample(P, 2)
                child = self.recombine(self.population[p1], self.population[p2])
                child.evaluate(self.problem_func)

                # Actualiza z*
                self.z = [min(self.z[j], child.f[j]) for j in range(2)]

                # Reemplazo
                for j in P:
                    f1 = scalarizing_chebyshev(child.f, self.weights[j], self.z)
                    f2 = scalarizing_chebyshev(self.population[j].f, self.weights[j], self.z)
                    if f1 < f2:
                        self.population[j] = child.copy()

    def recombine(self, ind1, ind2, **kwargs):
        child = Individual(self.n_var, self.bounds)
        child.x = [(x + y) / 2 for x, y in zip(ind1.x, ind2.x)]
        return child

    def get_pareto_front(self, **kwargs):
        return [ind.f for ind in self.population]
