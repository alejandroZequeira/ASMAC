from axo.contextmanager import AxoContextManager
from optikit.algorithms.suma_ponderada import SumaPonderada 
import pytest
import numpy as np

@pytest.mark.asyncio
async def test_suma_ponderada():
    with AxoContextManager.local() as dcm:
        sp:SumaPonderada = SumaPonderada(
        
            axo_endpoint_id="axo-endpoint-0")
        _ = await sp.persistify()
        res = sp.suma(pasos=50)
        print("Frente de Pareto generado con éxito:", res)
        assert res.is_ok
        solutions = res.unwrap()
        sp.graficar_frente_pareto(solutions[0])
        
        