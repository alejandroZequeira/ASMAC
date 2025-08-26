import pytest
from optikit.algorithms.tabu_search import TabuSearch1D
from axo.contextmanager import AxoContextManager

def objective_function(x):
    return (x - 10) ** 2


def neighbors_fn(x):
    return [x - 1, x + 1]

@pytest.mark.asyncio
async def test_local_Local_search():
    
    with AxoContextManager.local() as dcm:
        ts:TabuSearch1D = TabuSearch1D(
            objective_function,
            neighbors_fn, 
            initial_solution=25,
            axo_endpoint_id="axo-endpoint-0")
        _ = await ts.persistify()
        res = ts.tabu()
        assert res.is_ok
        best ,a = res.unwrap()
        print("Tabu Search:", best,a)



