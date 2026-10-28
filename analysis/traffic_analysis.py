"""
Traffic Congestion Impact & Bottleneck Analysis
Author: Bhavya Rattan (Roll No: 2401201004)
Repository: bhavyarattan21/smart-city-traffic-optimization

Simulates urban traffic congestion across predefined real-world scenarios,
quantifies travel delay, rerouting behavior, and system bottlenecks.
"""

import csv
import os
from algorithms.graph_model import CityGraph
from algorithms.shortest_path import analyze_traffic_impact


def run_traffic_scenario_analysis(
    nodes_csv: str = "data_csv/city_nodes.csv",
    roads_csv: str = "data_csv/city_roads.csv",
    scenarios_csv: str = "data_csv/congested_scenarios.csv",
    output_csv: str = "data_csv/traffic_impact_results.csv"
):
    city = CityGraph.load_from_csv(nodes_csv, roads_csv, directed=False)
    scenarios = []

    with open(scenarios_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scenarios.append(row)

    results = []
    print("\nRunning City Traffic Congestion Scenarios...")
    print(f"{'Scenario':<30} | {'Edge':<8} | {'Mult':<5} | {'Original Time':<14} | {'Congested Time':<15} | {'Delay':<8} | {'Rerouted?'}")
    print("-" * 105)

    # Key origin-destination pairs to evaluate
    od_pairs = [
        ("A", "D"),  # Downtown to University
        ("A", "G"),  # Downtown to Airport
        ("C", "G"),  # Tech Park to Airport
        ("I", "H"),  # Harbor to Green Valley
        ("B", "J"),  # North Station to East Suburbs
    ]

    for scen in scenarios:
        c_edge = (scen["source"], scen["target"])
        mult = float(scen["multiplier"])
        name = scen["scenario_name"]

        for orig, dest in od_pairs:
            impact = analyze_traffic_impact(
                city.adj_list,
                source=orig,
                target=dest,
                congested_edges={c_edge},
                multiplier=mult
            )

            # Only record if the scenario impacted or was relevant to the OD pair
            results.append({
                "scenario_id": scen["scenario_id"],
                "scenario_name": name,
                "congested_edge": f"{c_edge[0]}-{c_edge[1]}",
                "multiplier": mult,
                "origin": orig,
                "destination": dest,
                "original_route": " -> ".join(impact["before_path"]),
                "original_time_mins": impact["before_cost"],
                "congested_route": " -> ".join(impact["after_path"]),
                "congested_time_mins": impact["after_cost"],
                "delay_mins": impact["delay_minutes"],
                "pct_increase": impact["percentage_increase"],
                "rerouted": impact["rerouted"]
            })

            if impact["delay_minutes"] > 0:
                print(
                    f"{name[:28]:<30} | {c_edge[0]}-{c_edge[1]:<6} | {mult:<5} | "
                    f"{impact['before_cost']:<14.1f} | {impact['after_cost']:<15.1f} | "
                    f"+{impact['delay_minutes']:<7.1f} | {str(impact['rerouted']):<5}"
                )

    # Save to CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved comprehensive traffic impact analysis to {output_csv}")
    return results


if __name__ == "__main__":
    run_traffic_scenario_analysis()
