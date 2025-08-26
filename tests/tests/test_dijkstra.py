import pytest
from optikit.algorithms.dijkstra import DijkstraAlgorithm
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
        ad:DijkstraAlgorithm = DijkstraAlgorithm(G, axo_endpoint_id="axo-endpoint-0")
        _ = await ad.persistify()
        res = ad.dijkstra('A', 'Z')
        assert res.is_ok
        cost, path = res.unwrap()
        print("Dijkstra:", path, "Coste:", cost)
        ad.draw_path(path)
       
