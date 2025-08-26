import pytest
from optikit.algorithms.simulated_annealing import SimulatedAnnealing
import random
import matplotlib.pyplot as plt
from axo.contextmanager import AxoContextManager
from axo.endpoint.manager import DistributedEndpointManager

@pytest.fixture()
def dem():
    dem = DistributedEndpointManager()
    dem.add_endpoint(
        endpoint_id  = "axo-endpoint-0",
        hostname     = "localhost",
        protocol     = "tcp",
        req_res_port = 16667,
        pubsub_port  = 16666
    )
    return dem
 
@pytest.mark.skip("")
@pytest.mark.asyncio
async def test_simulated_annealing(dem:DistributedEndpointManager):
    with AxoContextManager.distributed(endpoint_manager=dem) as dcm:
        sa:SimulatedAnnealing = SimulatedAnnealing(
            solucion_inicial= random.uniform(-10,10),
            temperatura=100.0,
            temperatura_minima=.0001,
            factor_enfriamiento= 0.95,
            axo_endpoint_id = "axo-endpoint-0"
        )
        _ = await sa.persistify()
        res = sa.enfriamiento()
        assert res.is_ok
        solucion, coste, iteraciones  = res.unwrap()
        
        print(f"Solución encontrada: x = {solucion:.5f}")
        print(f"Coste final: f(x) = {coste:.5f}")
        print(f"Iteraciones: {iteraciones}")

        plt.plot(sa.historial_costes) # Aqui hay pedo
        plt.title("Evolución del coste en Simulated Annealing")
        plt.xlabel("Iteración")
        plt.ylabel("Coste f(x)")
        plt.grid(True)
        plt.show()


@pytest.mark.asyncio
async def test_local_simulated_annealing():
    with AxoContextManager.local() as lcm:
        sa:SimulatedAnnealing = SimulatedAnnealing(
            solucion_inicial= random.uniform(-10,10),
            temperatura=100.0,
            temperatura_minima=.0001,
            factor_enfriamiento= 0.95,
            axo_endpoint_id = "axo-endpoint-0"
        )
        res = sa.simulated()
        print(res)
        assert res.is_ok
        solucion, coste, iteraciones  = res.unwrap()
        
        print(f"Solución encontrada: x = {solucion:.5f}")
        print(f"Coste final: f(x) = {coste:.5f}")
        print(f"Iteraciones: {iteraciones}")

        plt.plot(sa.historial_costes) # Aqui hay pedo
        plt.title("Evolución del coste en Simulated Annealing")
        plt.xlabel("Iteración")
        plt.ylabel("Coste f(x)")
        plt.grid(True)
        plt.show()