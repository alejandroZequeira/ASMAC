import os    
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import csv

from optikit.algorithms.nsga2 import NSGA2

def get_experiment_path(script_path, name="sample"):
    output_dir = os.path.join(script_path, name)  
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

if __name__ == "__main__":
    script_path = os.path.dirname(os.path.abspath(__file__))
    output_path = get_experiment_path(script_path, name="sample")   

    params = {
        "name": "nsga2",
        "label": "NSGA-II",
        "runs": 2, 
        "iters": 50,
        "m_objs": 2,
        "pop_size": 100,
        "params_mop": {"name": "dtlz1"},
        "params_crossover": {"name": "sbx", "prob": 1.0, "eta": 20},
        "params_mutation": {"name": "polymutation", "prob": 1./6, "eta": 15},
        "verbose": True,}

    all_objectives = []
    tiempos_por_run = []
    colors = ['green', 'orange']  

    for run in range(params["runs"]):
        print(f"Ejecutando la corrida {run+1} de {params['runs']}")
        
        start_time = time.time()

        moea = NSGA2(params)
        population, objectives = moea.run()

        end_time = time.time()
        duration = end_time - start_time
        tiempos_por_run.append((run+1, duration))

        if objectives is not None:
            all_objectives.append(objectives)
            file_path = os.path.join(output_path, f"resultados_run_{run+1}.csv")
            np.savetxt(file_path, objectives, delimiter=",", header="Objetivo 1, Objetivo 2", comments="")
            print(f"Resultados guardados en {file_path}")
        else:
            print(f"No se generaron resultados en la corrida {run+1}")

    tiempos_csv = os.path.join(output_path, "tiempos.csv")
    with open(tiempos_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Run", "Tiempo (segundos)"])
        writer.writerows(tiempos_por_run)
    print(f"Tiempos guardados en {tiempos_csv}")

    plt.figure(figsize=(8, 6))
    for i, objectives in enumerate(all_objectives):
        plt.scatter(objectives[:, 0], objectives[:, 1], label=f'Run {i+1}', alpha=0.7, color=colors[i], s=30)

    plt.xlabel('Objetivo 1')
    plt.ylabel('Objetivo 2')
    plt.title('NSGA-II ')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_path, "fronts.png"), dpi=300)
    plt.show()
