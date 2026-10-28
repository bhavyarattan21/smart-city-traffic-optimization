"""
Comparative Performance Analysis & Empirical Benchmarking
Author: Bhavya Rattan (Roll No: 2401201004)
Repository: bhavyarattan21/smart-city-traffic-optimization

Compares:
1. Dijkstra vs Bellman-Ford across network sizes
2. Prim's vs Kruskal's MST execution times
3. BFS vs DFS reachability search times
Generates tabular data and plots for the final report.
"""

import time
import random
import csv
import os
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from algorithms.shortest_path import dijkstra, bellman_ford
from algorithms.mst import prim_mst, kruskal_mst
from algorithms.traversal import bfs, dfs


def generate_random_city_graph(
    num_nodes: int,
    edge_probability: float = 0.3,
    seed: int = 42
) -> Tuple[Dict[str, List[Tuple[str, float]]], List[Tuple[str, str, float]], List[str]]:
    """Generates a connected random city network with V nodes."""
    random.seed(seed)
    nodes = [f"N_{i}" for i in range(num_nodes)]
    adj_list: Dict[str, List[Tuple[str, float]]] = {n: [] for n in nodes}
    edges: List[Tuple[str, str, float]] = []

    # Ensure connectivity via a spanning backbone
    for i in range(1, num_nodes):
        parent = random.choice(nodes[:i])
        child = nodes[i]
        w = round(random.uniform(1.0, 15.0), 2)
        adj_list[parent].append((child, w))
        adj_list[child].append((parent, w))
        edges.append((parent, child, w))

    # Add additional random edges based on edge_probability
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            u, v = nodes[i], nodes[j]
            # Check if edge already added
            if any(nbr == v for nbr, _ in adj_list[u]):
                continue
            if random.random() < edge_probability:
                w = round(random.uniform(1.0, 20.0), 2)
                adj_list[u].append((v, w))
                adj_list[v].append((u, w))
                edges.append((u, v, w))

    return adj_list, edges, nodes


def run_benchmarks() -> List[Dict[str, float]]:
    """Executes runtime benchmarks for all algorithms across multiple graph scales."""
    test_sizes = [10, 25, 50, 75, 100, 150]
    results = []

    print("\nRunning Empirical Performance Benchmarks...")
    print(f"{'V':<5} | {'E':<6} | {'Dijkstra (s)':<14} | {'Bellman-Ford (s)':<18} | {'Prim (s)':<12} | {'Kruskal (s)':<12}")
    print("-" * 75)

    for v_count in test_sizes:
        adj, edges, nodes = generate_random_city_graph(v_count, edge_probability=0.25, seed=v_count)
        e_count = len(edges)
        source = nodes[0]

        # 1. Dijkstra
        t0 = time.perf_counter()
        for _ in range(5):
            dijkstra(adj, source)
        t_dijkstra = (time.perf_counter() - t0) / 5.0

        # 2. Bellman-Ford
        t0 = time.perf_counter()
        for _ in range(3):
            bellman_ford(edges, nodes, source)
        t_bellman = (time.perf_counter() - t0) / 3.0

        # 3. Prim's MST
        t0 = time.perf_counter()
        for _ in range(5):
            prim_mst(adj, source)
        t_prim = (time.perf_counter() - t0) / 5.0

        # 4. Kruskal's MST
        t0 = time.perf_counter()
        for _ in range(5):
            kruskal_mst(edges, nodes)
        t_kruskal = (time.perf_counter() - t0) / 5.0

        # 5. BFS & DFS
        t0 = time.perf_counter()
        for _ in range(10):
            bfs(adj, source)
        t_bfs = (time.perf_counter() - t0) / 10.0

        t0 = time.perf_counter()
        for _ in range(10):
            dfs(adj, source)
        t_dfs = (time.perf_counter() - t0) / 10.0

        row = {
            "vertices": v_count,
            "edges": e_count,
            "dijkstra_time_sec": round(t_dijkstra, 6),
            "bellman_ford_time_sec": round(t_bellman, 6),
            "prim_time_sec": round(t_prim, 6),
            "kruskal_time_sec": round(t_kruskal, 6),
            "bfs_time_sec": round(t_bfs, 6),
            "dfs_time_sec": round(t_dfs, 6),
        }
        results.append(row)

        print(
            f"{v_count:<5} | {e_count:<6} | {t_dijkstra:<14.6f} | {t_bellman:<18.6f} | "
            f"{t_prim:<12.6f} | {t_kruskal:<12.6f}"
        )

    return results


def save_benchmark_csv(results: List[Dict[str, float]], filepath: str = "data_csv/benchmark_results.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fieldnames = list(results[0].keys())
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved benchmark metrics to {filepath}")


def generate_benchmark_plots(results: List[Dict[str, float]], output_path: str = "graphes/benchmark_comparison.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    v = [r["vertices"] for r in results]
    dijkstra_t = [r["dijkstra_time_sec"] * 1000 for r in results]
    bellman_t = [r["bellman_ford_time_sec"] * 1000 for r in results]
    prim_t = [r["prim_time_sec"] * 1000 for r in results]
    kruskal_t = [r["kruskal_time_sec"] * 1000 for r in results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Shortest Path comparison (log scale due to Bellman-Ford O(VE))
    ax1.plot(v, dijkstra_t, marker="o", color="#2563EB", linewidth=2.2, label="Dijkstra O((V+E)logV)")
    ax1.plot(v, bellman_t, marker="s", color="#DC2626", linewidth=2.2, label="Bellman-Ford O(V*E)")
    ax1.set_title("Shortest Path Algorithms: Dijkstra vs Bellman-Ford", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Number of Intersections (Vertices |V|)", fontsize=10)
    ax1.set_ylabel("Execution Time (milliseconds)", fontsize=10)
    ax1.set_yscale("log")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="upper left")

    # MST comparison: Prim vs Kruskal
    ax2.plot(v, prim_t, marker="^", color="#059669", linewidth=2.2, label="Prim's O(E log V)")
    ax2.plot(v, kruskal_t, marker="D", color="#D97706", linewidth=2.2, label="Kruskal's O(E log E)")
    ax2.set_title("Minimum Spanning Tree: Prim vs Kruskal", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Number of Intersections (Vertices |V|)", fontsize=10)
    ax2.set_ylabel("Execution Time (milliseconds)", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="upper left")

    plt.suptitle("Smart City Traffic Optimization - Algorithm Benchmark Suite\nAuthor: Bhavya Rattan (Roll No: 2401201004)", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Generated benchmark comparison figure at {output_path}")


if __name__ == "__main__":
    res = run_benchmarks()
    save_benchmark_csv(res)
    generate_benchmark_plots(res)
