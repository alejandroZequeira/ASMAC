import matplotlib.pyplot as plt
import os
from axo import Axo, axo_method

class TabuSearch1D(Axo):
    def __init__(self, obj_function, neighborhood_fn, initial_solution, max_iter=50, tabu_size=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.f = obj_function
        self.neighbors = neighborhood_fn
        self.x0 = initial_solution
        self.max_iter = max_iter
        self.tabu_size = tabu_size
    @axo_method
    def tabu(self, *args, **kwargs):
        current = self.x0
        best = current
        tabu = []
        history = [self.f(best)]

        for _ in range(self.max_iter):
            candidates = [s for s in self.neighbors(current) if s not in tabu]
            if not candidates:
                break
            candidate = min(candidates, key=self.f)
            if self.f(candidate) < self.f(best):
                best = candidate
            tabu.append(candidate)
            if len(tabu) > self.tabu_size:
                tabu.pop(0)
            current = candidate
            history.append(self.f(best))

        self.plot_convergence(history)
        return best, self.f(best)

    def plot_convergence(self, history, *args, **kwargs):
        os.makedirs("img", exist_ok=True)
        plt.figure(figsize=(8, 4))
        plt.plot(history, marker='o', color='darkorange')
        plt.title("Convergencia de Tabú Search")
        plt.xlabel("Iteración")
        plt.ylabel("Mejor f(x)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("img/tabu_convergencia.png")
        plt.show()
