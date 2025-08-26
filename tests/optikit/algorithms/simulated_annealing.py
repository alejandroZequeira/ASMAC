from axo import Axo,axo_method

class SimulatedAnnealing(Axo):
    def __init__(self, solucion_inicial, temperatura, temperatura_minima, factor_enfriamiento,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.solucion_inicial = solucion_inicial
        self.temperatura = temperatura
        self.temperatura_minima = temperatura_minima
        self.factor_enfriamiento = factor_enfriamiento
        self.coste_actual = self.evaluar_coste(self.solucion_inicial)
        self.historial_costes = []  
        
        
    def generar_vecino(self, solucion_actual,**kwargs):
        import random
        return solucion_actual + random.uniform(-1, 1)

    def evaluar_coste(self, solucion,**kwargs):
        return solucion**2
    
    @axo_method
    def simulated(self,**kwargs):
        import random
        import math
        iteracion = 0
        while self.temperatura > self.temperatura_minima:
            nueva_solucion = self.generar_vecino(self.solucion_inicial)
            nuevo_coste = self.evaluar_coste(nueva_solucion)
            delta_e = nuevo_coste - self.coste_actual

            if delta_e < 0 or random.random() < math.exp(-delta_e / self.temperatura):
                self.solucion_inicial = nueva_solucion
                self.coste_actual = nuevo_coste

            self.historial_costes.append(self.coste_actual)

            self.temperatura *= self.factor_enfriamiento
            iteracion += 1

        return self.solucion_inicial, self.coste_actual, iteracion


# import matplotlib.pyplot as plt


# if __name__ == "__main__":
#     sa = SimulatedAnnealing(
#         solucion_inicial = random.uniform(-10, 10),
#         temperatura_inicial = 100.0,
#         temperatura_minima = 0.001,
#         factor_enfriamiento = 0.95
#     )

#     solucion, coste, iteraciones = sa.enfriamiento()

#     print(f"Solución encontrada: x = {solucion:.5f}")
#     print(f"Coste final: f(x) = {coste:.5f}")
#     print(f"Iteraciones: {iteraciones}")

#     plt.plot(sa.historial_costes)
#     plt.title("Evolución del coste en Simulated Annealing")
#     plt.xlabel("Iteración")
#     plt.ylabel("Coste f(x)")
#     plt.grid(True)
#     plt.show()
