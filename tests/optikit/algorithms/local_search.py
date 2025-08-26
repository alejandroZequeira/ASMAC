import random
import matplotlib.pyplot as plt
import os
from axo import Axo, axo_method

os.makedirs("img", exist_ok=True)


class LocalSearch(Axo):
    def __init__(self, x, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.trayectoria = []  # historial de soluciones
        self.fx = []     

    def obj_function(self, x):
        return x**2

    def generate_neighbors(self, x , **kwargs):
        return [x - 1, x + 1]

    def conditional(self, x, **kwargs):
        return abs(x) == 0  
    @axo_method
    def local(self, **kwargs):
        s = self.x
        self.trayectoria.append(s)
        self.fx.append(self.obj_function(s))
        print("Punto de partida:", s)
        print("Valor objetivo inicial:", self.obj_function(s))
        
        while not self.conditional(s):
            neighbors = self.generate_neighbors(s)
            print("Vecinos:", neighbors)

            best_neighbor = None
            best_value = float('inf')

            for neighbor in neighbors:
                value = self.obj_function(neighbor)
                if value < best_value:
                    best_value = value
                    best_neighbor = neighbor

            if best_value < self.obj_function(s):
                s = best_neighbor
                self.trayectoria.append(s)
                self.fx.append(self.obj_function(s))
                
            else:
                break

        print("Mejor solución encontrada:", s)
        return s

#if __name__ == "__main__":
#    busqueda = LocalSearch(x=50)
#    resultado = busqueda.search()

    # Gráfica de convergencia
#    plt.figure(figsize=(8,4))
#    plt.plot(busqueda.fx, marker='o', color='teal')
#    plt.title("Convergencia de Búsqueda Local en $f(x) = x^2$")
#    plt.xlabel("Iteración")
#    plt.ylabel("f(x)")
#    plt.grid()
#    plt.tight_layout()
#    plt.savefig("img/convergencia_local_search.png")
#    plt.show()

    # Gráfica de ruta sobre f(x)
#    import numpy as np
#    x = np.linspace(-55, 55, 400)
#    y = x ** 2

#    plt.figure(figsize=(8,4))
#    plt.plot(x, y, label="f(x) = x²", color='lightgray')
#    plt.plot(busqueda.trayectoria, busqueda.fx, marker='o', color='crimson', label="Ruta del algoritmo")
#    plt.title("Ruta de exploración en $f(x) = x^2$")
#    plt.xlabel("x")
#    plt.ylabel("f(x)")
#    plt.legend()
#    plt.grid()
#    plt.tight_layout()
#    plt.savefig("img/ruta_local_search.png")
#    plt.show()
