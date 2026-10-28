"""
Streamlit Web Application: Smart City Traffic Management & Route Optimization
Author: Bhavya Rattan (Roll No: 2401201004)
Repository: bhavyarattan21/smart-city-traffic-optimization

An interactive web dashboard for urban traffic engineers and city administrators:
- Interactive Route Planning (Dijkstra & Bellman-Ford)
- Real-time Traffic Congestion Simulator & Dynamic Rerouting
- Infrastructure Budget Optimization (Prim's vs Kruskal's MST)
- Network Connectivity & Emergency Dispatch Auditing (BFS / DFS)
- Empirical Complexity Benchmarking & Performance Analytics
"""

import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from algorithms.graph_model import CityGraph
from algorithms.shortest_path import dijkstra, bellman_ford, simulate_congestion, analyze_traffic_impact
from algorithms.mst import prim_mst, kruskal_mst
from algorithms.traversal import bfs, dfs, get_reachability_report, find_connected_components
from visualization import (
    plot_city_network,
    plot_congestion_comparison,
    plot_mst_comparison,
    ZONE_COLORS
)


st.set_page_config(
    page_title="Smart City Traffic Optimization",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_city_network():
    nodes_csv = "data_csv/city_nodes.csv"
    roads_csv = "data_csv/city_roads.csv"
    return CityGraph.load_from_csv(nodes_csv, roads_csv, directed=False)


city = load_city_network()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/traffic-light.png", width=70)
st.sidebar.title("Urban Mobility AI")
st.sidebar.markdown("**Lab 5: Capstone Project (Option A)**\n*Bhavya Rattan | Roll No: 2401201004*")

menu = st.sidebar.radio(
    "Navigation Modules:",
    [
        "🌆 City Network & Topology",
        "🗺️ Route Optimization (Dijkstra / Bellman-Ford)",
        "🚦 Real-time Congestion Simulator",
        "🏗️ Infrastructure Planning (Prim / Kruskal)",
        "📡 Network Connectivity (BFS / DFS)",
        "📊 Benchmark & Complexity Suite",
        "📄 Academic Documentation"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Core Graph Algorithms:**\n"
    "- Dijkstra & Bellman-Ford\n"
    "- Prim's & Kruskal's MST\n"
    "- BFS & DFS Traversal\n"
    "- Dynamic Rerouting Engine"
)


# ==============================================================================
# 1. City Network & Topology
# ==============================================================================
if menu == "🌆 City Network & Topology":
    st.markdown('<div class="main-header">🌆 Urban Road Network Topology</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Graph modeling of intersections (vertices) and arterial roads (edges) using Adjacency List and Matrix structures.</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Intersections (|V|)", len(city.nodes))
    with col2:
        st.metric("Total Arterial Roads (|E|)", len(city.get_edges()))
    with col3:
        st.metric("Average Degree", f"{2 * len(city.get_edges()) / len(city.nodes):.1f}")
    with col4:
        total_time = sum(w for _, _, w in city.get_edges())
        st.metric("Total Network Length", f"{total_time:.1f} km / min")

    tab1, tab2, tab3 = st.tabs(["🗺️ Cartographic Map", "📋 Node & Edge Datasets", "🧮 Adjacency Matrix (V x V)"])

    with tab1:
        fig = plot_city_network(city, title="Smart City Master Road Network")
        st.pyplot(fig)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Intersections (Vertices)")
            nodes_df = pd.DataFrame([
                {"ID": n, "Name": city.node_info[n]["name"], "Zone": city.node_info[n]["zone"], "Coordinates": f"({city.node_info[n]['x']}, {city.node_info[n]['y']})"}
                for n in city.nodes
            ])
            st.dataframe(nodes_df, use_container_width=True)

        with c2:
            st.markdown("#### Arterial Roads (Weighted Edges)")
            edges_df = pd.DataFrame([
                {"Source": u, "Target": v, "Travel Time (min)": w, "Road Type": city.edge_info.get((u, v), {}).get("road_type", "Standard")}
                for u, v, w in city.get_edges()
            ])
            st.dataframe(edges_df, use_container_width=True)

    with tab3:
        st.markdown("#### V x V Adjacency Matrix")
        st.caption("Diagonal elements are 0. Direct roads show travel weight. Non-adjacent nodes show ∞ (infinity).")
        matrix, index = city.to_adjacency_matrix()
        matrix_df = pd.DataFrame(
            [[val if val != float("inf") else "INF" for val in row] for row in matrix],
            index=city.nodes,
            columns=city.nodes
        )
        st.dataframe(matrix_df, use_container_width=True)


# ==============================================================================
# 2. Route Optimization (Dijkstra / Bellman-Ford)
# ==============================================================================
elif menu == "🗺️ Route Optimization (Dijkstra / Bellman-Ford)":
    st.markdown('<div class="main-header">🗺️ Dynamic Route Planning & Optimization</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Single-source shortest path computation using Dijkstra (Min-Priority Queue) and Bellman-Ford (supports negative toll credits).</div>', unsafe_allow_html=True)

    col_ctrl, col_map = st.columns([1, 2])

    with col_ctrl:
        st.markdown("### Route Parameters")
        node_options = [f"{n} - {city.node_info[n]['name']}" for n in city.nodes]

        src_sel = st.selectbox("Origin Intersection:", node_options, index=0)
        dst_sel = st.selectbox("Destination Intersection:", node_options, index=6)

        src_id = src_sel.split(" - ")[0]
        dst_id = dst_sel.split(" - ")[0]

        algo_choice = st.radio("Routing Algorithm:", ["Dijkstra's Algorithm (O((V+E)logV))", "Bellman-Ford Algorithm (O(V*E))"])

        st.markdown("#### Incentive / Rebate Modeling")
        enable_rebate = st.checkbox("Inject Negative Toll Credit (Eco-discount)")
        neg_edge = None
        rebate_val = 0.0

        if enable_rebate:
            c_u = st.selectbox("Discount Road Origin:", city.nodes, index=1)
            c_v = st.selectbox("Discount Road Destination:", [n for n in city.nodes if n != c_u], index=1)
            rebate_val = st.slider("Toll Credit Value (Cost Reduction):", min_value=-5.0, max_value=-0.5, value=-2.0, step=0.5)
            neg_edge = (c_u, c_v, rebate_val)

        calc_btn = st.button("🚀 Calculate Optimal Route", type="primary", use_container_width=True)

    with col_map:
        if src_id == dst_id:
            st.warning("Origin and Destination are identical. Travel time is 0 minutes.")
        else:
            if "Bellman-Ford" in algo_choice or enable_rebate:
                edges = list(city.get_edges())
                if enable_rebate and neg_edge:
                    edges.append(neg_edge)
                dist, prev, path, has_neg_cycle = bellman_ford(edges, city.nodes, src_id, dst_id, directed=False)
                cost = dist.get(dst_id, float("inf"))
                if has_neg_cycle:
                    st.error("🚨 Negative Weight Cycle Detected! Infinite cost reduction loop exists.")
            else:
                dist, prev, path = dijkstra(city.adj_list, src_id, dst_id)
                cost = dist.get(dst_id, float("inf"))

            # Metrics
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Travel Time", f"{cost:.1f} mins")
            with m2:
                st.metric("Number of Hops", len(path) - 1 if path else 0)
            with m3:
                st.metric("Algorithm Applied", "Bellman-Ford" if "Bellman-Ford" in algo_choice or enable_rebate else "Dijkstra")

            st.success(f"**Optimal Route:** {' ➔ '.join(path)}")

            # Render route plot
            path_edges = list(zip(path[:-1], path[1:]))
            fig = plot_city_network(
                city,
                highlight_edges=path_edges,
                highlight_nodes=[src_id, dst_id],
                highlight_color="#2563EB",
                highlight_label="Optimal Route",
                title=f"Optimal Navigation: {city.node_info[src_id]['name']} to {city.node_info[dst_id]['name']}"
            )
            st.pyplot(fig)


# ==============================================================================
# 3. Real-time Traffic Congestion Simulator
# ==============================================================================
elif menu == "🚦 Real-time Congestion Simulator":
    st.markdown('<div class="main-header">🚦 Real-time Traffic Congestion & Rerouting Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Quantify travel delay, identify urban bottlenecks, and test dynamic rerouting when road incidents occur.</div>', unsafe_allow_html=True)

    col_side, col_vis = st.columns([1, 2])

    with col_side:
        st.markdown("### Congestion Simulation Controls")
        src_n = st.selectbox("Trip Origin:", [f"{n} - {city.node_info[n]['name']}" for n in city.nodes], index=0)
        dst_n = st.selectbox("Trip Destination:", [f"{n} - {city.node_info[n]['name']}" for n in city.nodes], index=3)

        src = src_n.split(" - ")[0]
        dst = dst_n.split(" - ")[0]

        # Edge choices
        edge_list = [f"{u} - {v} (Normal: {w}m)" for u, v, w in city.get_edges()]
        selected_edge_str = st.selectbox("Select Bottleneck Road:", edge_list, index=3)
        u_sel, v_sel = selected_edge_str.split(" (")[0].split(" - ")

        multiplier = st.slider("Traffic Congestion Multiplier (Delay Factor):", min_value=1.5, max_value=8.0, value=5.0, step=0.5)

        st.markdown("#### Predefined Incident Scenarios")
        scen_preset = st.selectbox("Load Scenario Preset:", [
            "Custom Incident",
            "Morning Rush Hour Tech Park (B-C x5)",
            "Freeway Bridge Repairs (D-E x4)",
            "Airport Peak Commute (D-G x3)",
            "Downtown Emergency Roadwork (A-B x4)",
            "Valley Flash Flooding (F-H x3)"
        ])

        if scen_preset == "Morning Rush Hour Tech Park (B-C x5)":
            u_sel, v_sel, multiplier = "B", "C", 5.0
        elif scen_preset == "Freeway Bridge Repairs (D-E x4)":
            u_sel, v_sel, multiplier = "D", "E", 4.0
        elif scen_preset == "Airport Peak Commute (D-G x3)":
            u_sel, v_sel, multiplier = "D", "G", 3.0
        elif scen_preset == "Downtown Emergency Roadwork (A-B x4)":
            u_sel, v_sel, multiplier = "A", "B", 4.0
        elif scen_preset == "Valley Flash Flooding (F-H x3)":
            u_sel, v_sel, multiplier = "F", "H", 3.0

    impact = analyze_traffic_impact(
        city.adj_list,
        source=src,
        target=dst,
        congested_edges={(u_sel, v_sel)},
        multiplier=multiplier
    )

    with col_vis:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Normal Travel Time", f"{impact['before_cost']:.1f}m")
        with c2:
            st.metric("Congested Travel Time", f"{impact['after_cost']:.1f}m")
        with c3:
            st.metric("Travel Delay", f"+{impact['delay_minutes']:.1f}m", delta=f"{impact['percentage_increase']}%", delta_color="inverse")
        with c4:
            st.metric("Rerouted?", "YES" if impact["rerouted"] else "NO")

        if impact["rerouted"]:
            st.info(f"🔄 **Smart Reroute Triggered:** Primary route delayed! Diverted traffic along: `{' ➔ '.join(impact['after_path'])}`")
        else:
            st.warning("⚠️ **No Faster Alternate:** Existing route remains quickest despite congestion.")

        fig = plot_congestion_comparison(
            city,
            source=src,
            target=dst,
            congested_edges={(u_sel, v_sel)},
            multiplier=multiplier
        )
        st.pyplot(fig)


# ==============================================================================
# 4. Infrastructure Planning (Prim / Kruskal)
# ==============================================================================
elif menu == "🏗️ Infrastructure Planning (Prim / Kruskal)":
    st.markdown('<div class="main-header">🏗️ Infrastructure Planning & Spanning Tree Optimization</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Minimum Spanning Tree (MST) algorithms to connect all city districts at minimal municipal capital expenditure and maintenance cost.</div>', unsafe_allow_html=True)

    prim_edges, prim_cost, prim_steps = prim_mst(city.adj_list, city.nodes[0])
    kruskal_edges, kruskal_cost, kruskal_steps = kruskal_mst(city.get_edges(), city.nodes)
    total_network_len = sum(w for _, _, w in city.get_edges())
    savings = total_network_len - prim_cost
    savings_pct = (savings / total_network_len) * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Network Length", f"{total_network_len:.1f} km")
    with col2:
        st.metric("Optimal MST Budget", f"{prim_cost:.1f} km / cost units")
    with col3:
        st.metric("Budget Savings", f"-{savings:.1f} km", delta=f"{savings_pct:.1f}% Savings")
    with col4:
        st.metric("Equivalence Verification", "PASSED (Identical Cost)" if abs(prim_cost - kruskal_cost) < 1e-4 else "FAILED")

    tab1, tab2, tab3 = st.tabs(["🗺️ MST Comparative Visualizer", "🪜 Prim's Step-by-Step Expansion", "🔍 Kruskal's Edge Decisions"])

    with tab1:
        fig = plot_mst_comparison(city)
        st.pyplot(fig)

    with tab2:
        st.markdown("#### Prim's Algorithm Growth Log (Vertex Cut Expansion)")
        st.caption("Greedily extends the tree frontier by picking the minimum-weight edge connecting visited to unvisited vertices.")
        prim_df = pd.DataFrame([
            {
                "Step": s["step"],
                "Connected Edge": f"{s['added_edge'][0]} - {s['added_edge'][1]}",
                "New Intersection": s["connected_node"],
                "Edge Weight (km)": s["weight"],
                "Cumulative Cost (km)": s["cumulative_cost"]
            }
            for s in prim_steps
        ])
        st.dataframe(prim_df, use_container_width=True)

    with tab3:
        st.markdown("#### Kruskal's Algorithm Decision Log (Disjoint Set Union-Find)")
        st.caption("Evaluates edges in global non-decreasing order of weight. Detects cycles in O(α(V)) amortized time using Union-Find.")
        kruskal_df = pd.DataFrame([
            {
                "Step": s["step"],
                "Evaluated Edge": f"{s['edge'][0]} - {s['edge'][1]}",
                "Weight (km)": s["weight"],
                "Decision": s["action"],
                "Rationale": s["reason"],
                "Running Cost": s["cumulative_cost"]
            }
            for s in kruskal_steps
        ])
        st.dataframe(kruskal_df, use_container_width=True)


# ==============================================================================
# 5. Network Connectivity (BFS / DFS)
# ==============================================================================
elif menu == "📡 Network Connectivity (BFS / DFS)":
    st.markdown('<div class="main-header">📡 Urban Network Connectivity & Traversal Auditing</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Layer-by-layer exploration (BFS) and deep-branch search (DFS) for emergency dispatch reachability and partition detection.</div>', unsafe_allow_html=True)

    col_ctrl, col_res = st.columns([1, 2])

    with col_ctrl:
        st.markdown("### Emergency Dispatch Center")
        center_node = st.selectbox("Select Center / Dispatch Hub:", city.nodes, index=0)

        report = get_reachability_report(city.adj_list, center_node)
        components = find_connected_components(city.adj_list)

        st.metric("Network Fully Connected?", "YES" if report["is_fully_connected"] else "NO (Partitioned)")
        st.metric("Reachable Intersections", f"{report['reachable_count']} / {report['total_nodes']}")
        st.metric("Disconnected Sub-Components", len(components))

        st.markdown("#### BFS Exploration Sequence")
        st.write(" ➔ ".join(report["bfs_order"]))

        st.markdown("#### DFS Exploration Sequence")
        st.write(" ➔ ".join(report["dfs_order"]))

    with col_res:
        tab_bfs, tab_dfs, tab_levels = st.tabs(["🌳 BFS Spanning Tree", "🌲 DFS Deep-Branch Tree", "📊 Hop-Count Distribution"])

        with tab_bfs:
            fig_bfs = plot_city_network(
                city,
                highlight_edges=report["bfs_tree_edges"],
                highlight_nodes=[center_node],
                highlight_color="#7C3AED",
                highlight_label="BFS Spanning Tree",
                title=f"BFS Minimum-Hop Spanning Tree from {city.node_info[center_node]['name']}"
            )
            st.pyplot(fig_bfs)

        with tab_dfs:
            fig_dfs = plot_city_network(
                city,
                highlight_edges=report["dfs_tree_edges"],
                highlight_nodes=[center_node],
                highlight_color="#DB2777",
                highlight_label="DFS Exploration Tree",
                title=f"DFS Exploration Tree from {city.node_info[center_node]['name']}"
            )
            st.pyplot(fig_dfs)

        with tab_levels:
            lvl_df = pd.DataFrame([
                {"Intersection": n, "Name": city.node_info[n]["name"], "Zone": city.node_info[n]["zone"], "Hop Distance from Center": lvl}
                for n, lvl in report["bfs_levels"].items()
            ]).sort_values("Hop Distance from Center")
            st.dataframe(lvl_df, use_container_width=True)


# ==============================================================================
# 6. Benchmark & Complexity Suite
# ==============================================================================
elif menu == "📊 Benchmark & Complexity Suite":
    st.markdown('<div class="main-header">📊 Empirical Benchmarking & Asymptotic Complexity Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Empirical runtime scaling of all six algorithms across synthetic city networks from V=10 to V=150.</div>', unsafe_allow_html=True)

    benchmark_csv_path = "data_csv/benchmark_results.csv"
    benchmark_img_path = "graphes/benchmark_comparison.png"

    if os.path.exists(benchmark_csv_path):
        df_bench = pd.read_csv(benchmark_csv_path)
    else:
        st.warning("Benchmark CSV not found. Run analysis/benchmark.py or click 'Run Benchmark' below.")
        df_bench = None

    if st.button("⚡ Re-run Benchmark Suite (V=10 to V=150)"):
        with st.spinner("Executing empirical runs across multiple graph scales..."):
            from analysis.benchmark import run_benchmarks, save_benchmark_csv, generate_benchmark_plots
            res = run_benchmarks()
            save_benchmark_csv(res)
            generate_benchmark_plots(res)
            df_bench = pd.read_csv(benchmark_csv_path)
            st.success("Benchmarks completed and plotted successfully!")

    if df_bench is not None:
        st.markdown("### Empirical Benchmark Metrics (Execution Time in Seconds)")
        st.dataframe(df_bench, use_container_width=True)

        if os.path.exists(benchmark_img_path):
            st.image(benchmark_img_path, caption="Comparative Performance Curves: Dijkstra vs Bellman-Ford & Prim vs Kruskal")

    st.markdown("### Theoretical Complexity Comparison Table")
    complexity_data = [
        {"Algorithm": "Graph Build (List)", "Time Complexity": "O(V + E)", "Space Complexity": "O(V + E)", "Optimal Use Case": "Sparse urban street networks"},
        {"Algorithm": "Graph Build (Matrix)", "Time Complexity": "O(V²)", "Space Complexity": "O(V²)", "Optimal Use Case": "Dense grid downtown networks"},
        {"Algorithm": "Dijkstra's Algorithm", "Time Complexity": "O((V + E) log V)", "Space Complexity": "O(V + E)", "Optimal Use Case": "Standard non-negative travel times"},
        {"Algorithm": "Bellman-Ford Algorithm", "Time Complexity": "O(V * E)", "Space Complexity": "O(V)", "Optimal Use Case": "Negative toll incentives, cycle detection"},
        {"Algorithm": "Breadth-First Search (BFS)", "Time Complexity": "O(V + E)", "Space Complexity": "O(V)", "Optimal Use Case": "Fewest-hop routing & flood reachability"},
        {"Algorithm": "Depth-First Search (DFS)", "Time Complexity": "O(V + E)", "Space Complexity": "O(V)", "Optimal Use Case": "Network partition & cycle detection"},
        {"Algorithm": "Prim's Algorithm (MST)", "Time Complexity": "O(E log V)", "Space Complexity": "O(V + E)", "Optimal Use Case": "Dense network infrastructure maintenance"},
        {"Algorithm": "Kruskal's Algorithm (MST)", "Time Complexity": "O(E log E)", "Space Complexity": "O(V + E)", "Optimal Use Case": "Sparse road network infrastructure"}
    ]
    st.table(pd.DataFrame(complexity_data))


# ==============================================================================
# 7. Academic Documentation
# ==============================================================================
elif menu == "📄 Academic Documentation":
    st.markdown('<div class="main-header">📄 Capstone Project Academic Documentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Comprehensive architectural overview, problem statement, algorithmic designs, and engineering findings.</div>', unsafe_allow_html=True)

    st.markdown(r"""
    ### 1. Executive Summary & Problem Formulation
    Modern urban centers face severe traffic congestion, infrastructure bottlenecks, and capital expenditure constraints.
    This capstone project implements an **Intelligent Smart City Traffic Management and Route Optimization System** (Option A).
    The system models the transportation grid as a weighted graph $G = (V, E)$, where:
    - Vertices $V$ denote key transit intersections, commercial centers, residential districts, and logistics terminals.
    - Edges $E$ denote arterial avenues, expressways, and bypass roads weighted by travel time (minutes).
    
    ### 2. Algorithmic Implementations
    1. **Dual Graph Representation:** Built simultaneously as an **Adjacency List** ($O(V+E)$ space) for fast neighbor traversal and an **Adjacency Matrix** ($O(V^2)$ space) for instant edge presence lookups.
    2. **Dijkstra's Algorithm:** Employs a binary min-heap (`heapq`) to achieve optimal $O((V+E)\log V)$ runtime for rapid real-time navigation.
    3. **Bellman-Ford Algorithm:** Implements edge relaxation over $|V|-1$ passes to evaluate economic incentives (negative toll credits) and catch negative cycles.
    4. **Traffic Congestion Simulation:** Dynamically scales edge weights and computes rerouting thresholds, proving that route choice adapts automatically to incident bottlenecks.
    5. **Network Connectivity Auditing:** Employs BFS (queue-based) for hop-count level partitioning and DFS (recursive/stack-based) for component identification.
    6. **Minimum Spanning Tree Optimization:** Compares Prim's cut-crossing method against Kruskal's Union-Find method with path compression, proving exact cost equivalence and discovering **~45% budget reduction** compared to maintaining all existing roads.
    """)

st.markdown("---")
st.caption("Smart City Traffic Management System | Developed by Bhavya Rattan (Roll No: 2401201004) | Lab 5 Capstone Assignment")
