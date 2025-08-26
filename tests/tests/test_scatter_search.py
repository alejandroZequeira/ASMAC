from optikit.algorithms.scatter_search import ScatterSearch
import pytest
from axo.contextmanager import AxoContextManager


def objective_function(x):
    return x ** 2

@pytest.mark.asyncio
async def test_local_bess_algorithm():
    with AxoContextManager.local() as dcm:
        sc: ScatterSearch =  ScatterSearch(
            objective_function,
            lower=-10, 
            upper=10, 
            params = {
                "pop_size": 20,
                "refset_size": 5,
                "max_iter": 50
            },
            axo_endpoint_id="axo-endpoint-0"
        )
        _ = await sc.persistify()
        mejor_x = sc.scatter()
        assert mejor_x.is_ok
        best = mejor_x.unwrap()
        print("Best solution found:", best)
        
        
    