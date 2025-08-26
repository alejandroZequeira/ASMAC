from optikit.algorithms.cuckoo_search import CuckooSearch
import pytest
from axo.contextmanager import AxoContextManager
from axo.endpoint.manager import DistributedEndpointManager


def objective_function(x):
    return x ** 2

@pytest.mark.asyncio
async def test_local_bess_algorithm():
    with AxoContextManager.local() as dcm:
        cs: CuckooSearch =  CuckooSearch(
            objective_function,
            lower=-10, 
            upper=10, 
            params = {
                "n": 20,
                "pa": 0.25,
                "max_iter": 100,
                "alpha": 1.0
        },
            axo_endpoint_id="axo-endpoint-0"
        )
        _ = await cs.persistify()
        res = cs.cuckoo()
        assert res.is_ok
        best = res.unwrap()
        print("Best solution found:", best)
        
        
          
    

#    cs = CuckooSearch(objective_function, lower=-10, upper=10, params=params)
#
        