import flet as ft
from itertools import permutations


# ── Core Algorithm ──────────────────────────────────────────────────────────

def build_adjacency(nodes: list[str], edges: list[tuple[str, str]]) -> dict:
    adj = {n: set() for n in nodes}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def find_hamiltonian(nodes: list[str], adj: dict):
    """
    Returns (classification, path_list) where classification is one of:
      'Circuit'  – Hamiltonian Circuit found
      'Path'     – Hamiltonian Path found (no circuit)
      'Neither'  – no Hamiltonian path exists
    Uses backtracking (efficient for small graphs).
    """
    n = len(nodes)
    if n == 0:
        return "Neither", []

    def backtrack(path: list[str], visited: set):
        if len(path) == n:
            # Check circuit: last node connects back to first
            if path[0] in adj[path[-1]]:
                return "Circuit", path[:]
            return "Path", path[:]

        current = path[-1]
        for neighbor in sorted(adj[current]):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                result, found_path = backtrack(path, visited)
                if result in ("Circuit", "Path"):
                    return result, found_path
                path.pop()
                visited.remove(neighbor)
        return "Neither", []

    # Try every starting node
    best_path = None
    for start in sorted(nodes):
        visited = {start}
        result, path = backtrack([start], visited)
        if result == "Circuit":
            return "Circuit", path
        if result == "Path" and best_path is None:
            best_path = path

    if best_path:
        return "Path", best_path
    return "Neither", []


# ── Flet App ─────────────────────────────────────────────────────────────────

def main(page: ft.Page):
    page.title = "Hamiltonian Graph Detector"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0D0D14"
    page.padding = 0
    page.fonts = {
        "Mono": "https://fonts.gstatic.com/s/spacemono/v13/i7dPIFZifjKcF5UAWdDRYEF8RQ.woff2",
        "Display": "https://fonts.gstatic.com/s/orbitron/v31/yMJMMIlzdpvBhQQL_SC3X9yhF25-T1nyGy6BoWgz.woff2",
    }

    # ── State ──
    nodes_list: list[str] = []
    edges_list: list[tuple[str, str]] = []

    # ── Refs / Controls ──
    node_input = ft.TextField(
        hint_text="e.g.  A  or  1",
        border_color="#3A3A5C",
        focused_border_color="#7C6FCD",
        color="#E8E8FF",
        hint_style=ft.TextStyle(color="#555577"),
        bgcolor="#16162A",
        border_radius=8,
        text_size=14,
        font_family="Mono",
        width=200,
    )

    edge_u_input = ft.TextField(
        hint_text="Node U",
        border_color="#3A3A5C",
        focused_border_color="#7C6FCD",
        color="#E8E8FF",
        hint_style=ft.TextStyle(color="#555577"),
        bgcolor="#16162A",
        border_radius=8,
        text_size=14,
        font_family="Mono",
        width=130,
    )

    edge_v_input = ft.TextField(
        hint_text="Node V",
        border_color="#3A3A5C",
        focused_border_color="#7C6FCD",
        color="#E8E8FF",
        hint_style=ft.TextStyle(color="#555577"),
        bgcolor="#16162A",
        border_radius=8,
        text_size=14,
        font_family="Mono",
        width=130,
    )

    nodes_display = ft.Row(wrap=True, spacing=8, run_spacing=8)
    edges_display = ft.Row(wrap=True, spacing=8, run_spacing=8)

    result_classification = ft.Text(
        value="—",
        size=28,
        weight=ft.FontWeight.BOLD,
        font_family="Display",
        color="#7C6FCD",
    )

    result_path = ft.Text(
        value="",
        size=15,
        font_family="Mono",
        color="#A8A8CC",
        selectable=True,
    )

    result_icon = ft.Text(value="🔍", size=48)
    status_msg = ft.Text(value="", size=13, color="#FF6B8A", font_family="Mono")

    def chip(label: str, color: str):
        return ft.Container(
            content=ft.Text(label, size=13, font_family="Mono", color=color),
            bgcolor=color + "22",
            border=ft.border.all(1, color + "66"),
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
        )

    def refresh_displays():
        nodes_display.controls = [chip(n, "#7C6FCD") for n in sorted(nodes_list)]
        edges_display.controls = [chip(f"{u}–{v}", "#3FB8AF") for u, v in edges_list]
        nodes_display.update()
        edges_display.update()

    def add_node(e):
        name = node_input.value.strip()
        if not name:
            status_msg.value = "⚠ Node name cannot be empty."
            status_msg.update()
            return
        if name in nodes_list:
            status_msg.value = f"⚠ Node '{name}' already exists."
            status_msg.update()
            return
        nodes_list.append(name)
        node_input.value = ""
        node_input.update()
        status_msg.value = ""
        status_msg.update()
        refresh_displays()

    def add_edge(e):
        u = edge_u_input.value.strip()
        v = edge_v_input.value.strip()
        if not u or not v:
            status_msg.value = "⚠ Both U and V are required."
            status_msg.update()
            return
        if u not in nodes_list:
            status_msg.value = f"⚠ Node '{u}' not in graph."
            status_msg.update()
            return
        if v not in nodes_list:
            status_msg.value = f"⚠ Node '{v}' not in graph."
            status_msg.update()
            return
        if u == v:
            status_msg.value = "⚠ Self-loops are not allowed."
            status_msg.update()
            return
        if (u, v) in edges_list or (v, u) in edges_list:
            status_msg.value = f"⚠ Edge {u}–{v} already exists."
            status_msg.update()
            return
        edges_list.append((u, v))
        edge_u_input.value = ""
        edge_v_input.value = ""
        edge_u_input.update()
        edge_v_input.update()
        status_msg.value = ""
        status_msg.update()
        refresh_displays()

    def run_detection(e):
        if len(nodes_list) == 0:
            status_msg.value = "⚠ Please add at least one node."
            status_msg.update()
            return
        if len(nodes_list) == 1:
            result_classification.value = "Hamiltonian Path"
            result_classification.color = "#3FB8AF"
            result_icon.value = "✅"
            result_path.value = f"Path: {nodes_list[0]}"
            result_classification.update()
            result_path.update()
            result_icon.update()
            status_msg.value = ""
            status_msg.update()
            return

        adj = build_adjacency(nodes_list, edges_list)
        classification, path = find_hamiltonian(nodes_list, adj)

        if classification == "Circuit":
            result_classification.value = "Hamiltonian Circuit"
            result_classification.color = "#FFD700"
            result_icon.value = "🏆"
            path_str = " → ".join(path) + f" → {path[0]}"
            result_path.value = f"Circuit: {path_str}"
        elif classification == "Path":
            result_classification.value = "Hamiltonian Path"
            result_classification.color = "#3FB8AF"
            result_icon.value = "✅"
            result_path.value = "Path: " + " → ".join(path)
        else:
            result_classification.value = "Neither"
            result_classification.color = "#FF6B8A"
            result_icon.value = "❌"
            result_path.value = "No Hamiltonian path or circuit exists in this graph."

        result_classification.update()
        result_path.update()
        result_icon.update()
        status_msg.value = ""
        status_msg.update()

    def reset_all(e):
        nodes_list.clear()
        edges_list.clear()
        node_input.value = ""
        edge_u_input.value = ""
        edge_v_input.value = ""
        result_classification.value = "—"
        result_classification.color = "#7C6FCD"
        result_path.value = ""
        result_icon.value = "🔍"
        status_msg.value = ""
        refresh_displays()
        for ctrl in [node_input, edge_u_input, edge_v_input,
                     result_classification, result_path, result_icon, status_msg]:
            ctrl.update()

    # Bind Enter key
    node_input.on_submit = add_node

    # ── Layout ──
    def section(title: str, content: ft.Control):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=11, color="#555577", font_family="Mono",
                        weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                content,
            ]),
            bgcolor="#16162A",
            border=ft.border.all(1, "#2A2A40"),
            border_radius=12,
            padding=20,
        )

    def btn(label: str, handler, primary=False):
        return ft.ElevatedButton(
            text=label,
            on_click=handler,
            style=ft.ButtonStyle(
                bgcolor={"": "#7C6FCD" if primary else "#1E1E35"},
                color={"": "#FFFFFF"},
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                overlay_color="#FFFFFF15",
            ),
        )

    header = ft.Container(
        content=ft.Column([
            ft.Text("HAMILTONIAN", size=32, weight=ft.FontWeight.BOLD,
                    font_family="Display", color="#7C6FCD"),
            ft.Text("GRAPH DETECTOR", size=32, weight=ft.FontWeight.BOLD,
                    font_family="Display", color="#E8E8FF"),
            ft.Text("Add nodes & edges, then run detection.",
                    size=13, color="#555577", font_family="Mono"),
        ], spacing=2),
        padding=ft.padding.only(left=32, top=36, right=32, bottom=20),
    )

    node_section = section(
        "① ADD NODES",
        ft.Row([node_input, btn("Add Node", add_node)], spacing=12),
    )

    edge_section = section(
        "② ADD EDGES  (undirected)",
        ft.Column([
            ft.Row([edge_u_input,
                    ft.Text("↔", size=20, color="#3A3A5C"),
                    edge_v_input,
                    btn("Add Edge", add_edge)], spacing=12),
        ]),
    )

    graph_state_section = section(
        "GRAPH STATE",
        ft.Column([
            ft.Text("Nodes", size=11, color="#555577", font_family="Mono"),
            ft.Container(content=nodes_display, min_height=36),
            ft.Divider(color="#2A2A40", height=16),
            ft.Text("Edges", size=11, color="#555577", font_family="Mono"),
            ft.Container(content=edges_display, min_height=36),
        ], spacing=6),
    )

    result_section = ft.Container(
        content=ft.Column([
            ft.Text("CLASSIFICATION RESULT", size=11, color="#555577",
                    font_family="Mono", weight=ft.FontWeight.BOLD),
            ft.Container(height=12),
            ft.Row([
                result_icon,
                ft.Column([result_classification, result_path], spacing=4),
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ]),
        bgcolor="#0F0F1E",
        border=ft.border.all(1, "#7C6FCD44"),
        border_radius=12,
        padding=24,
    )

    action_row = ft.Row([
        btn("⚡  DETECT", run_detection, primary=True),
        btn("↺  RESET", reset_all),
    ], spacing=12)

    body = ft.Column(
        controls=[
            header,
            ft.Container(
                content=ft.Column([
                    node_section,
                    edge_section,
                    graph_state_section,
                    status_msg,
                    action_row,
                    result_section,
                ], spacing=16),
                padding=ft.padding.symmetric(horizontal=32, vertical=8),
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    page.add(body)


ft.app(target=main)
