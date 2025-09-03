
from axo import Axo, axo_method

class MOEAD(Axo):
    
    def __init__(self, problem_func:callable, n_var, bounds, n_gen=100, n_sub=100, T=20 , *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.problem_func = problem_func
        self.n_var = n_var
        self.bounds = bounds
        self.n_gen = n_gen
        self.n_sub = n_sub
        self.T = T

        self.weights = self.init_weights(n_sub)
        self.neighbors = self.get_neighbors(self.weights, T)
        self.population = [self.__set_individual(n_var, bounds) for _ in range(n_sub)]
        for ind in self.population:
            ind=self.__evaluate(ind,problem_func)

        self.z = [min([ind["f"][i] for ind in self.population]) for i in range(2)]
    
    def __set_individual(self,n_var,bounds):
        import random
        ind={
        "n_var": n_var,
        "bounds" : bounds,
        "x": [random.uniform(*bounds[i]) for i in range(n_var)],
        "f" : None
        }
        return ind
        
    def __evaluate(self, ind,problem_func):
        if not callable(problem_func):
            raise TypeError(f"problem_func debe ser callable, pero es {type(problem_func)}")
        ind["f"] = problem_func(ind["x"])
        return ind

    def __copy(self,ind):
        clone = self.__set_individual(ind["n_var"], ind["bounds"])
        clone["x"] =ind["x"][:]
        clone["f"] = ind["f"][:]
        return clone
    
    def init_weights(self,n_subproblems):
        weights = []
        for i in range(n_subproblems):
            w = i / (n_subproblems - 1)
            weights.append([w, 1 - w])
        return weights

    def get_neighbors(self,weights, T):
        neighbors = []
        for i, w in enumerate(weights):
            dists = [(j, self.euclidean_dist(w, weights[j])) for j in range(len(weights))]
            dists.sort(key=lambda x: x[1])
            neighbors.append([j for j, _ in dists[:T]])
        return neighbors
    
    def euclidean_dist(self,a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5
    
    def scalarizing_chebyshev(self,f, weight, z):
        return max(weight[i] * abs(f[i] - z[i]) for i in range(len(f)))
    
    def moea(self,**kwargs):
        import random
        for gen in range(self.n_gen):
            for i in range(self.n_sub):
                P = self.neighbors[i]
                p1, p2 = random.sample(P, 2)
                child = self.recombine(self.population[p1], self.population[p2])
                child=self.__evaluate(child,self.problem_func)

                # Actualiza z*
                self.z = [min(self.z[j], child["f"][j]) for j in range(2)]

                # Reemplazo
                for j in P:
                    f1 = self.scalarizing_chebyshev(child["f"], self.weights[j], self.z)
                    f2 = self.scalarizing_chebyshev(self.population[j]["f"], self.weights[j], self.z)
                    if f1 < f2:
                        self.population[j] = self.__copy(child)

    def recombine(self, ind1, ind2, **kwargs):
        child = self.__set_individual(self.n_var, self.bounds)
        child["X"] = [(x + y) / 2 for x, y in zip(ind1["x"], ind2["x"])]
        return child
    
    def get_pareto_front(self, **kwargs):
        return [ind["f"] for ind in self.population]
