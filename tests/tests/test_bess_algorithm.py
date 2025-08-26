from optikit.algorithms.bees_algorithm import BeesAlgorithm
import pytest
from axo.contextmanager import AxoContextManager
from axo.endpoint.manager import DistributedEndpointManager



@pytest.mark.asyncio
async def test_local_bess_algorithm():
    with AxoContextManager.local() as dcm:
        ba: BeesAlgorithm =  BeesAlgorithm(
            objective_function=lambda x: x ** 2,
            lower_bound=-10,
            upper_bound=10,
            params={
                "n": 20,
                "m": 10,
                "e": 5,
                "nep": 3,
                "nsp": 2,
                "ngh": 0.5,
                "max_iter": 50
            },
            axo_endpoint_id="axo-endpoint-0"
        )
        _ = await ba.persistify()
        best_solution = ba.bees()
        assert best_solution.is_ok
        print("Best solution found:", best_solution.unwrap())
        