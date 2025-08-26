import os
import sys
import time
import csv
import matplotlib.pyplot as plt
from optikit.algorithms.moead import MOEAD
from optikit.problems.problem import Problems

#objeto de problema
problem = Problems()
fn_problem = problem.evaluate_zdt1
# Parámetros del problema
n_var = 30
bounds = [(0, 1)] * n_var
n_runs = 2
tiempos = []

for i in range(n_runs):
    print(f"Ejecutando corrida {i + 1} de {n_runs}")
    inicio = time.time()

    moead = MOEAD(fn_problem, n_var, bounds, n_gen=200, n_sub=100, T=20)
    moead.evolve()

    fin = time.time()
    duracion = fin - inicio
    tiempos.append((i + 1, duracion))
    print(f"Tiempo de ejecución: {duracion:.6f} segundos")

csv_path = "tiempos_moead.csv"
with open(csv_path, mode='w', newline='') as archivo_csv:
    escritor = csv.writer(archivo_csv)
    escritor.writerow(['Ejecución', 'Tiempo (segundos)'])
    escritor.writerows(tiempos)

print(f"\nTiempos guardados en '{csv_path}'")

pareto = moead.get_pareto_front()
f1_vals = [f[0] for f in pareto]
f2_vals = [f[1] for f in pareto]

plt.scatter(f1_vals, f2_vals ,s=10)
plt.xlabel("f1")
plt.ylabel("f2")
plt.title("Pareto Front")
plt.savefig("pareto_front.png", dpi=300)
