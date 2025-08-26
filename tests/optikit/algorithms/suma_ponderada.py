import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import time
import csv
from axo import Axo, axo_method


class SumaPonderada(Axo):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass
    # Función objetivo 1
    def f1(self, x, *args, **kwargs):
        return x[0]**2 + x[1]**2
    # Función objetivo 2
    def f2(self, x, *args, **kwargs):
        return (x[0] - 1)**2 + (x[1] - 2)**2
    # Función objetivo combinada con pesos
    def weighted_sum_objective(self, x, weights, *args, **kwargs):
        return weights[0]*self.f1(x) + weights[1]*self.f2(x)

    def weighted_sum_method(self, weights, x0=[0, 0]  , *args, **kwargs):
        result = minimize(self.weighted_sum_objective, x0, args=(weights,))
        return result.x, result.fun

    @axo_method
    def suma(self, pasos=50, *args, **kwargs):
        solutions = []
        weights_list = []

        for alpha in np.linspace(0, 1, pasos):
            w = [alpha, 1 - alpha]
            x_opt, _ = self.weighted_sum_method(w)
            f1_val = self.f1(x_opt)
            f2_val = self.f2(x_opt)
            solutions.append([f1_val, f2_val])
            weights_list.append(w)

        return np.array(solutions), weights_list

    def graficar_frente_pareto(self, soluciones, *args, **kwargs):
        plt.figure(figsize=(8, 6))
        plt.plot(soluciones[:, 0], soluciones[:, 1], 'bo-', label='Frente de Pareto (estimado)')
        plt.xlabel('f1(x)')
        plt.ylabel('f2(x)')
        plt.title('Frente de Pareto aproximado por suma ponderada')
        plt.grid(True)
        plt.legend()
        plt.savefig("frente_ponderada.png")
        plt.show()

# Uso
#if __name__ == "__main__":   
#    n=32 
#    pasos = 50
#    TIEMPO =  []
    
#    for i in  range (n):
#        print("ejecucion: ", i)
#        inicio = time.time()    
#        sp = SumaPonderada()
#        final = time.time()
        
#        duracion = final - inicio 
        
#        TIEMPO.append((i+1 ,duracion))
#        print(f"Tiempo de ejecución: {duracion:.8f} ")
        

#    with open('tiempos_ejecucion.csv', mode='w', newline='') as archivo_csv:
#        escritor = csv.writer(archivo_csv)
#        escritor.writerow(['Ejecucion', 'Tiempo (segundos)']) 
#        escritor.writerows(TIEMPO)

#    print("\nTiempos guardados en 'tiempos_ejecucion.csv'")
    
    

#    soluciones, _ = sp.generar_frente_pareto(pasos=50)
#    sp.graficar_frente_pareto(soluciones)
