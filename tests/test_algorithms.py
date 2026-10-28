"""
Unit & Integration Test Suite for Smart City Traffic Management System
Author: Bhavya Rattan (Roll No: 2401201004)
Repository: bhavyarattan21/smart-city-traffic-optimization

Tests:
1. CityGraph adjacency list and matrix generation
2. Dijkstra single-source shortest path and path reconstruction
3. Bellman-Ford shortest path and negative cycle detection
4. Traffic congestion simulator and rerouting impact
5. BFS and DFS traversals, hop levels, and reachability
6. Prim's and Kruskal's MST cost equivalence and cycle rejection
"""

import unittest
from algorithms.graph_model import CityGraph
from algorithms.shortest_path import dijkstra, bellman_ford, simulate_congestion, analyze_traffic_impact
from algorithms.mst import prim_mst, kruskal_mst, UnionFind
from algorithms.traversal import bfs, dfs, get_reachability_report, find_connected_components


class TestSmartCityAlgorithms(unittest.TestCase):

    def setUp(self):
        """Set up standard 4-node benchmark graph from the lab manual."""
        self.manual_adj = {
            "A": [("B", 4.0), ("C", 2.0)],
            "B": [("A", 4.0), ("C", 1.0), ("D", 5.0)],
            "C": [("A", 2.0), ("B", 1.0), ("D", 8.0)],
            "D": [("B", 5.0), ("C", 8.0)],
        }
        self.manual_nodes = ["A", "B", "C", "D"]
        self.manual_edges = [
            ("A", "B", 4.0),
            ("A", "C", 2.0),
            ("B", "C", 1.0),
            ("B", "D", 5.0),
            ("C", "D", 8.0),
        ]

    # --- Phase 1: Graph Representation Tests ---
    def test_city_graph_construction(self):
        city = CityGraph(directed=False)
        city.add_edge("A", "B", 4)
        city.add_edge("A", "C", 2)
        city.add_edge("B", "C", 1)
        city.add_edge("B", "D", 5)
        city.add_edge("C", "D", 8)

        self.assertEqual(len(city.nodes), 4)
        matrix, index = city.to_adjacency_matrix()
        self.assertEqual(len(matrix), 4)
        self.assertEqual(matrix[index["A"]][index["B"]], 4.0)
        self.assertEqual(matrix[index["B"]][index["C"]], 1.0)
        self.assertEqual(matrix[index["A"]][index["D"]], float("inf"))

    # --- Phase 2: Shortest Path Tests ---
    def test_dijkstra_shortest_path(self):
        dist, prev, path = dijkstra(self.manual_adj, "A", "D")
        self.assertEqual(dist["A"], 0.0)
        self.assertEqual(dist["C"], 2.0)
        self.assertEqual(dist["B"], 3.0)  # A -> C -> B = 2 + 1 = 3
        self.assertEqual(dist["D"], 8.0)  # A -> C -> B -> D = 2 + 1 + 5 = 8
        self.assertEqual(path, ["A", "C", "B", "D"])

    def test_bellman_ford_no_negative_cycle(self):
        dist, prev, path, has_neg_cycle = bellman_ford(
            self.manual_edges, self.manual_nodes, "A", "D", directed=False
        )
        self.assertFalse(has_neg_cycle)
        self.assertEqual(dist["D"], 8.0)
        self.assertEqual(path, ["A", "C", "B", "D"])

    def test_bellman_ford_negative_edge(self):
        # Edge B -> C has negative toll credit of -3.0
        neg_edges = [("A", "B", 4.0), ("A", "C", 2.0), ("B", "C", -3.0), ("B", "D", 5.0), ("C", "D", 8.0)]
        dist, _, _, has_neg_cycle = bellman_ford(neg_edges, self.manual_nodes, "A")
        self.assertFalse(has_neg_cycle)
        self.assertEqual(dist["C"], 1.0)  # A -> B -> C = 4 - 3 = 1

    def test_bellman_ford_negative_cycle_detection(self):
        # A - B - A forms negative cycle: (A->B = 1, B->A = -2)
        cyclic_edges = [("A", "B", 1.0), ("B", "A", -2.0), ("B", "C", 3.0)]
        dist, _, _, has_neg_cycle = bellman_ford(cyclic_edges, ["A", "B", "C"], "A")
        self.assertTrue(has_neg_cycle)

    def test_congestion_simulation_and_rerouting(self):
        impact = analyze_traffic_impact(
            self.manual_adj,
            source="A",
            target="D",
            congested_edges={("B", "C")},
            multiplier=5.0  # B-C increases from 1 to 5
        )
        # Normal path: A -> C -> B -> D (cost 8)
        # With B-C = 5:
        # Route 1: A -> C -> B -> D = 2 + 5 + 5 = 12
        # Route 2: A -> B -> D = 4 + 5 = 9 (Reroutes to A -> B -> D!)
        self.assertEqual(impact["before_cost"], 8.0)
        self.assertEqual(impact["after_cost"], 9.0)
        self.assertEqual(impact["after_path"], ["A", "B", "D"])
        self.assertTrue(impact["rerouted"])
        self.assertEqual(impact["delay_minutes"], 1.0)

    # --- Phase 3: Traversal & Connectivity Tests ---
    def test_bfs_traversal(self):
        order, levels, tree_edges = bfs(self.manual_adj, "A")
        self.assertEqual(order[0], "A")
        self.assertEqual(levels["A"], 0)
        self.assertEqual(levels["B"], 1)
        self.assertEqual(levels["C"], 1)
        self.assertEqual(levels["D"], 2)
        self.assertEqual(len(tree_edges), 3)

    def test_dfs_traversal(self):
        order, tree_edges = dfs(self.manual_adj, "A")
        self.assertEqual(order[0], "A")
        self.assertEqual(len(order), 4)
        self.assertEqual(len(tree_edges), 3)

    def test_reachability_report_disconnected_network(self):
        disconnected_adj = dict(self.manual_adj)
        disconnected_adj["Z"] = []  # Isolated intersection
        report = get_reachability_report(disconnected_adj, "A")
        self.assertFalse(report["is_fully_connected"])
        self.assertIn("Z", report["unreachable_nodes"])
        self.assertEqual(report["reachable_count"], 4)
        self.assertEqual(report["unreachable_count"], 1)

    # --- Phase 4: Minimum Spanning Tree Tests ---
    def test_union_find(self):
        uf = UnionFind(["1", "2", "3"])
        self.assertTrue(uf.union("1", "2"))
        self.assertFalse(uf.union("1", "2"))  # Already united
        self.assertTrue(uf.union("2", "3"))
        self.assertEqual(uf.find("1"), uf.find("3"))

    def test_mst_prim_and_kruskal_equivalence(self):
        p_edges, p_cost, _ = prim_mst(self.manual_adj, "A")
        k_edges, k_cost, _ = kruskal_mst(self.manual_edges, self.manual_nodes)

        # Expected MST on manual graph:
        # B-C (1.0), A-C (2.0), B-D (5.0) -> Total Cost = 8.0
        self.assertEqual(p_cost, 8.0)
        self.assertEqual(k_cost, 8.0)
        self.assertEqual(len(p_edges), 3)
        self.assertEqual(len(k_edges), 3)


if __name__ == "__main__":
    unittest.main()
