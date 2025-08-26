import pytest
from optikit.algorithms.bellaman_ford import BellmanFordAlgorithm
from axo.contextmanager import AxoContextManager
import matplotlib.pyplot as plt
import networkx as nx

edges = [
    ('A', 'B', 1),
    ('B', 'C', 2),
    ('C', 'A', 2),   
    ('C', 'Z', 2)
]#Dijkstra solo acepta aristas con peso positivo, por lo que no se puede usar el grafo con aristas negativas



G = nx.DiGraph()
G.add_weighted_edges_from(edges)


@pytest.mark.asyncio
async def test_local_Local_search():
    with AxoContextManager.local() as dcm:
        bf:BellmanFordAlgorithm = BellmanFordAlgorithm(G, axo_endpoint_id="axo-endpoint-0")
        _ = await bf.persistify()
        res = bf.bellaman('A', 'Z')
        assert res.is_ok
        print(res)
        # cost, path = res.unwrap()
        # print("Bellaman ford:", path, "Coste:", cost)
        # bf.draw_path(path)
       
