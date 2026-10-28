"""
Phase 4: Infrastructure Planning & Comparative Analysis
Author: Bhavya Rattan (Roll No: 2401201004)
Repository: bhavyarattan21/smart-city-traffic-optimization

Implements:
1. Prim's Algorithm (Min-Heap based MST construction)
2. Kruskal's Algorithm (Disjoint Set Union-Find with path compression)
3. Performance comparator and verification of Minimum Spanning Trees
"""

import heapq
from typing import Dict, List, Tuple, Any, Set, Optional


class UnionFind:
    """
    Disjoint Set Union (DSU) data structure with Path Compression
    and Union by Rank for near O(1) amortized operations.
    """

    def __init__(self, nodes: List[str]):
        self.parent: Dict[str, str] = {n: n for n in nodes}
        self.rank: Dict[str, int] = {n: 0 for n in nodes}

    def find(self, x: str) -> str:
        """Find the root representative of the set containing x with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: str, y: str) -> bool:
        """
        Unites the sets containing x and y.
        Returns True if successful (merged two separate sets),
        or False if they are already in the same set (cycle would be formed).
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        return True


def prim_mst(
    adj_list: Dict[str, List[Tuple[str, float]]],
    start: Optional[str] = None
) -> Tuple[List[Tuple[str, str, float]], float, List[Dict[str, Any]]]:
    """
    Prim's Algorithm for Minimum Spanning Tree.
    Grows the tree by picking the cheapest crossing edge from the visited cut.
    Time Complexity: O(E log V)
    Space Complexity: O(V + E)

    Returns:
        mst_edges: List of (u, v, weight) in the MST
        total_cost: Sum of weights of MST edges
        steps: Step-by-step logs of edge additions for educational visualization
    """
    if not adj_list:
        return [], 0.0, []

    if start is None or start not in adj_list:
        start = next(iter(adj_list.keys()))

    visited: Set[str] = {start}
    edge_heap: List[Tuple[float, str, str]] = [(w, start, v) for v, w in adj_list[start]]
    heapq.heapify(edge_heap)

    mst_edges: List[Tuple[str, str, float]] = []
    total_cost: float = 0.0
    steps: List[Dict[str, Any]] = []

    step_idx = 1
    while edge_heap and len(visited) < len(adj_list):
        weight, u, v = heapq.heappop(edge_heap)
        if v in visited:
            continue

        visited.add(v)
        mst_edges.append((u, v, weight))
        total_cost += weight

        steps.append({
            "step": step_idx,
            "added_edge": (u, v),
            "weight": weight,
            "connected_node": v,
            "cumulative_cost": round(total_cost, 2),
        })
        step_idx += 1

        for nxt, w in adj_list[v]:
            if nxt not in visited:
                heapq.heappush(edge_heap, (w, v, nxt))

    return mst_edges, round(total_cost, 2), steps


def kruskal_mst(
    edges: List[Tuple[str, str, float]],
    nodes: List[str]
) -> Tuple[List[Tuple[str, str, float]], float, List[Dict[str, Any]]]:
    """
    Kruskal's Algorithm for Minimum Spanning Tree.
    Greedily selects the globally smallest edges that do not create cycles.
    Time Complexity: O(E log E)
    Space Complexity: O(V + E)

    Returns:
        mst_edges: List of (u, v, weight) in the MST
        total_cost: Sum of weights of MST edges
        steps: Step-by-step decision log (accepted/rejected)
    """
    uf = UnionFind(nodes)
    mst_edges: List[Tuple[str, str, float]] = []
    total_cost: float = 0.0
    steps: List[Dict[str, Any]] = []

    # Sort edges in non-decreasing order of weight
    sorted_edges = sorted(edges, key=lambda e: e[2])

    step_idx = 1
    for u, v, w in sorted_edges:
        if uf.union(u, v):
            mst_edges.append((u, v, w))
            total_cost += w
            steps.append({
                "step": step_idx,
                "edge": (u, v),
                "weight": w,
                "action": "ACCEPTED",
                "reason": "Connects two disjoint components",
                "cumulative_cost": round(total_cost, 2),
            })
            step_idx += 1
            if len(mst_edges) == len(nodes) - 1:
                break
        else:
            steps.append({
                "step": step_idx,
                "edge": (u, v),
                "weight": w,
                "action": "REJECTED",
                "reason": "Forms a cycle in existing tree",
                "cumulative_cost": round(total_cost, 2),
            })
            step_idx += 1

    return mst_edges, round(total_cost, 2), steps


if __name__ == "__main__":
    print("=" * 60)
    print("Lab 5: Phase 4 - Infrastructure Planning & MST Analysis")
    print("Author: Bhavya Rattan (Roll No: 2401201004)")
    print("=" * 60)

    sample_adj = {
        "A": [("B", 4.0), ("C", 2.0)],
        "B": [("A", 4.0), ("C", 1.0), ("D", 5.0)],
        "C": [("A", 2.0), ("B", 1.0), ("D", 8.0)],
        "D": [("B", 5.0), ("C", 8.0)],
    }
    sample_nodes = ["A", "B", "C", "D"]
    sample_edges = [
        ("A", "B", 4.0),
        ("A", "C", 2.0),
        ("B", "C", 1.0),
        ("B", "D", 5.0),
        ("C", "D", 8.0),
    ]

    prim_res, prim_cost, _ = prim_mst(sample_adj, "A")
    print("\n[Prim's Algorithm MST]")
    print("  Edges:", prim_res)
    print(f"  Total Infrastructure Cost: {prim_cost}")

    kruskal_res, kruskal_cost, _ = kruskal_mst(sample_edges, sample_nodes)
    print("\n[Kruskal's Algorithm MST]")
    print("  Edges:", kruskal_res)
    print(f"  Total Infrastructure Cost: {kruskal_cost}")

    assert abs(prim_cost - kruskal_cost) < 1e-5, "MST costs must match!"
    print("\nVerification Passed: Both Prim's and Kruskal's yielded identical optimal MST cost!")
