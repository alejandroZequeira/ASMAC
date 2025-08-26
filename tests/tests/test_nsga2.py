from optikit.algorithms.nsga2 import NSGA2
import pytest
from axo.contextmanager import AxoContextManager
from axo.endpoint.manager import DistributedEndpointManager

@pytest.mark.asyncio
async def test_local_nsga2():
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
        nsga2: NSGA2 = NSGA2(params)
        _ = await nsga2.persistify()
        result = nsga2.nsga()
        assert result.is_ok
        population , objectives  = result.unwrap()
        print("Final Population:\n", population)
        print("Objectives:\n", objectives)
        
        
        
    