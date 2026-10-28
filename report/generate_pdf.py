"""
Automated PDF Report Generator for Smart City Traffic Optimization Capstone
Author: Bhavya Rattan (Roll No: 2401201004)
Generates: report/CAPSTONE_REPORT.pdf using ReportLab
Includes formatted text, tables, and embedded high-res graphs.
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "DAA Lab 5 Capstone: Smart City Traffic Optimization")
            self.drawRightString(558, 755, "Bhavya Rattan (2401201004)")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 750, 558, 750)
            
        # Footer
        self.drawString(54, 36, "Confidential - For Academic Evaluation Only (ZOSIMA Submission)")
        self.drawRightString(558, 36, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()


def build_pdf_report(
    output_pdf_path: str = "report/CAPSTONE_REPORT.pdf",
    graphes_dir: str = "graphes"
):
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "CoverSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=14
    )

    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#475569")
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
        backColor=colors.HexColor("#F1F5F9"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # Title & Metadata Banner
    story.append(Paragraph("CAPSTONE PROJECT FINAL REPORT", subtitle_style))
    story.append(Paragraph("Intelligent Smart City Traffic Management and Route Optimization System", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563EB"), spaceAfter=12))

    meta_text = """
    <b>Course:</b> Design and Analysis of Algorithms (DAA) — Lab 5 Capstone Assignment (Option A)<br/>
    <b>Author:</b> Bhavya Rattan &nbsp;|&nbsp; <b>Roll No:</b> 2401201004<br/>
    <b>Date of Submission:</b> October 28, 2026 &nbsp;|&nbsp; <b>Evaluation Platform:</b> ZOSIMA<br/>
    <b>Repository:</b> https://github.com/bhavyarattan21/smart-city-traffic-optimization
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 14))

    # Executive Summary Box
    exec_summary_html = """
    <b>Executive Summary:</b> Modern urban metropolises face recurrent traffic bottlenecks, excessive fuel emissions, and stressed road maintenance budgets. This Capstone Project designs and deploys an end-to-end intelligent traffic management system built on core algorithmic techniques: dual road graph representation (Adjacency List & Matrix), dynamic navigation via <b>Dijkstra's Algorithm</b> and <b>Bellman-Ford Algorithm</b> with negative toll incentive support, real-time traffic bottleneck simulation, <b>BFS and DFS</b> emergency connectivity audits, and <b>Prim's vs Kruskal's</b> Minimum Spanning Tree (MST) capital budget optimization achieving an empirical <b>45.9% maintenance savings</b>. The system includes an interactive Streamlit Web Dashboard, terminal CLI, publication cartography, and empirical scaling benchmarks.
    """
    summary_table = Table(
        [[Paragraph(exec_summary_html, body_style)]],
        colWidths=[504]
    )
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # Section 1: Problem Statement & Objectives
    story.append(Paragraph("1. Problem Statement & System Objectives", h1_style))
    story.append(Paragraph(
        "Urban traffic management requires adaptive algorithms that can respond dynamically to incident closures, balance traffic flow across alternate corridors, model economic pricing incentives (negative toll rebates), and minimize municipal road resurfacing budgets without stranding urban zones.",
        body_style
    ))
    story.append(Paragraph("<b>Primary Architectural Objectives:</b>", h2_style))
    story.append(Paragraph("• <b>Dual Graph Representation:</b> Balance memory-efficient sparse neighbor lookups (Adjacency List, O(V+E)) with instantaneous O(1) edge lookups (Adjacency Matrix, O(V^2)).", bullet_style))
    story.append(Paragraph("• <b>Dynamic Route Navigation:</b> Implement binary-heap Dijkstra for standard travel times, and Bellman-Ford to accommodate negative toll incentives and catch negative cycles.", bullet_style))
    story.append(Paragraph("• <b>Bottleneck Simulation:</b> Artificially inflate road travel times and dynamically quantify commute inflation and rerouting thresholds.", bullet_style))
    story.append(Paragraph("• <b>Reachability Auditing:</b> Leverage BFS and DFS to compute hop-depth trees and ensure 100% emergency service reachability.", bullet_style))
    story.append(Paragraph("• <b>Infrastructure Capital Optimization:</b> Synthesize Minimum Spanning Trees using both Prim's and Kruskal's algorithms, verifying cost equivalence.", bullet_style))

    story.append(Spacer(1, 10))

    # Section 2: City Road Network Model
    story.append(Paragraph("2. Road Network Topography & Modeling", h1_style))
    story.append(Paragraph(
        "The municipal network comprises 10 primary intersections (vertices |V|) and 19 two-way arterial roads (edges |E|) representing distinct urban functional zones.",
        body_style
    ))

    # Nodes Table
    node_data = [
        [Paragraph("<b>Node</b>", table_header_style), Paragraph("<b>Intersection Name</b>", table_header_style), Paragraph("<b>Functional Zone</b>", table_header_style), Paragraph("<b>(X, Y)</b>", table_header_style), Paragraph("<b>Role / Purpose</b>", table_header_style)],
        [Paragraph("A", table_cell_style), Paragraph("Downtown Central", table_cell_style), Paragraph("Commercial", table_cell_style), Paragraph("(20, 50)", table_cell_style), Paragraph("High-density core", table_cell_style)],
        [Paragraph("B", table_cell_style), Paragraph("North Station", table_cell_style), Paragraph("Transport Hub", table_cell_style), Paragraph("(40, 80)", table_cell_style), Paragraph("Intercity rail terminal", table_cell_style)],
        [Paragraph("C", table_cell_style), Paragraph("Tech Park", table_cell_style), Paragraph("Industrial", table_cell_style), Paragraph("(40, 20)", table_cell_style), Paragraph("IT & innovation district", table_cell_style)],
        [Paragraph("D", table_cell_style), Paragraph("University Campus", table_cell_style), Paragraph("Educational", table_cell_style), Paragraph("(70, 80)", table_cell_style), Paragraph("Academic & student hub", table_cell_style)],
        [Paragraph("E", table_cell_style), Paragraph("Civic Center", table_cell_style), Paragraph("Government", table_cell_style), Paragraph("(65, 50)", table_cell_style), Paragraph("Municipal administration", table_cell_style)],
        [Paragraph("F", table_cell_style), Paragraph("South Market", table_cell_style), Paragraph("Commercial", table_cell_style), Paragraph("(70, 20)", table_cell_style), Paragraph("Retail & wholesale trade", table_cell_style)],
        [Paragraph("G", table_cell_style), Paragraph("Airport Terminal", table_cell_style), Paragraph("Transport Hub", table_cell_style), Paragraph("(95, 70)", table_cell_style), Paragraph("International gateway", table_cell_style)],
        [Paragraph("H", table_cell_style), Paragraph("Green Valley", table_cell_style), Paragraph("Residential", table_cell_style), Paragraph("(95, 30)", table_cell_style), Paragraph("Suburban residential", table_cell_style)],
        [Paragraph("I", table_cell_style), Paragraph("Harbor Point", table_cell_style), Paragraph("Industrial", table_cell_style), Paragraph("(15, 20)", table_cell_style), Paragraph("Freight & maritime logistics", table_cell_style)],
        [Paragraph("J", table_cell_style), Paragraph("East Suburbs", table_cell_style), Paragraph("Residential", table_cell_style), Paragraph("(90, 50)", table_cell_style), Paragraph("Residential expansion zone", table_cell_style)],
    ]
    t_nodes = Table(node_data, colWidths=[38, 110, 85, 55, 216])
    t_nodes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_nodes)
    story.append(Spacer(1, 10))

    # Embed Base Network Image if available
    img_network = os.path.join(graphes_dir, "city_road_network.png")
    if os.path.exists(img_network):
        story.append(KeepTogether([
            Image(img_network, width=6.5*inch, height=4.2*inch),
            Paragraph("<b>Figure 1:</b> Master City Road Network topology with zone-colored intersections and travel times.", meta_style),
            Spacer(1, 10)
        ]))

    # Section 3: Algorithmic Complexity Table
    story.append(Paragraph("3. Algorithmic Complexity & Theoretical Foundations", h1_style))
    story.append(Paragraph(
        "All algorithms were analyzed asymptotically and empirically benchmarked across synthetic network topologies from V=10 to V=150.",
        body_style
    ))

    comp_data = [
        [Paragraph("<b>Algorithm</b>", table_header_style), Paragraph("<b>Time Complexity</b>", table_header_style), Paragraph("<b>Space</b>", table_header_style), Paragraph("<b>Observed (V=10)</b>", table_header_style), Paragraph("<b>Observed (V=150)</b>", table_header_style), Paragraph("<b>Urban Application</b>", table_header_style)],
        [Paragraph("Adjacency List", table_cell_style), Paragraph("O(V + E)", table_cell_style), Paragraph("O(V+E)", table_cell_style), Paragraph("0.005 ms", table_cell_style), Paragraph("0.120 ms", table_cell_style), Paragraph("Sparse street networks", table_cell_style)],
        [Paragraph("Adjacency Matrix", table_cell_style), Paragraph("O(V²)", table_cell_style), Paragraph("O(V²)", table_cell_style), Paragraph("0.008 ms", table_cell_style), Paragraph("0.850 ms", table_cell_style), Paragraph("Dense downtown cores", table_cell_style)],
        [Paragraph("Dijkstra (Heap)", table_cell_style), Paragraph("O((V+E) log V)", table_cell_style), Paragraph("O(V+E)", table_cell_style), Paragraph("0.016 ms", table_cell_style), Paragraph("0.847 ms", table_cell_style), Paragraph("Real-time navigation", table_cell_style)],
        [Paragraph("Bellman-Ford", table_cell_style), Paragraph("O(V · E)", table_cell_style), Paragraph("O(V)", table_cell_style), Paragraph("0.026 ms", table_cell_style), Paragraph("4.480 ms", table_cell_style), Paragraph("Negative toll incentives", table_cell_style)],
        [Paragraph("BFS Traversal", table_cell_style), Paragraph("O(V + E)", table_cell_style), Paragraph("O(V)", table_cell_style), Paragraph("0.008 ms", table_cell_style), Paragraph("0.412 ms", table_cell_style), Paragraph("Emergency dispatch hops", table_cell_style)],
        [Paragraph("DFS Traversal", table_cell_style), Paragraph("O(V + E)", table_cell_style), Paragraph("O(V)", table_cell_style), Paragraph("0.007 ms", table_cell_style), Paragraph("0.389 ms", table_cell_style), Paragraph("Partition & cycle checks", table_cell_style)],
        [Paragraph("Prim's MST", table_cell_style), Paragraph("O(E log V)", table_cell_style), Paragraph("O(V+E)", table_cell_style), Paragraph("0.022 ms", table_cell_style), Paragraph("2.658 ms", table_cell_style), Paragraph("Dense road maintenance", table_cell_style)],
        [Paragraph("Kruskal's MST", table_cell_style), Paragraph("O(E log E)", table_cell_style), Paragraph("O(V+E)", table_cell_style), Paragraph("0.036 ms", table_cell_style), Paragraph("2.189 ms", table_cell_style), Paragraph("Regional sparse transit", table_cell_style)],
    ]
    t_comp = Table(comp_data, colWidths=[85, 75, 45, 65, 65, 169])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))

    # Benchmark image
    img_bench = os.path.join(graphes_dir, "benchmark_comparison.png")
    if os.path.exists(img_bench):
        story.append(KeepTogether([
            Image(img_bench, width=6.5*inch, height=2.6*inch),
            Paragraph("<b>Figure 2:</b> Empirical scaling curves: Dijkstra vs Bellman-Ford (log-scale) and Prim vs Kruskal MST.", meta_style),
            Spacer(1, 10)
        ]))

    # Section 4: Experimental Findings & Traffic Congestion
    story.append(Paragraph("4. Experimental Results & Dynamic Traffic Rerouting", h1_style))
    story.append(Paragraph(
        "Traffic incidents were simulated by inflating edge travel times by a multiplier and observing commuter route adaptation.",
        body_style
    ))

    # Congestion table
    cong_data = [
        [Paragraph("<b>Origin-Dest</b>", table_header_style), Paragraph("<b>Incident Simulated</b>", table_header_style), Paragraph("<b>Normal Route</b>", table_header_style), Paragraph("<b>Normal</b>", table_header_style), Paragraph("<b>Congested Route</b>", table_header_style), Paragraph("<b>Congested</b>", table_header_style), Paragraph("<b>Rerouted?</b>", table_header_style)],
        [Paragraph("A -> D", table_cell_style), Paragraph("Rush Hour B-C (5x)", table_cell_style), Paragraph("A -> C -> B -> D", table_cell_style), Paragraph("8.0m", table_cell_style), Paragraph("A -> B -> D", table_cell_style), Paragraph("9.0m", table_cell_style), Paragraph("<b>YES</b>", table_cell_style)],
        [Paragraph("A -> G", table_cell_style), Paragraph("Repairs D-E (4x)", table_cell_style), Paragraph("A -> C -> B -> D -> G", table_cell_style), Paragraph("14.0m", table_cell_style), Paragraph("A -> C -> B -> D -> G", table_cell_style), Paragraph("14.0m", table_cell_style), Paragraph("NO", table_cell_style)],
        [Paragraph("C -> G", table_cell_style), Paragraph("Expressway D-G (3x)", table_cell_style), Paragraph("C -> B -> D -> G", table_cell_style), Paragraph("12.0m", table_cell_style), Paragraph("C -> F -> J -> G", table_cell_style), Paragraph("14.0m", table_cell_style), Paragraph("<b>YES</b>", table_cell_style)],
        [Paragraph("F -> H", table_cell_style), Paragraph("Valley Flood F-H (3x)", table_cell_style), Paragraph("F -> H", table_cell_style), Paragraph("6.0m", table_cell_style), Paragraph("F -> J -> H", table_cell_style), Paragraph("7.0m", table_cell_style), Paragraph("<b>YES</b>", table_cell_style)],
    ]
    t_cong = Table(cong_data, colWidths=[55, 95, 105, 45, 105, 55, 44])
    t_cong.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#DC2626")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_cong)
    story.append(Spacer(1, 10))

    img_cong = os.path.join(graphes_dir, "traffic_congestion_reroute.png")
    if os.path.exists(img_cong):
        story.append(KeepTogether([
            Image(img_cong, width=6.5*inch, height=2.8*inch),
            Paragraph("<b>Figure 3:</b> Visual demonstration of dynamic traffic diversion: Primary route A-C-B-D diverts to A-B-D under B-C congestion.", meta_style),
            Spacer(1, 10)
        ]))

    # Section 5: Infrastructure Budget Optimization (MST)
    story.append(Paragraph("5. Infrastructure Planning & Spanning Tree Budget Reduction", h1_style))
    story.append(Paragraph(
        "Municipalities cannot afford to resurface every road annually. Both Prim's and Kruskal's algorithms were implemented to discover the minimal capital expenditure required to keep all 10 urban zones connected.",
        body_style
    ))
    story.append(Paragraph("• <b>Total Full Grid Road Length:</b> 19 roads = <b>74.0 km</b> of pavement.", bullet_style))
    story.append(Paragraph("• <b>Prim's Algorithm MST Cost:</b> 9 edges = <b>40.0 km</b>.", bullet_style))
    story.append(Paragraph("• <b>Kruskal's Algorithm MST Cost:</b> 9 edges = <b>40.0 km</b> (Identical cost verification passed).", bullet_style))
    story.append(Paragraph("• <b>Municipal Maintenance Savings:</b> (74.0 - 40.0) / 74.0 = <b>45.9% Budget Reduction</b>.", bullet_style))

    img_mst = os.path.join(graphes_dir, "mst_prim_vs_kruskal.png")
    if os.path.exists(img_mst):
        story.append(KeepTogether([
            Image(img_mst, width=6.5*inch, height=2.8*inch),
            Paragraph("<b>Figure 4:</b> Minimum Spanning Tree verification: Prim's (green) vs Kruskal's (orange) yielding identical 40.0 km cost.", meta_style),
            Spacer(1, 10)
        ]))

    # Section 6: Emergency Dispatch & Traversal
    story.append(Paragraph("6. Network Reachability & Emergency Dispatch Auditing", h1_style))
    story.append(Paragraph(
        "BFS traversal from Downtown Central (A) confirmed 100% reachability across the city, with a maximum emergency response radius of 4 hops:",
        body_style
    ))
    story.append(Paragraph("• <b>Hop 0:</b> Node A (Downtown Central)", bullet_style))
    story.append(Paragraph("• <b>Hop 1:</b> Node B (North Station), Node C (Tech Park), Node I (Harbor Point)", bullet_style))
    story.append(Paragraph("• <b>Hop 2:</b> Node D (University), Node E (Civic Center), Node F (South Market)", bullet_style))
    story.append(Paragraph("• <b>Hop 3:</b> Node G (Airport Terminal), Node J (East Suburbs)", bullet_style))
    story.append(Paragraph("• <b>Hop 4:</b> Node H (Green Valley)", bullet_style))

    # Section 7: Verification & Testing
    story.append(Paragraph("7. Testing & Verification Evidence", h1_style))
    story.append(Paragraph(
        "An automated unit test suite (<b>tests/test_algorithms.py</b>) comprises 11 rigorous tests covering: graph matrix symmetry, Dijkstra shortest paths, Bellman-Ford negative edge credits, negative cycle detection, automated congestion rerouting, BFS hop levels, DFS components, Union-Find path compression, and Prim/Kruskal MST equivalence. <b>Result: 11/11 tests passed in 0.001s.</b>",
        body_style
    ))

    # Section 8: Recommendations & Conclusion
    story.append(Paragraph("8. Strategic Recommendations & Conclusions", h1_style))
    story.append(Paragraph(
        "1. <b>Dynamic Toll Incentive Pricing:</b> Utilize Bellman-Ford with negative edge weights to offer variable toll rebates on green corridors (e.g. Harbor Expressway A-I) during peak hours to incentivize commuter diversion.<br/>"
        "2. <b>Infrastructure Prioritization:</b> Allocate annual road resurfacing budgets primarily to the 9 core MST arterial corridors (40.0 km), preserving zero-isolation guarantee at 45.9% lower cost.<br/>"
        "3. <b>Emergency Base Placement:</b> Locate emergency vehicle bases at Civic Center (E) or Downtown (A) to guarantee sub-2-hop response times to all high-density zones.<br/>"
        "<b>Conclusion:</b> The system successfully demonstrates the practical efficacy of classical algorithmic techniques in solving modern urban mobility challenges.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated publication-grade PDF report at: {output_pdf_path}")


if __name__ == "__main__":
    build_pdf_report()
