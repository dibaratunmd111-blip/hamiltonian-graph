import flet as ft


# ── Core Algorithm ───────────────────────────────────────────────────────────

def build_adjacency(nodes, edges):
    adj = {n: set() for n in nodes}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def find_hamiltonian(nodes, adj):
    n = len(nodes)
    if n == 0:
        return "Neither", []

    def backtrack(path, visited):
        if len(path) == n:
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
    page.scroll = ft.ScrollMode.AUTO

    nodes_list = []
    edges_list = []

    # ── Input fields (font_family removed, use text_style instead) ──
    mono_style = ft.TextStyle(font_family="monospace", size=14, color="#E8E8FF")
    hint_style = ft.TextStyle(color="#555577")

    node_input = ft.TextField(
        hint_text="e.g.  A  or  1",
        border_color="#3A3A5C",
        focused_border_color="#7C6FCD",
        color="#E8E8FF",
        hint_style=hint_style,
        bgcolor="#16162A",
        border_radius=8,
        text_size=14,
        text_style=mono_style,
        width=200,
    )

    edge_u_input = ft.TextField(
        hint_text="Node U",
        border_color="#3A3A5C",
        focused_border_color="#7C6FCD",
        color="#E8E8FF",
        hint_style=hint_style,
        bgcolor="#16162A",
        border_radius=8,
        text_size=14,
        text_style=mono_style,
        width=130,
    )

    edge_v_input = ft.TextField(
        hint_text="Node V",
        border_color="#3A3A5C",
        focused_border_color="#7C6FCD",
        color="#E8E8FF",
        hint_style=hint_style,
        bgcolor="#16162A",
        border_radius=8,
        text_size=14,
        text_style=mono_style,
        width=130,
    )

    nodes_display = ft.Row(wrap=True, spacing=8, run_spacing=8)
    edges_display = ft.Row(wrap=True, spacing=8, run_spacing=8)

    result_classification = ft.Text(
        value="—",
        size=26,
        weight=ft.FontWeight.BOLD,
        color="#7C6FCD",
    )
    result_path = ft.Text(
        value="",
        size=14,
        color="#A8A8CC",
        selectable=True,
    )
    result_icon = ft.Text(value="🔍", size=44)
    status_msg  = ft.Text(value="", size=13, color="#FF6B8A")

    def chip(label, color):
        return ft.Container(
            content=ft.Text(label, size=13, color=color),
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
            status_msg.value = "⚠  Node name cannot be empty."
            status_msg.update(); return
        if name in nodes_list:
            status_msg.value = f"⚠  Node '{name}' already exists."
            status_msg.update(); return
        nodes_list.append(name)
        node_input.value = ""
        node_input.update()
        status_msg.value = ""; status_msg.update()
        refresh_displays()

    def add_edge(e):
        u = edge_u_input.value.strip()
        v = edge_v_input.value.strip()
        if not u or not v:
            status_msg.value = "⚠  Both U and V are required."
            status_msg.update(); return
        if u not in nodes_list:
            status_msg.value = f"⚠  Node '{u}' not in graph."
            status_msg.update(); return
        if v not in nodes_list:
            status_msg.value = f"⚠  Node '{v}' not in graph."
            status_msg.update(); return
        if u == v:
            status_msg.value = "⚠  Self-loops are not allowed."
            status_msg.update(); return
        if (u, v) in edges_list or (v, u) in edges_list:
            status_msg.value = f"⚠  Edge {u}–{v} already exists."
            status_msg.update(); return
        edges_list.append((u, v))
        edge_u_input.value = ""; edge_v_input.value = ""
        edge_u_input.update(); edge_v_input.update()
        status_msg.value = ""; status_msg.update()
        refresh_displays()

    def run_detection(e):
        if not nodes_list:
            status_msg.value = "⚠  Please add at least one node."
            status_msg.update(); return
        if len(nodes_list) == 1:
            result_classification.value = "Hamiltonian Path"
            result_classification.color  = "#3FB8AF"
            result_icon.value  = "✅"
            result_path.value  = f"Path:  {nodes_list[0]}"
        else:
            adj = build_adjacency(nodes_list, edges_list)
            classification, path = find_hamiltonian(nodes_list, adj)
            if classification == "Circuit":
                result_classification.value = "Hamiltonian Circuit"
                result_classification.color  = "#FFD700"
                result_icon.value = "🏆"
                result_path.value = "Circuit:  " + " → ".join(path) + f" → {path[0]}"
            elif classification == "Path":
                result_classification.value = "Hamiltonian Path"
                result_classification.color  = "#3FB8AF"
                result_icon.value = "✅"
                result_path.value = "Path:  " + " → ".join(path)
            else:
                result_classification.value = "Neither"
                result_classification.color  = "#FF6B8A"
                result_icon.value = "❌"
                result_path.value = "No Hamiltonian path or circuit exists in this graph."

        for c in [result_classification, result_path, result_icon]:
            c.update()
        status_msg.value = ""; status_msg.update()

    def reset_all(e):
        nodes_list.clear(); edges_list.clear()
        node_input.value = edge_u_input.value = edge_v_input.value = ""
        result_classification.value = "—"; result_classification.color = "#7C6FCD"
        result_path.value = ""; result_icon.value = "🔍"; status_msg.value = ""
        refresh_displays()
        for c in [node_input, edge_u_input, edge_v_input,
                  result_classification, result_path, result_icon, status_msg]:
            c.update()

    node_input.on_submit = add_node

    # ── Helper builders ──
    def mk_btn(label, handler, primary=False):
        return ft.Button(
            content=ft.Text(label, size=13, weight=ft.FontWeight.W_600, color="#FFFFFF"),
            bgcolor="#7C6FCD" if primary else "#1E1E35",
            on_click=handler,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                overlay_color="#FFFFFF15",
            ),
        )

    def section(title, content):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=11, color="#555577", weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                content,
            ]),
            bgcolor="#16162A",
            border=ft.border.all(1, "#2A2A40"),
            border_radius=12,
            padding=20,
        )

    # ── Page layout ──
    page.add(
        ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Column([
                        ft.Text("HAMILTONIAN", size=30, weight=ft.FontWeight.BOLD, color="#7C6FCD"),
                        ft.Text("GRAPH DETECTOR", size=30, weight=ft.FontWeight.BOLD, color="#E8E8FF"),
                        ft.Text("Add nodes & edges, then run detection.",
                                size=13, color="#555577"),
                    ], spacing=2),
                    padding=ft.padding.only(left=32, top=36, right=32, bottom=20),
                ),

                ft.Container(
                    content=ft.Column([

                        section(
                            "①  ADD NODES",
                            ft.Row([node_input, mk_btn("Add Node", add_node)], spacing=12),
                        ),

                        section(
                            "②  ADD EDGES  (undirected)",
                            ft.Row([
                                edge_u_input,
                                ft.Text("↔", size=20, color="#3A3A5C"),
                                edge_v_input,
                                mk_btn("Add Edge", add_edge),
                            ], spacing=12),
                        ),

                        section(
                            "GRAPH STATE",
                            ft.Column([
                                ft.Text("Nodes", size=11, color="#555577"),
                                ft.Container(content=nodes_display, min_height=36),
                                ft.Divider(color="#2A2A40", height=16),
                                ft.Text("Edges", size=11, color="#555577"),
                                ft.Container(content=edges_display, min_height=36),
                            ], spacing=6),
                        ),

                        status_msg,

                        ft.Row([
                            mk_btn("⚡  DETECT", run_detection, primary=True),
                            mk_btn("↺  RESET",  reset_all),
                        ], spacing=12),

                        # Result box
                        ft.Container(
                            content=ft.Column([
                                ft.Text("CLASSIFICATION RESULT", size=11,
                                        color="#555577", weight=ft.FontWeight.BOLD),
                                ft.Container(height=12),
                                ft.Row([
                                    result_icon,
                                    ft.Column([result_classification, result_path], spacing=4),
                                ], spacing=16,
                                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ]),
                            bgcolor="#0F0F1E",
                            border=ft.border.all(1, "#7C6FCD44"),
                            border_radius=12,
                            padding=24,
                        ),

                    ], spacing=16),
                    padding=ft.padding.symmetric(horizontal=32, vertical=8),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    )


ft.app(target=main)
