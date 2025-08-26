from optikit.algorithms.moead import MOEAD
from optikit.problems.problem import Problems
import pytest
from axo.contextmanager import AxoContextManager
import matplotlib.pyplot as plt

problem = Problems()
fn_problem = problem.evaluate_zdt1
# Parámetros del problema
n_var = 30
bounds = [(0, 1)] * n_var
n_runs = 2
tiempos = []

@pytest.mark.asyncio
async def test_local_moea():
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
    
    with AxoContextManager.local() as dcm:
        moead: MOEAD = MOEAD(fn_problem, n_var, bounds, n_gen=200, n_sub=100, T=20)
        _ = await moead.persistify()
        result = moead.moea()
        assert result.is_ok
        pareto = moead.get_pareto_front()
        f1_vals = [f[0] for f in pareto]
        f2_vals = [f[1] for f in pareto]

        plt.scatter(f1_vals, f2_vals ,s=10)
        plt.xlabel("f1")
        plt.ylabel("f2")
        plt.title("Pareto Front")
        plt.savefig("pareto_front.png", dpi=300)
        