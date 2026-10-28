"""
Phase 2: Route Planning & Traffic Analysis
Author: Bhavya Rattan (Roll No: 2401201004)
Repository: bhavyarattan21/smart-city-traffic-optimization

Implements:
1. Dijkstra's Algorithm (Min-Priority Queue via heapq)
2. Bellman-Ford Algorithm (Handles negative edge costs & detects negative cycles)
3. Traffic Congestion Simulator (Modifies weights and quantifies impact)
4. Path Reconstruction & Comparative Route Cost Analysis
"""

import heapq
from typing import Dict, List, Tuple, Optional, Any, Set


def dijkstra(
    adj_list: Dict[str, List[Tuple[str, float]]],
    source: str,
    target: Optional[str] = None
) -> Tuple[Dict[str, float], Dict[str, Optional[str]], List[str]]:
    """
    Computes shortest paths from source using Dijkstra's Algorithm.
    Time Complexity: O((V + E) log V)
    Space Complexity: O(V + E)

    Returns:
        dist: Dict of {node: shortest_travel_time}
        previous: Dict of {node: predecessor_node} for path reconstruction
        path: List of nodes representing shortest path to target (if target specified)
    """
    dist: Dict[str, float] = {node: float("inf") for node in adj_list}
    previous: Dict[str, Optional[str]] = {node: None for node in adj_list}
    dist[source] = 0.0
    pq: List[Tuple[float, str]] = [(0.0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue

        if target is not None and u == target:
            break

        for v, weight in adj_list.get(u, []):
            new_dist = d + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                previous[v] = u
                heapq.heappush(pq, (new_dist, v))

    path: List[str] = []
    if target is not None and dist[target] != float("inf"):
        curr: Optional[str] = target
        while curr is not None:
            path.append(curr)
            curr = previous[curr]
        path.reverse()

    return dist, previous, path


def bellman_ford(
    edges: List[Tuple[str, str, float]],
    nodes: List[str],
    source: str,
    target: Optional[str] = None,
    directed: bool = True
) -> Tuple[Dict[str, float], Dict[str, Optional[str]], List[str], bool]:
    """
    Computes shortest paths using the Bellman-Ford Algorithm.
    Supports negative toll credits/incentives and detects negative-weight cycles.
    Time Complexity: O(V * E)
    Space Complexity: O(V)

    Parameters:
        edges: list of (u, v, weight)
        nodes: list of node identifiers
        source: starting intersection
        target: destination intersection (optional)
        directed: if False, treats each edge as bidirectional

    Returns:
        dist: Dict of {node: shortest_distance}
        previous: Predecessor map
        path: Shortest path to target if target is provided
        has_negative_cycle: True if negative weight cycle is detected
    """
    all_edges = list(edges)
    if not directed:
        for u, v, w in edges:
            all_edges.append((v, u, w))

    dist: Dict[str, float] = {node: float("inf") for node in nodes}
    previous: Dict[str, Optional[str]] = {node: None for node in nodes}
    dist[source] = 0.0

    # Relax all edges |V| - 1 times
    for _ in range(len(nodes) - 1):
        relaxed = False
        for u, v, w in all_edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                previous[v] = u
                relaxed = True
        if not relaxed:
            break

    # Check for negative-weight cycles
    has_negative_cycle = False
    for u, v, w in all_edges:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            has_negative_cycle = True
            break

    path: List[str] = []
    if target is not None and not has_negative_cycle and dist[target] != float("inf"):
        curr: Optional[str] = target
        while curr is not None:
            path.append(curr)
            curr = previous[curr]
        path.reverse()

    return dist, previous, path, has_negative_cycle


def simulate_congestion(
    adj_list: Dict[str, List[Tuple[str, float]]],
    congested_edges: Set[Tuple[str, str]],
    multiplier: float = 3.0
) -> Dict[str, List[Tuple[str, float]]]:
    """
    Simulates traffic congestion by scaling edge travel times by a multiplier.
    Returns a NEW adjacency list reflecting congested traffic conditions.
    """
    new_adj: Dict[str, List[Tuple[str, float]]] = {node: [] for node in adj_list}
    
    # Normalize edges as undirected checks
    norm_congested = set()
    for u, v in congested_edges:
        norm_congested.add((u, v))
        norm_congested.add((v, u))

    for u in adj_list:
        for v, w in adj_list[u]:
            if (u, v) in norm_congested:
                new_w = w * multiplier
            else:
                new_w = w
            new_adj[u].append((v, round(new_w, 2)))

    return new_adj


def analyze_traffic_impact(
    adj_list: Dict[str, List[Tuple[str, float]]],
    source: str,
    target: str,
    congested_edges: Set[Tuple[str, str]],
    multiplier: float = 3.0
) -> Dict[str, Any]:
    """
    Compares route time and route paths before and after simulated congestion.
    """
    before_dist, _, before_path = dijkstra(adj_list, source, target)
    congested_adj = simulate_congestion(adj_list, congested_edges, multiplier)
    after_dist, _, after_path = dijkstra(congested_adj, source, target)

    original_cost = before_dist.get(target, float("inf"))
    congested_cost = after_dist.get(target, float("inf"))
    delay = congested_cost - original_cost
    pct_increase = (delay / original_cost * 100.0) if original_cost > 0 else 0.0

    rerouted = (before_path != after_path)

    return {
        "source": source,
        "target": target,
        "before_path": before_path,
        "before_cost": original_cost,
        "after_path": after_path,
        "after_cost": congested_cost,
        "delay_minutes": delay,
        "percentage_increase": round(pct_increase, 2),
        "rerouted": rerouted,
        "congested_adj_list": congested_adj,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Lab 5: Phase 2 - Route Planning & Congestion Analysis")
    print("Author: Bhavya Rattan (Roll No: 2401201004)")
    print("=" * 60)

    sample_adj = {
        "A": [("B", 4.0), ("C", 2.0)],
        "B": [("A", 4.0), ("C", 1.0), ("D", 5.0)],
        "C": [("A", 2.0), ("B", 1.0), ("D", 8.0)],
        "D": [("B", 5.0), ("C", 8.0)],
    }

    # Dijkstra
    d_dist, _, d_path = dijkstra(sample_adj, "A", "D")
    print("\n[Dijkstra] Shortest distances from A:", d_dist)
    print(f"[Dijkstra] Shortest route A -> D: {' -> '.join(d_path)} (Cost: {d_dist['D']} mins)")

    # Bellman-Ford
    edges = [("A", "B", 4.0), ("A", "C", 2.0), ("B", "C", -3.0), ("B", "D", 5.0), ("C", "D", 8.0)]
    nodes = ["A", "B", "C", "D"]
    bf_dist, _, bf_path, has_neg_cycle = bellman_ford(edges, nodes, "A", "D")
    print("\n[Bellman-Ford with Negative Tolls] Distances:", bf_dist)
    print("Negative weight cycle detected:", has_neg_cycle)

    # Congestion simulation
    impact = analyze_traffic_impact(sample_adj, "A", "D", congested_edges={("B", "C")}, multiplier=5.0)
    print("\n[Congestion Impact Analysis]")
    print(f"Normal Route: {' -> '.join(impact['before_path'])} | Travel Time: {impact['before_cost']} mins")
    print(f"Congested Route: {' -> '.join(impact['after_path'])} | Travel Time: {impact['after_cost']} mins")
    print(f"Delay: +{impact['delay_minutes']} mins (+{impact['percentage_increase']}%), Rerouted: {impact['rerouted']}")
