import random
import numpy as np
import math
import matplotlib.pyplot as plt
import os
from axo import Axo, axo_method

class CuckooSearch(Axo):
    def __init__(self, objective, lower, upper, params, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.f = objective
        self.lower = lower
        self.upper = upper
        self.n = params["n"]              # Número de nidos
        self.pa = params["pa"]            # Probabilidad de descubrimiento
        self.max_iter = params["max_iter"]
        self.alpha = params.get("alpha", 1.0)  # Escala del vuelo Lévy

    def levy_flight(self,**kwargs):
        beta = 1.5
        sigma = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) /
                (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
        u = np.random.normal(0, sigma)
        v = np.random.normal(0, 1)
        step = u / abs(v) ** (1 / beta)
        return self.alpha * step

    def simple_bounds(self, x ,**kwargs):
        return max(self.lower, min(x, self.upper))
    
    @axo_method
    def cuckoo(self, **kwargs):
        os.makedirs("img", exist_ok=True)

        nests = [random.uniform(self.lower, self.upper) for _ in range(self.n)]
        fitness = [self.f(x) for x in nests]
        best = nests[np.argmin(fitness)]
        fx_history = [self.f(best)]

        for _ in range(self.max_iter):
            for i in range(self.n):
                x = nests[i]
                step = self.levy_flight()
                new_x = self.simple_bounds(x + step)
                new_f = self.f(new_x)

                j = random.randint(0, self.n - 1)
                if new_f < fitness[j]:
                    nests[j] = new_x
                    fitness[j] = new_f

            for i in range(self.n):
                if random.random() < self.pa:
                    nests[i] = random.uniform(self.lower, self.upper)
                    fitness[i] = self.f(nests[i])

            current_best = nests[np.argmin(fitness)]
            if self.f(current_best) < self.f(best):
                best = current_best

            fx_history.append(self.f(best))

        self.plot_convergence(fx_history)
        return best

    def plot_convergence(self,fx_history, **kwargs):
        plt.figure(figsize=(8, 4))
        plt.plot(fx_history, marker='o', color='navy')
        plt.title("Convergencia de Cuckoo Search")
        plt.xlabel("Iteración")
        plt.ylabel("Mejor f(x)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("img/cuckoo_convergencia.png")
        plt.show()

#if __name__ == "__main__":
#    def objective_function(x):
#        return x ** 2

#    params = {
#        "n": 20,
#        "pa": 0.25,
#        "max_iter": 100,
#        "alpha": 1.0
#    }

#    cs = CuckooSearch(objective_function, lower=-10, upper=10, params=params)
#    best_solution = cs.search()
#    print("Mejor solución encontrada:", best_solution)
#    print("Valor objetivo:", objective_function(best_solution))
