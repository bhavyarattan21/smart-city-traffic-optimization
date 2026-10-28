"""
Phase 1: Project Setup & Road Network Modeling
Author: Bhavya Rattan (Roll No: 2401201004)
Repository: bhavyarattan21/smart-city-traffic-optimization

Represents a smart city road network using both an Adjacency List
and an Adjacency Matrix data structure.
"""

import csv
from typing import Dict, List, Tuple, Any, Optional


class CityGraph:
    """
    Represents a road network using both an adjacency list and an adjacency matrix.
    
    Intersections are represented as vertices and roads as weighted edges.
    Adjacency List is optimal for sparse road networks (O(V + E) space).
    Adjacency Matrix provides O(1) edge lookup (O(V^2) space).
    """

    def __init__(self, directed: bool = False):
        self.directed = directed
        self.adj_list: Dict[str, List[Tuple[str, float]]] = {}
        self.nodes: List[str] = []
        self.node_info: Dict[str, Dict[str, Any]] = {}
        self.edge_info: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def add_node(self, node: str, name: str = "", zone: str = "", x: float = 0.0, y: float = 0.0) -> None:
        """Add a road intersection (vertex) to the city network."""
        if node not in self.adj_list:
            self.adj_list[node] = []
            self.nodes.append(node)
            self.node_info[node] = {
                "name": name if name else f"Intersection {node}",
                "zone": zone if zone else "General",
                "x": float(x),
                "y": float(y),
            }

    def add_edge(self, u: str, v: str, weight: float = 1.0, **metadata) -> None:
        """Add a road (edge) between two intersections with travel cost (weight)."""
        self.add_node(u)
        self.add_node(v)
        
        # Avoid duplicate edges in adjacency list
        self.adj_list[u] = [(nbr, w) for nbr, w in self.adj_list[u] if nbr != v]
        self.adj_list[u].append((v, float(weight)))
        self.edge_info[(u, v)] = {"weight": float(weight), **metadata}

        if not self.directed:
            self.adj_list[v] = [(nbr, w) for nbr, w in self.adj_list[v] if nbr != u]
            self.adj_list[v].append((u, float(weight)))
            self.edge_info[(v, u)] = {"weight": float(weight), **metadata}

    def to_adjacency_matrix(self) -> Tuple[List[List[float]], Dict[str, int]]:
        """
        Converts the graph into a V x V adjacency matrix.
        Returns:
            matrix: 2D array of travel times/weights (float('inf') if no direct road, 0 on diagonal)
            index: mapping from node identifier to 0-based matrix row/column index
        """
        n = len(self.nodes)
        index = {node: i for i, node in enumerate(self.nodes)}
        INF = float("inf")
        matrix = [[0.0 if i == j else INF for j in range(n)] for i in range(n)]
        
        for u in self.adj_list:
            for v, w in self.adj_list[u]:
                matrix[index[u]][index[v]] = float(w)
                
        return matrix, index

    def get_edges(self) -> List[Tuple[str, str, float]]:
        """Returns unique edges as a list of (u, v, weight) tuples."""
        seen = set()
        edges = []
        for u in self.adj_list:
            for v, w in self.adj_list[u]:
                edge_key = (u, v) if self.directed else tuple(sorted((u, v)))
                if edge_key not in seen:
                    seen.add(edge_key)
                    edges.append((u, v, w))
        return edges

    @classmethod
    def load_from_csv(cls, nodes_csv_path: str, roads_csv_path: str, directed: bool = False) -> "CityGraph":
        """Factory method to instantiate a CityGraph from CSV datasets."""
        graph = cls(directed=directed)
        
        # Load Intersections
        with open(nodes_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                graph.add_node(
                    node=row["node_id"],
                    name=row.get("name", ""),
                    zone=row.get("zone", ""),
                    x=float(row.get("x", 0.0)),
                    y=float(row.get("y", 0.0)),
                )
                
        # Load Roads
        with open(roads_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                graph.add_edge(
                    u=row["source"],
                    v=row["target"],
                    weight=float(row["weight"]),
                    road_type=row.get("road_type", "Standard"),
                    speed_limit=row.get("speed_limit", 50),
                    lanes=row.get("lanes", 2),
                )
                
        return graph


if __name__ == "__main__":
    print("=" * 60)
    print("Lab 5: Phase 1 - Road Network Modeling Demonstration")
    print("Author: Bhavya Rattan (Roll No: 2401201004)")
    print("=" * 60)

    city = CityGraph()
    city.add_edge("A", "B", 4)
    city.add_edge("A", "C", 2)
    city.add_edge("B", "C", 1)
    city.add_edge("B", "D", 5)
    city.add_edge("C", "D", 8)

    print("\nAdjacency List Representation:")
    for node, edges in city.adj_list.items():
        print(f"  Intersection {node}: {edges}")

    matrix, index = city.to_adjacency_matrix()
    print(f"\nAdjacency Matrix Representation (Nodes: {city.nodes}):")
    for row in matrix:
        print([round(val, 1) if val != float("inf") else "INF" for val in row])
