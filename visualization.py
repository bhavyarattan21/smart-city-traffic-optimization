"""
Phase 5: Graph Visualizations & Cartographic Rendering
Author: Bhavya Rattan (Roll No: 2401201004)
Repository: bhavyarattan21/smart-city-traffic-optimization

Generates publication-quality network graphs and comparative maps:
1. Base Road Network topology
2. Dijkstra Shortest Route highlight
3. Congestion impact comparison (Before vs After)
4. BFS and DFS traversal trees
5. Prim's and Kruskal's Minimum Spanning Trees (MST)
"""

import os
from typing import Dict, List, Tuple, Optional, Set
import matplotlib.pyplot as plt
import networkx as nx
from algorithms.graph_model import CityGraph
from algorithms.shortest_path import dijkstra, simulate_congestion
from algorithms.mst import prim_mst, kruskal_mst
from algorithms.traversal import bfs, dfs


# Color scheme for city functional zones
ZONE_COLORS = {
    "Commercial": "#3B82F6",    # Blue
    "Transport Hub": "#EF4444", # Red
    "Industrial": "#F59E0B",    # Amber
    "Educational": "#10B981",   # Green
    "Government": "#8B5CF6",    # Purple
    "Residential": "#EC4899",   # Pink
    "General": "#6B7280"        # Gray
}


def build_networkx_graph(city: CityGraph) -> Tuple[nx.Graph, Dict[str, Tuple[float, float]]]:
    """Converts CityGraph into a NetworkX graph with spatial coordinates."""
    G = nx.Graph()
    pos = {}

    for node in city.nodes:
        info = city.node_info.get(node, {})
        G.add_node(
            node,
            name=info.get("name", node),
            zone=info.get("zone", "General")
        )
        pos[node] = (info.get("x", 0.0), info.get("y", 0.0))

    # Fallback to spring layout if coordinates are missing
    if all(x == 0.0 and y == 0.0 for x, y in pos.values()):
        pos = nx.spring_layout(G, seed=42)

    for u, v, w in city.get_edges():
        G.add_edge(u, v, weight=w)

    return G, pos


def plot_city_network(
    city: CityGraph,
    highlight_edges: Optional[List[Tuple[str, str]]] = None,
    highlight_nodes: Optional[List[str]] = None,
    highlight_color: str = "#DC2626",
    highlight_label: str = "Highlighted Route",
    title: str = "Smart City Road Network & Intersections",
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Renders the city road network with styled nodes, weighted edges, and optional highlighted subgraphs.
    """
    G, pos = build_networkx_graph(city)
    fig, ax = plt.subplots(figsize=figsize, facecolor="#F8FAFC")
    ax.set_facecolor("#F8FAFC")

    # Node colors mapped by urban zone
    node_colors = [
        ZONE_COLORS.get(city.node_info.get(node, {}).get("zone", "General"), "#6B7280")
        for node in G.nodes()
    ]

    # Draw all edges (standard roads)
    nx.draw_networkx_edges(
        G, pos,
        ax=ax,
        edge_color="#CBD5E1",
        width=2.0,
        alpha=0.85
    )

    # Highlight specific edges (e.g., shortest path or MST)
    if highlight_edges:
        # Standardize edge tuples
        h_edges = []
        for u, v in highlight_edges:
            if G.has_edge(u, v):
                h_edges.append((u, v))
            elif G.has_edge(v, u):
                h_edges.append((v, u))

        nx.draw_networkx_edges(
            G, pos,
            edgelist=h_edges,
            ax=ax,
            edge_color=highlight_color,
            width=4.5,
            label=highlight_label
        )

    # Draw vertices
    nx.draw_networkx_nodes(
        G, pos,
        ax=ax,
        node_color=node_colors,
        node_size=1100,
        edgecolors="#1E293B",
        linewidths=1.8
    )

    # Highlight source / destination / tree nodes
    if highlight_nodes:
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=highlight_nodes,
            ax=ax,
            node_color="#FBBF24",
            node_size=1300,
            edgecolors="#B45309",
            linewidths=2.5
        )

    # Labels for node IDs
    nx.draw_networkx_labels(
        G, pos,
        ax=ax,
        font_size=11,
        font_weight="bold",
        font_color="#0F172A"
    )

    # Edge weight labels (travel times in minutes)
    edge_labels = {
        (u, v): f"{d['weight']}m" for u, v, d in G.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        ax=ax,
        font_size=9,
        font_color="#334155",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#E2E8F0", alpha=0.85)
    )

    # Descriptive node annotations
    for node, (x, y) in pos.items():
        name = city.node_info.get(node, {}).get("name", "")
        zone = city.node_info.get(node, {}).get("zone", "")
        ax.text(
            x, y - 4.5,
            f"{name}\n({zone})",
            fontsize=8,
            ha="center",
            va="top",
            color="#475569",
            fontweight="medium"
        )

    ax.set_title(title, fontsize=14, fontweight="bold", pad=20, color="#0F172A")
    ax.axis("off")
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Saved visualization to {save_path}")

    return fig


def plot_congestion_comparison(
    city: CityGraph,
    source: str,
    target: str,
    congested_edges: Set[Tuple[str, str]],
    multiplier: float = 4.0,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Renders side-by-side maps showing route change caused by traffic congestion.
    """
    G, pos = build_networkx_graph(city)

    # Normal route
    normal_dist, _, normal_path = dijkstra(city.adj_list, source, target)
    normal_edges = list(zip(normal_path[:-1], normal_path[1:]))

    # Congested graph & route
    congested_adj = simulate_congestion(city.adj_list, congested_edges, multiplier)
    congested_dist, _, congested_path = dijkstra(congested_adj, source, target)
    congested_route_edges = list(zip(congested_path[:-1], congested_path[1:]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), facecolor="#F8FAFC")

    # Helper function to plot a single subplot
    def render_subplot(ax, edge_weights, route_edges, title, cost, is_congested=False):
        ax.set_facecolor("#F8FAFC")
        node_colors = [
            ZONE_COLORS.get(city.node_info.get(n, {}).get("zone", "General"), "#6B7280")
            for n in G.nodes()
        ]

        # Draw all edges
        for u, v, w in city.get_edges():
            is_c_edge = (u, v) in congested_edges or (v, u) in congested_edges
            edge_col = "#DC2626" if (is_congested and is_c_edge) else "#CBD5E1"
            edge_w = 4.0 if (is_congested and is_c_edge) else 2.0
            style = "dashed" if (is_congested and is_c_edge) else "solid"
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(u, v)],
                ax=ax,
                edge_color=edge_col,
                width=edge_w,
                style=style
            )

        # Draw active shortest route
        r_edges = []
        for u, v in route_edges:
            if G.has_edge(u, v):
                r_edges.append((u, v))
            elif G.has_edge(v, u):
                r_edges.append((v, u))

        nx.draw_networkx_edges(
            G, pos,
            edgelist=r_edges,
            ax=ax,
            edge_color="#2563EB" if not is_congested else "#059669",
            width=5.0
        )

        nx.draw_networkx_nodes(
            G, pos,
            ax=ax,
            node_color=node_colors,
            node_size=1000,
            edgecolors="#1E293B",
            linewidths=1.5
        )

        nx.draw_networkx_labels(
            G, pos,
            ax=ax,
            font_size=10,
            font_weight="bold",
            font_color="#0F172A"
        )

        # Labels
        lbls = {(u, v): f"{edge_weights.get((u, v), edge_weights.get((v, u), 0))}m" for u, v in G.edges()}
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=lbls,
            ax=ax,
            font_size=8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#E2E8F0", alpha=0.8)
        )
        ax.set_title(f"{title}\nTotal Time: {cost:.1f} mins", fontsize=12, fontweight="bold", pad=12)
        ax.axis("off")

    # Normal weights
    norm_w = {(u, v): w for u, v, w in city.get_edges()}
    render_subplot(ax1, norm_w, normal_edges, f"Normal Conditions ({source} -> {target})", normal_dist[target])

    # Congested weights
    cong_w = {}
    for u in congested_adj:
        for v, w in congested_adj[u]:
            cong_w[(u, v)] = w
    render_subplot(
        ax2,
        cong_w,
        congested_route_edges,
        f"Simulated Congestion ({source} -> {target})",
        congested_dist[target],
        is_congested=True
    )

    rerouted = normal_path != congested_path
    delay = congested_dist[target] - normal_dist[target]
    fig.suptitle(
        f"Traffic Congestion Rerouting Impact: {source} to {target} | Delay: +{delay:.1f} mins | Rerouted: {rerouted}",
        fontsize=14,
        fontweight="bold"
    )
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Saved congestion comparison to {save_path}")

    return fig


def plot_mst_comparison(
    city: CityGraph,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Renders Prim's and Kruskal's Minimum Spanning Tree side-by-side to verify equivalence.
    """
    G, pos = build_networkx_graph(city)
    edges = city.get_edges()

    prim_edges, prim_cost, _ = prim_mst(city.adj_list, city.nodes[0])
    kruskal_edges, kruskal_cost, _ = kruskal_mst(edges, city.nodes)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), facecolor="#F8FAFC")

    def render_mst(ax, mst_edge_list, title, cost, edge_color):
        ax.set_facecolor("#F8FAFC")
        node_colors = [
            ZONE_COLORS.get(city.node_info.get(n, {}).get("zone", "General"), "#6B7280")
            for n in G.nodes()
        ]

        # Draw base graph faint
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#E2E8F0", width=1.5, style="dotted")

        # Draw MST edges
        m_edges = []
        for u, v, _ in mst_edge_list:
            if G.has_edge(u, v):
                m_edges.append((u, v))
            elif G.has_edge(v, u):
                m_edges.append((v, u))

        nx.draw_networkx_edges(G, pos, edgelist=m_edges, ax=ax, edge_color=edge_color, width=4.0)

        nx.draw_networkx_nodes(
            G, pos,
            ax=ax,
            node_color=node_colors,
            node_size=1000,
            edgecolors="#1E293B",
            linewidths=1.5
        )
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight="bold", font_color="#0F172A")

        # Edge labels for MST
        mst_labels = {(u, v): f"{w}m" for u, v, w in mst_edge_list}
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=mst_labels,
            ax=ax,
            font_size=8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#E2E8F0", alpha=0.85)
        )

        ax.set_title(f"{title}\nTotal Infrastructure Cost: {cost:.1f}", fontsize=12, fontweight="bold", pad=12)
        ax.axis("off")

    render_mst(ax1, prim_edges, "Prim's Algorithm (Vertex Expansion)", prim_cost, "#059669")
    render_mst(ax2, kruskal_edges, "Kruskal's Algorithm (Edge Sorting + Union-Find)", kruskal_cost, "#D97706")

    fig.suptitle(
        f"Minimum Spanning Tree Verification: Prim's vs Kruskal's (Total Cost = {prim_cost:.1f})",
        fontsize=14,
        fontweight="bold"
    )
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Saved MST comparison to {save_path}")

    return fig


def generate_all_visualizations(
    nodes_csv: str = "data_csv/city_nodes.csv",
    roads_csv: str = "data_csv/city_roads.csv",
    output_dir: str = "graphes"
) -> None:
    """Generates and saves the full visual portfolio for the final report."""
    os.makedirs(output_dir, exist_ok=True)
    city = CityGraph.load_from_csv(nodes_csv, roads_csv, directed=False)

    print("\nGenerating Capstone Visualizations...")

    # 1. Base City Network
    plot_city_network(
        city,
        title="Smart City Road Network (10 Intersections, 19 Arterial Roads)",
        save_path=os.path.join(output_dir, "city_road_network.png")
    )

    # 2. Dijkstra Shortest Route (Downtown A to Airport G)
    _, _, d_path = dijkstra(city.adj_list, "A", "G")
    d_edges = list(zip(d_path[:-1], d_path[1:]))
    plot_city_network(
        city,
        highlight_edges=d_edges,
        highlight_nodes=["A", "G"],
        highlight_color="#2563EB",
        highlight_label="Shortest Route A -> G",
        title=f"Dijkstra Shortest Route: Downtown (A) to Airport (G) [Route: {' -> '.join(d_path)}]",
        save_path=os.path.join(output_dir, "dijkstra_shortest_route.png")
    )

    # 3. Traffic Congestion Comparison
    plot_congestion_comparison(
        city,
        source="A",
        target="D",
        congested_edges={("B", "C")},
        multiplier=5.0,
        save_path=os.path.join(output_dir, "traffic_congestion_reroute.png")
    )

    # 4. MST Comparison (Prim vs Kruskal)
    plot_mst_comparison(
        city,
        save_path=os.path.join(output_dir, "mst_prim_vs_kruskal.png")
    )

    # 5. BFS Connectivity Tree from Downtown (A)
    _, _, bfs_tree = bfs(city.adj_list, "A")
    plot_city_network(
        city,
        highlight_edges=bfs_tree,
        highlight_nodes=["A"],
        highlight_color="#7C3AED",
        highlight_label="BFS Spanning Tree",
        title="BFS Hop-by-Hop Reachability Tree from Downtown Central (A)",
        save_path=os.path.join(output_dir, "bfs_reachability_tree.png")
    )

    # 6. DFS Exploration Tree from North Station (B)
    _, dfs_tree = dfs(city.adj_list, "B")
    plot_city_network(
        city,
        highlight_edges=dfs_tree,
        highlight_nodes=["B"],
        highlight_color="#DB2777",
        highlight_label="DFS Tree",
        title="DFS Deep-Branch Exploration Tree from North Station (B)",
        save_path=os.path.join(output_dir, "dfs_exploration_tree.png")
    )

    print(f"All visualizations successfully generated in '{output_dir}/' directory.")


if __name__ == "__main__":
    generate_all_visualizations()
