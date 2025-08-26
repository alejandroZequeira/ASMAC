import random
import matplotlib.pyplot as plt
import numpy as np
import os
from axo import Axo, axo_method

class BeesAlgorithm(Axo):
    def __init__(self, objective_function, lower_bound, upper_bound, params, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.f = objective_function
        self.lower = lower_bound
        self.upper = upper_bound
        self.n = params["n"]      
        self.m = params["m"]       
        self.e = params["e"]       
        self.nep = params["nep"]   
        self.nsp = params["nsp"]   
        self.ngh = params["ngh"]   
        self.max_iter = params["max_iter"]

    def _random_solution(self, **kwargs):
        return random.uniform(self.lower, self.upper)

    def _neighborhood(self, x, **kwargs):
        delta = random.uniform(-self.ngh, self.ngh)
        neighbor = x + delta
        return max(self.lower, min(neighbor, self.upper))
    @axo_method
    def bees(self, **kwargs):
        os.makedirs("img", exist_ok=True)

        population = [self._random_solution() for _ in range(self.n)]
        best_solution = min(population, key=self.f)

        history_fx = []
        history_elite = []
        history_sites = []
        history_scouts = []

        for it in range(self.max_iter):
            population.sort(key=self.f)
            new_population = []

            elite_sites = []
            selected_sites = []

            # Élite
            for i in range(self.e):
                patch_center = population[i]
                recruits = [self._neighborhood(patch_center) for _ in range(self.nep)]
                best_patch = min(recruits, key=self.f)
                new_population.append(best_patch)
                elite_sites.append(best_patch)

            # Resto de sitios
            for i in range(self.e, self.m):
                patch_center = population[i]
                recruits = [self._neighborhood(patch_center) for _ in range(self.nsp)]
                best_patch = min(recruits, key=self.f)
                new_population.append(best_patch)
                selected_sites.append(best_patch)

            # Exploradoras
            scouts = [self._random_solution() for _ in range(self.n - self.m)]
            new_population.extend(scouts)

            # Historial
            population = new_population
            best_candidate = min(population, key=self.f)
            if self.f(best_candidate) < self.f(best_solution):
                best_solution = best_candidate

            history_fx.append(self.f(best_solution))
            history_elite.append(elite_sites)
            history_sites.append(selected_sites)
            history_scouts.append(scouts)

            self._plot_iteration(it, elite_sites, selected_sites, scouts)

        
        self._plot_convergence(history_fx)

        return best_solution

    def _plot_iteration(self, iter_num, elites, sites, scouts, **kwargs):
        x_curve = np.linspace(self.lower, self.upper, 400)
        y_curve = x_curve ** 2

        plt.figure(figsize=(8, 4))
        plt.plot(x_curve, y_curve, color='lightgray', label="f(x) = x²")
        plt.scatter(scouts, [self.f(x) for x in scouts], color='skyblue', label='Exploradoras')
        plt.scatter(sites, [self.f(x) for x in sites], color='orange', label='Sitios Seleccionados')
        plt.scatter(elites, [self.f(x) for x in elites], color='crimson', label='Élite')
        plt.title(f"Iteración {iter_num + 1}")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"img/bees_iter_{iter_num+1:02d}.png")
        plt.close()

    def _plot_convergence(self, fx_history):
        plt.figure(figsize=(8, 4))
        plt.plot(fx_history, marker='o', color='green')
        plt.title("Convergencia del Bees Algorithm")
        plt.xlabel("Iteración")
        plt.ylabel("Mejor f(x)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("img/bees_convergencia.png")
        plt.show()


if __name__ == "__main__":
    def objective(x):
        return x ** 2


    params = {
        "n": 30,
        "m": 10,
        "e": 3,
        "nep": 5,
        "nsp": 3,
        "ngh": 1.0,
        "max_iter": 50
    }

    bees = BeesAlgorithm(objective, lower_bound=-100, upper_bound=100, params=params)
    best = bees.search()
    print("Mejor solución encontrada:", best, "con f(x) =", objective(best))
