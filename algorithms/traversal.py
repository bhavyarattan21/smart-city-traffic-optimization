"""
Phase 3: Network Connectivity Analysis
Author: Bhavya Rattan (Roll No: 2401201004)
Repository: bhavyarattan21/smart-city-traffic-optimization

Implements:
1. Breadth-First Search (BFS) for layer-by-layer exploration and hop-count reachability
2. Depth-First Search (DFS) for branch exploration and cycle/component detection
3. Comprehensive reachability reporting for emergency dispatch and road closure impacts
"""

from collections import deque
from typing import Dict, List, Tuple, Set, Optional, Any


def bfs(
    adj_list: Dict[str, List[Tuple[str, float]]],
    source: str
) -> Tuple[List[str], Dict[str, int], List[Tuple[str, str]]]:
    """
    Breadth-First Search traversal starting from source.
    Finds level-by-level exploration, minimum hop count from source, and tree edges.
    Time Complexity: O(V + E)
    Space Complexity: O(V)

    Returns:
        order: List of nodes in order of visitation
        levels: Dict mapping node to hop distance (layer) from source
        tree_edges: List of (u, v) tree edges traversed
    """
    if source not in adj_list:
        return [], {}, []

    visited: Set[str] = {source}
    queue: deque = deque([source])
    order: List[str] = []
    levels: Dict[str, int] = {source: 0}
    tree_edges: List[Tuple[str, str]] = []

    while queue:
        u = queue.popleft()
        order.append(u)

        for v, _ in adj_list.get(u, []):
            if v not in visited:
                visited.add(v)
                levels[v] = levels[u] + 1
                tree_edges.append((u, v))
                queue.append(v)

    return order, levels, tree_edges


def dfs(
    adj_list: Dict[str, List[Tuple[str, float]]],
    source: str,
    visited: Optional[Set[str]] = None,
    order: Optional[List[str]] = None,
    tree_edges: Optional[List[Tuple[str, str]]] = None
) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Depth-First Search traversal starting from source.
    Explores as deep as possible before backtracking.
    Time Complexity: O(V + E)
    Space Complexity: O(V)

    Returns:
        order: List of nodes in DFS visit sequence
        tree_edges: Directed edges used to discover new vertices
    """
    if visited is None:
        visited = set()
    if order is None:
        order = []
    if tree_edges is None:
        tree_edges = []

    if source not in adj_list:
        return order, tree_edges

    visited.add(source)
    order.append(source)

    for v, _ in adj_list.get(source, []):
        if v not in visited:
            tree_edges.append((source, v))
            dfs(adj_list, v, visited, order, tree_edges)

    return order, tree_edges


def get_reachability_report(
    adj_list: Dict[str, List[Tuple[str, float]]],
    source: str
) -> Dict[str, Any]:
    """
    Evaluates city road connectivity from a given emergency dispatch or center node.
    Identifies reachable intersections, unreachable zones, and network partitions.
    """
    all_nodes = set(adj_list.keys())
    bfs_order, levels, bfs_tree = bfs(adj_list, source)
    dfs_order, dfs_tree = dfs(adj_list, source)

    reachable_nodes = set(bfs_order)
    unreachable_nodes = all_nodes - reachable_nodes

    return {
        "source": source,
        "total_nodes": len(all_nodes),
        "reachable_count": len(reachable_nodes),
        "unreachable_count": len(unreachable_nodes),
        "reachable_nodes": sorted(list(reachable_nodes)),
        "unreachable_nodes": sorted(list(unreachable_nodes)),
        "is_fully_connected": len(unreachable_nodes) == 0,
        "bfs_order": bfs_order,
        "bfs_levels": levels,
        "bfs_tree_edges": bfs_tree,
        "dfs_order": dfs_order,
        "dfs_tree_edges": dfs_tree,
    }


def find_connected_components(
    adj_list: Dict[str, List[Tuple[str, float]]]
) -> List[List[str]]:
    """
    Identifies all disconnected sub-networks (components) in the city.
    """
    visited: Set[str] = set()
    components: List[List[str]] = []

    for node in adj_list:
        if node not in visited:
            component, _ = dfs(adj_list, node, visited=set())
            for c_node in component:
                visited.add(c_node)
            components.append(component)

    return components


if __name__ == "__main__":
    print("=" * 60)
    print("Lab 5: Phase 3 - Network Connectivity Analysis")
    print("Author: Bhavya Rattan (Roll No: 2401201004)")
    print("=" * 60)

    sample_adj = {
        "A": [("B", 4.0), ("C", 2.0)],
        "B": [("A", 4.0), ("C", 1.0), ("D", 5.0)],
        "C": [("A", 2.0), ("B", 1.0), ("D", 8.0)],
        "D": [("B", 5.0), ("C", 8.0)],
        "E": [],  # Isolated intersection
    }

    bfs_seq, lvls, _ = bfs(sample_adj, "A")
    print("BFS Exploration Order from A:", bfs_seq)
    print("Hop Levels from A:", lvls)

    dfs_seq, _ = dfs(sample_adj, "A")
    print("DFS Exploration Order from A:", dfs_seq)

    report = get_reachability_report(sample_adj, "A")
    print("\nConnectivity Report for Node A:")
    print(f"  Reachable Nodes ({report['reachable_count']}): {report['reachable_nodes']}")
    print(f"  Unreachable Nodes ({report['unreachable_count']}): {report['unreachable_nodes']}")
    print(f"  Network Fully Connected: {report['is_fully_connected']}")
