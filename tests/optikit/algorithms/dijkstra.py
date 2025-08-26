import networkx as nx
import matplotlib.pyplot as plt
import os
from axo import Axo, axo_method

class DijkstraAlgorithm(Axo):
    def __init__(self, graph,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = graph

    @axo_method
    def dijkstra(self, source, target, **kwargs):
        # Devuelve el camino y el costo total desde source hasta target
        path, cost = nx.single_source_dijkstra(self.graph, source=source, target=target)
        return path, cost  # orden correcto: primero la lista del camino, luego el costo

    def draw_path(self, path, algorithm_name="Dijkstra", **kwargs):
        os.makedirs("img", exist_ok=True)

        pos = nx.spring_layout(self.graph, seed=42)
        plt.figure(figsize=(8, 5))

        nx.draw(self.graph, pos, with_labels=True, node_size=700, node_color='lightblue')
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges, edge_color='crimson', width=3)

        plt.title(f"Camino más corto con {algorithm_name}")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(f"img/{algorithm_name.lower()}_camino.png")
        plt.show()
