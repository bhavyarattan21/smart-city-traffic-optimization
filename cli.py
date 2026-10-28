"""
Interactive Command Line Interface (CLI)
Smart City Traffic Management and Route Optimization System
Author: Bhavya Rattan (Roll No: 2401201004)
Repository: bhavyarattan21/smart-city-traffic-optimization

Allows interactive execution of:
1. Shortest Route computation (Dijkstra vs Bellman-Ford)
2. Real-time Traffic Congestion Simulation & Rerouting
3. Network Connectivity & Reachability Analysis (BFS/DFS)
4. Infrastructure Planning (Prim's vs Kruskal's MST)
5. Algorithmic Benchmarks & Visual Portfolio Generation
"""

import sys
import os
from algorithms.graph_model import CityGraph
from algorithms.shortest_path import dijkstra, bellman_ford, analyze_traffic_impact
from algorithms.mst import prim_mst, kruskal_mst
from algorithms.traversal import bfs, dfs, get_reachability_report, find_connected_components
from analysis.benchmark import run_benchmarks, save_benchmark_csv, generate_benchmark_plots
from visualization import generate_all_visualizations, plot_city_network


def print_header(title: str):
    print("\n" + "=" * 65)
    print(f" {title.center(61)} ")
    print("=" * 65)


def display_node_menu(city: CityGraph):
    print("\nAvailable Intersections in Network:")
    for node in city.nodes:
        info = city.node_info.get(node, {})
        print(f"  [{node}] {info.get('name', 'Intersection') + ' (' + info.get('zone', 'General') + ')':<40}")


def run_cli():
    nodes_csv = "data_csv/city_nodes.csv"
    roads_csv = "data_csv/city_roads.csv"
    city = CityGraph.load_from_csv(nodes_csv, roads_csv, directed=False)

    while True:
        print_header("SMART CITY TRAFFIC OPTIMIZATION SYSTEM")
        print("  Author: Bhavya Rattan (Roll No: 2401201004)")
        print("  Capstone Option A: Graph Algorithms for Urban Mobility")
        print("-" * 65)
        print("  1. View City Network Representation (List & Matrix)")
        print("  2. Compute Optimal Route (Dijkstra Single-Source Path)")
        print("  3. Compute Route with Negative Toll Credits (Bellman-Ford)")
        print("  4. Simulate Real-time Traffic Congestion & Rerouting")
        print("  5. Network Reachability & Traversal Analysis (BFS / DFS)")
        print("  6. Infrastructure Planning: Minimum Spanning Tree (Prim vs Kruskal)")
        print("  7. Run Empirical Benchmarking Suite (V=10 to V=150)")
        print("  8. Generate All Visual Maps & Plots (PNG outputs)")
        print("  0. Exit System")
        print("-" * 65)

        choice = input("Select an option [0-8]: ").strip()

        if choice == "0":
            print("\nExiting Smart City Traffic Optimization System. Goodbye!")
            sys.exit(0)

        elif choice == "1":
            print_header("PHASE 1: ROAD NETWORK MODELING")
            print(f"Total Intersections (Vertices |V|): {len(city.nodes)}")
            edges = city.get_edges()
            print(f"Total Arterial Roads (Edges |E|): {len(edges)}")

            sub_c = input("\nDisplay (1) Adjacency List, (2) Adjacency Matrix, or (3) Both? ").strip()
            if sub_c in ("1", "3"):
                print("\n--- Adjacency List Representation ---")
                for u in city.nodes:
                    name = city.node_info.get(u, {}).get("name", u)
                    nbrs_str = ", ".join([f"{v} ({w}m)" for v, w in city.adj_list.get(u, [])])
                    print(f"  [{u}] {name:<22}: {nbrs_str}")

            if sub_c in ("2", "3"):
                print("\n--- Adjacency Matrix Representation (V x V) ---")
                matrix, index = city.to_adjacency_matrix()
                header_row = "    " + " ".join([f"{n:>5}" for n in city.nodes])
                print(header_row)
                print("   " + "-" * len(header_row))
                for node in city.nodes:
                    row = matrix[index[node]]
                    row_str = " ".join([f"{w:5.1f}" if w != float("inf") else "  INF" for w in row])
                    print(f"  {node} |{row_str}")

        elif choice == "2":
            print_header("PHASE 2: DIJKSTRA SHORTEST ROUTE")
            display_node_menu(city)
            src = input("\nEnter Origin Intersection ID (e.g., A): ").strip().upper()
            dst = input("Enter Destination Intersection ID (e.g., G): ").strip().upper()

            if src not in city.nodes or dst not in city.nodes:
                print("\n[Error] Invalid node ID selected. Please select from the available list.")
                continue

            dist, prev, path = dijkstra(city.adj_list, src, dst)
            print("\n--- Dijkstra Routing Result ---")
            print(f"Origin:      [{src}] {city.node_info[src]['name']}")
            print(f"Destination: [{dst}] {city.node_info[dst]['name']}")
            print(f"Route:       {' -> '.join(path)}")
            print(f"Travel Time: {dist[dst]:.1f} minutes")

            save_fig = input("\nGenerate and display route map plot? (y/n): ").strip().lower()
            if save_fig == "y":
                path_edges = list(zip(path[:-1], path[1:]))
                fig_path = f"graphes/route_{src}_to_{dst}.png"
                plot_city_network(
                    city,
                    highlight_edges=path_edges,
                    highlight_nodes=[src, dst],
                    highlight_color="#2563EB",
                    highlight_label=f"Shortest Route ({dist[dst]} mins)",
                    title=f"Dijkstra Shortest Route: {city.node_info[src]['name']} -> {city.node_info[dst]['name']}",
                    save_path=fig_path
                )
                print(f"Saved route map to {fig_path}")

        elif choice == "3":
            print_header("PHASE 2: BELLMAN-FORD ROUTING & NEGATIVE CYCLE CHECK")
            print("Evaluates shortest routes when roads incorporate negative toll rebates or discounts.")
            display_node_menu(city)
            src = input("\nEnter Origin Intersection ID (e.g., A): ").strip().upper()
            dst = input("Enter Destination Intersection ID (e.g., G): ").strip().upper()

            if src not in city.nodes or dst not in city.nodes:
                print("\n[Error] Invalid node ID selected.")
                continue

            # Check if user wants to add a negative toll incentive
            add_rebate = input("Inject a simulated green corridor toll rebate (-3.0 mins) on a road? (y/n): ").strip().lower()
            edges = list(city.get_edges())

            if add_rebate == "y":
                u_reb = input("Enter road origin node: ").strip().upper()
                v_reb = input("Enter road target node: ").strip().upper()
                rebate_val = float(input("Enter toll credit (e.g. -3.0): ").strip())
                edges.append((u_reb, v_reb, rebate_val))
                print(f"Injected incentive edge: ({u_reb} -> {v_reb}, {rebate_val})")

            dist, prev, path, has_neg_cycle = bellman_ford(edges, city.nodes, src, dst, directed=False)
            print("\n--- Bellman-Ford Result ---")
            print(f"Negative-Weight Cycle Detected: {has_neg_cycle}")
            if not has_neg_cycle:
                print(f"Route:       {' -> '.join(path)}")
                print(f"Travel Cost: {dist[dst]:.1f} mins/cost units")
            else:
                print("[Warning] Infinite negative loop detected in road incentive scheme!")

        elif choice == "4":
            print_header("PHASE 2: REAL-TIME TRAFFIC CONGESTION SIMULATOR")
            print("Simulates high peak traffic and lane closures, calculating dynamic rerouting.")
            display_node_menu(city)
            src = input("\nEnter Origin (e.g., A): ").strip().upper()
            dst = input("Enter Destination (e.g., D): ").strip().upper()

            if src not in city.nodes or dst not in city.nodes:
                print("\n[Error] Invalid node ID selected.")
                continue

            print("\nEnter Congested Road Intersections:")
            u_c = input("  Node 1 (e.g., B): ").strip().upper()
            v_c = input("  Node 2 (e.g., C): ").strip().upper()
            mult = float(input("  Congestion Multiplier (e.g., 3.0 to 5.0): ").strip() or "3.0")

            impact = analyze_traffic_impact(
                city.adj_list,
                source=src,
                target=dst,
                congested_edges={(u_c, v_c)},
                multiplier=mult
            )

            print("\n--- Traffic Bottleneck Impact Analysis ---")
            print(f"Original Optimal Route:   {' -> '.join(impact['before_path'])}")
            print(f"Original Travel Time:     {impact['before_cost']:.1f} minutes")
            print(f"Congested Optimal Route:  {' -> '.join(impact['after_path'])}")
            print(f"Congested Travel Time:    {impact['after_cost']:.1f} minutes")
            print(f"Travel Time Delay:        +{impact['delay_minutes']:.1f} mins (+{impact['percentage_increase']}%)")
            print(f"System Rerouted Traffic:  {'YES - Rerouting triggered' if impact['rerouted'] else 'NO - Primary route remained quickest'}")

        elif choice == "5":
            print_header("PHASE 3: NETWORK CONNECTIVITY & TRAVERSAL (BFS / DFS)")
            display_node_menu(city)
            src = input("\nEnter Dispatch / Emergency Center Node (e.g., A): ").strip().upper()
            if src not in city.nodes:
                print("\n[Error] Invalid node ID.")
                continue

            report = get_reachability_report(city.adj_list, src)
            print("\n--- Connectivity & Reachability Audit ---")
            print(f"Center Node:              [{src}] {city.node_info[src]['name']}")
            print(f"Network Fully Connected:  {report['is_fully_connected']}")
            print(f"Reachable Intersections:  {report['reachable_count']} / {report['total_nodes']}")
            print(f"BFS Exploration Sequence: {' -> '.join(report['bfs_order'])}")
            print("\nBFS Hop Levels from Center:")
            for n, lvl in report['bfs_levels'].items():
                print(f"  [{n}] {city.node_info[n]['name']:<24}: {lvl} hop(s)")

            print(f"\nDFS Deep-Branch Order:    {' -> '.join(report['dfs_order'])}")
            components = find_connected_components(city.adj_list)
            print(f"Connected Sub-Components: {len(components)}")

        elif choice == "6":
            print_header("PHASE 4: INFRASTRUCTURE PLANNING & MST OPTIMIZATION")
            print("Evaluates Minimum Spanning Tree (MST) to minimize municipal road maintenance costs.")

            prim_edges, prim_cost, prim_steps = prim_mst(city.adj_list, city.nodes[0])
            kruskal_edges, kruskal_cost, kruskal_steps = kruskal_mst(city.get_edges(), city.nodes)

            total_network_cost = sum(w for _, _, w in city.get_edges())
            savings = total_network_cost - prim_cost
            savings_pct = (savings / total_network_cost) * 100

            print("\n--- Comparative MST Results ---")
            print(f"Total Full Road Network Length:    {total_network_cost:.1f} km / cost units")
            print(f"Prim's Algorithm MST Total Cost:   {prim_cost:.1f} units (|E_mst| = {len(prim_edges)})")
            print(f"Kruskal's Algorithm MST Total Cost:{kruskal_cost:.1f} units (|E_mst| = {len(kruskal_edges)})")
            print(f"Verification:                      {'PASSED (Identical Costs)' if abs(prim_cost - kruskal_cost) < 1e-4 else 'FAILED'}")
            print(f"Infrastructure Cost Savings:       {savings:.1f} units ({savings_pct:.1f}% reduction)")

            print("\nPrim's MST Step-by-Step Expansion:")
            for s in prim_steps:
                print(f"  Step {s['step']:2d}: Added Road {s['added_edge'][0]}-{s['added_edge'][1]} (Weight: {s['weight']:.1f}m) -> Subtree Cost: {s['cumulative_cost']:.1f}")

        elif choice == "7":
            print_header("EMPIRICAL BENCHMARK SUITE")
            print("Benchmarking Dijkstra, Bellman-Ford, Prim's, Kruskal's, BFS, and DFS...")
            results = run_benchmarks()
            save_benchmark_csv(results)
            generate_benchmark_plots(results)
            print("\nBenchmark completed and plots updated in 'graphes/benchmark_comparison.png'.")

        elif choice == "8":
            print_header("GENERATING VISUAL PORTFOLIO")
            generate_all_visualizations(nodes_csv, roads_csv, output_dir="graphes")
            print("\nGenerated high-resolution figures in 'graphes/' directory.")

        input("\nPress [Enter] to return to Main Menu...")


if __name__ == "__main__":
    run_cli()
