import flet as ft
import math
import random
from typing import Optional
import flet.canvas as cv

# ── Data model ──────────────────────────────────────────────────────────────

class Vertex:
    def __init__(self, label: str, x: float, y: float):
        self.label = label
        self.x = x
        self.y = y


class Graph:
    def __init__(self):
        self.vertices: dict[str, Vertex] = {}
        self.adjacency: dict[str, set[str]] = {}
        self._label_counter = 0

    def _next_label(self) -> str:
        labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        while self._label_counter < len(labels):
            lbl = labels[self._label_counter]
            self._label_counter += 1
            if lbl not in self.vertices:
                return lbl
        # fallback: numeric labels
        n = self._label_counter - len(labels) + 1
        self._label_counter += 1
        return str(n)

    def add_vertex(self, x: float, y: float) -> str:
        label = self._next_label()
        self.vertices[label] = Vertex(label, x, y)
        self.adjacency[label] = set()
        return label

    def add_edge(self, a: str, b: str):
        if a != b and a in self.vertices and b in self.vertices:
            self.adjacency[a].add(b)
            self.adjacency[b].add(a)

    def has_edge(self, a: str, b: str) -> bool:
        return b in self.adjacency.get(a, set())

    def remove_vertex(self, label: str):
        if label not in self.vertices:
            return
        del self.vertices[label]
        del self.adjacency[label]
        for nbrs in self.adjacency.values():
            nbrs.discard(label)

    def remove_edge(self, a: str, b: str):
        self.adjacency.get(a, set()).discard(b)
        self.adjacency.get(b, set()).discard(a)

    def clear(self):
        self.vertices.clear()
        self.adjacency.clear()
        self._label_counter = 0

    def load_example(self):
        self.clear()
        cx, cy = 300, 200
        r = 130
        n = 5
        labels = []
        for i in range(n):
            angle = math.pi / 2 + (2 * math.pi * i / n)
            x = cx + r * math.cos(angle)
            y = cy - r * math.sin(angle)
            lbl = self.add_vertex(x, y)
            labels.append(lbl)
        # pentagon edges
        for i in range(n):
            self.add_edge(labels[i], labels[(i + 1) % n])
        # diagonals: A-C, A-D (indices 0-2, 0-3)
        self.add_edge(labels[0], labels[2])
        self.add_edge(labels[0], labels[3])

    # ── Hamiltonian algorithms ───────────────────────────────────────────────

    def find_hamiltonian_path(self) -> Optional[list[str]]:
        verts = list(self.vertices.keys())
        for start in verts:
            path = [start]
            visited = {start}
            if self._ham_path_bt(path, visited, verts):
                return path
        return None

    def _ham_path_bt(self, path, visited, verts) -> bool:
        if len(path) == len(verts):
            return True
        current = path[-1]
        for nbr in sorted(self.adjacency[current]):
            if nbr not in visited:
                path.append(nbr)
                visited.add(nbr)
                if self._ham_path_bt(path, visited, verts):
                    return True
                path.pop()
                visited.remove(nbr)
        return False

    def find_hamiltonian_cycle(self) -> Optional[list[str]]:
        verts = list(self.vertices.keys())
        if len(verts) < 3:
            return None
        for start in verts:
            path = [start]
            visited = {start}
            if self._ham_cycle_bt(path, visited, verts, start):
                return path + [start]
        return None

    def _ham_cycle_bt(self, path, visited, verts, start) -> bool:
        if len(path) == len(verts):
            return start in self.adjacency[path[-1]]
        current = path[-1]
        for nbr in sorted(self.adjacency[current]):
            if nbr not in visited:
                path.append(nbr)
                visited.add(nbr)
                if self._ham_cycle_bt(path, visited, verts, start):
                    return True
                path.pop()
                visited.remove(nbr)
        return False


# ── Flet App ─────────────────────────────────────────────────────────────────

CANVAS_W = 620
CANVAS_H = 360

# colour palette (dark theme)
BG_DARK   = "#1a1a2e"
BG_PANEL  = "#16213e"
BG_CANVAS = "#0d0d0d"
ACCENT    = "#00e676"        # bright green
EDGE_DEF  = "#444444"
EDGE_PATH = "#00e676"
VERT_DEF  = "#1e3a1e"
VERT_PATH = "#00c853"
VERT_SEL  = "#ff5252"
TEXT_DEF  = "#ffffff"
TEXT_DIM  = "#888888"
BADGE_BG  = "#e65100"


def main(page: ft.Page):
    page.title = "Hamiltonian Graph Visualizer"
    page.bgcolor = BG_DARK
    page.padding = 0
    page.window.width = 720
    page.window.height = 600
    page.window.resizable = True
    page.theme_mode = ft.ThemeMode.DARK

    graph = Graph()

    # ── state ─────────────────────────────────────────────────────────────
    mode = {"value": "normal"}   # normal | add_edge | delete
    edge_first: dict = {"v": None}
    highlight_path: list[str] = []
    highlight_edges: set[tuple[str, str]] = set()
    result_text = {"msg": "", "found": False}

    # ── canvas drawing ────────────────────────────────────────────────────
    canvas = cv.Canvas(width=CANVAS_W, height=CANVAS_H)

    def make_arrow_str(path: list[str]) -> str:
        return " → ".join(path)

    def redraw():
        shapes: list[ft.canvas.Shape] = []

        # edges
        for a, nbrs in graph.adjacency.items():
            va = graph.vertices.get(a)
            if not va:
                continue
            for b in nbrs:
                if b <= a:
                    continue
                vb = graph.vertices.get(b)
                if not vb:
                    continue
                is_path_edge = (
                    (a, b) in highlight_edges or (b, a) in highlight_edges
                )
                color = EDGE_PATH if is_path_edge else EDGE_DEF
                width = 2.5 if is_path_edge else 1.5
                shapes.append(ft.canvas.Line(va.x, va.y, vb.x, vb.y,
                    paint=ft.Paint(color=color, stroke_width=width)))

        # vertices
        R = 18
        for lbl, v in graph.vertices.items():
            in_path = lbl in highlight_path
            sel = edge_first["v"] == lbl
            if sel:
                fill = VERT_SEL
                ring = VERT_SEL
            elif in_path:
                fill = VERT_PATH
                ring = ACCENT
            else:
                fill = VERT_DEF
                ring = ACCENT

            # glow ring when in path
            if in_path or sel:
                shapes.append(ft.canvas.Circle(v.x, v.y, R + 4,
                    paint=ft.Paint(color=ring + "40",
                                   style=ft.PaintingStyle.FILL)))
            # circle
            shapes.append(ft.canvas.Circle(v.x, v.y, R,
                paint=ft.Paint(color=fill, style=ft.PaintingStyle.FILL)))
            shapes.append(ft.canvas.Circle(v.x, v.y, R,
                paint=ft.Paint(color=ring, stroke_width=2,
                               style=ft.PaintingStyle.STROKE)))
            # label
            shapes.append(ft.canvas.Text(
                v.x - 6, v.y - 8, lbl,
                style=ft.TextStyle(color=TEXT_DEF, size=14,
                                   weight=ft.FontWeight.BOLD)))

        canvas.shapes = shapes
        canvas.update()

    # ── status bar ────────────────────────────────────────────────────────
    status_label = ft.Text(
        f"Vertices: {len(graph.vertices)}  Edges: {sum(len(v) for v in graph.adjacency.values()) // 2}",
        color=TEXT_DIM, size=12)

    mode_badge = ft.Container(
        content=ft.Text("mode: normal", size=11, color="#ffffff"),
        bgcolor="#444444", border_radius=4, padding=ft.padding.symmetric(4, 8),
        visible=False)

    def update_status():
        e_count = sum(len(v) for v in graph.adjacency.values()) // 2
        status_label.value = (
            f"Vertices: {len(graph.vertices)}  "
            f"Edges: {e_count}")
        status_label.update()

    def set_mode(m: str):
        mode["value"] = m
        edge_first["v"] = None
        if m == "normal":
            mode_badge.visible = False
        else:
            mode_badge.visible = True
            mode_badge.content.value = f"mode: {m.replace('_', ' ')}"
            mode_badge.bgcolor = BADGE_BG if m == "delete" else "#1565c0"
        mode_badge.update()

    # ── result panel ──────────────────────────────────────────────────────
    result_row = ft.Container(
        visible=False,
        bgcolor="#1b2e1b",
        border=ft.border.all(1, ACCENT + "60"),
        border_radius=6,
        padding=ft.padding.symmetric(10, 14),
        content=ft.Row([], spacing=8))

    def show_result(path: Optional[list[str]], is_cycle: bool):
        if path is None:
            result_row.bgcolor = "#2e1b1b"
            result_row.border = ft.border.all(1, "#ff525260")
            msg = "No Hamiltonian " + ("cycle" if is_cycle else "path") + " found."
            result_row.content = ft.Row([
                ft.Text("✗", color="#ff5252", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(msg, color="#ff8a80", size=13)])
        else:
            result_row.bgcolor = "#1b2e1b"
            result_row.border = ft.border.all(1, ACCENT + "60")
            label = "Cycle found" if is_cycle else "Path found"
            arrow = make_arrow_str(path)
            result_row.content = ft.Row([
                ft.Text(label, color=ACCENT, size=13,
                        weight=ft.FontWeight.BOLD),
                ft.Text(arrow, color="#ffffff", size=13,
                        weight=ft.FontWeight.BOLD)])
        result_row.visible = True
        result_row.update()

    def clear_result():
        result_row.visible = False
        result_row.update()
        highlight_path.clear()
        highlight_edges.clear()

    # ── hit-test helper ───────────────────────────────────────────────────
    def vertex_at(x: float, y: float) -> Optional[str]:
        for lbl, v in graph.vertices.items():
            if math.hypot(v.x - x, v.y - y) <= 20:
                return lbl
        return None

    def edge_at(x: float, y: float) -> Optional[tuple[str, str]]:
        """Return the (a, b) edge closest to (x,y) within tolerance."""
        TOLERANCE = 8
        best = None
        best_d = TOLERANCE
        for a, nbrs in graph.adjacency.items():
            va = graph.vertices.get(a)
            for b in nbrs:
                if b <= a:
                    continue
                vb = graph.vertices.get(b)
                dx, dy = vb.x - va.x, vb.y - va.y
                length = math.hypot(dx, dy)
                if length == 0:
                    continue
                t = ((x - va.x) * dx + (y - va.y) * dy) / (length * length)
                t = max(0, min(1, t))
                px = va.x + t * dx - x
                py = va.y + t * dy - y
                d = math.hypot(px, py)
                if d < best_d:
                    best_d = d
                    best = (a, b)
        return best

    # ── canvas interaction ────────────────────────────────────────────────
    def on_canvas_tap(e: ft.TapEvent):
        x, y = e.local_x, e.local_y
        hit = vertex_at(x, y)
        m = mode["value"]

        if m == "normal":
            # add vertex on empty canvas click
            if hit is None:
                graph.add_vertex(x, y)
                clear_result()
                update_status()
                redraw()

        elif m == "add_edge":
            if hit is None:
                return
            if edge_first["v"] is None:
                edge_first["v"] = hit
                redraw()
            else:
                first = edge_first["v"]
                edge_first["v"] = None
                if first != hit and not graph.has_edge(first, hit):
                    graph.add_edge(first, hit)
                    clear_result()
                    update_status()
                redraw()

        elif m == "delete":
            if hit:
                graph.remove_vertex(hit)
                if edge_first["v"] == hit:
                    edge_first["v"] = None
                clear_result()
                update_status()
                redraw()
            else:
                edge = edge_at(x, y)
                if edge:
                    graph.remove_edge(*edge)
                    clear_result()
                    update_status()
                    redraw()

    canvas_gesture = ft.GestureDetector(
        content=ft.Stack([
            ft.Container(width=CANVAS_W, height=CANVAS_H, bgcolor=BG_CANVAS,
                         border_radius=8),
            canvas]),
        on_tap=on_canvas_tap)

    # ── toolbar buttons ────────────────────────────────────────────────────
    def btn(label, on_click, bgcolor="#2a2a3e", color=TEXT_DEF):
        return ft.ElevatedButton(
            label,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor={"": bgcolor},
                color={"": color},
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.padding.symmetric(8, 16)),
            height=34)

    def on_add_vertex(_):
        set_mode("normal")
        # place randomly in canvas
        x = random.randint(60, CANVAS_W - 60)
        y = random.randint(40, CANVAS_H - 40)
        graph.add_vertex(x, y)
        clear_result()
        update_status()
        redraw()

    def on_add_edge(_):
        if mode["value"] == "add_edge":
            set_mode("normal")
        else:
            set_mode("add_edge")

    def on_delete(_):
        if mode["value"] == "delete":
            set_mode("normal")
        else:
            set_mode("delete")

    def on_load_example(_):
        graph.load_example()
        set_mode("normal")
        clear_result()
        update_status()
        redraw()

    def on_clear(_):
        graph.clear()
        set_mode("normal")
        clear_result()
        update_status()
        redraw()

    def on_find_path(_):
        result = graph.find_hamiltonian_path()
        highlight_path.clear()
        highlight_edges.clear()
        if result:
            highlight_path.extend(result)
            for i in range(len(result) - 1):
                highlight_edges.add((result[i], result[i + 1]))
        show_result(result, is_cycle=False)
        redraw()

    def on_find_cycle(_):
        result = graph.find_hamiltonian_cycle()
        highlight_path.clear()
        highlight_edges.clear()
        if result:
            highlight_path.extend(result[:-1])   # don't double-count start
            for i in range(len(result) - 1):
                highlight_edges.add((result[i], result[i + 1]))
        show_result(result, is_cycle=True)
        redraw()

    toolbar = ft.Row([
        btn("Add vertex", on_add_vertex),
        btn("Add edge",   on_add_edge),
        btn("Delete",     on_delete),
        btn("Load example", on_load_example),
        btn("Clear",      on_clear),
    ], spacing=6)

    algo_row = ft.Row([
        ft.OutlinedButton(
            "Find Hamiltonian path",
            on_click=on_find_path,
            style=ft.ButtonStyle(
                color={"": TEXT_DEF},
                side={"": ft.BorderSide(1, "#555555")},
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.padding.symmetric(8, 16)),
            height=36),
        ft.OutlinedButton(
            "Find Hamiltonian cycle",
            on_click=on_find_cycle,
            style=ft.ButtonStyle(
                color={"": TEXT_DEF},
                side={"": ft.BorderSide(1, "#555555")},
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.padding.symmetric(8, 16)),
            height=36),
    ], spacing=8)

    legend = ft.Row([
        ft.Row([ft.Container(width=10, height=10, bgcolor="#448aff",
                             border_radius=5), ft.Text("Normal vertex", size=11, color=TEXT_DIM)], spacing=4),
        ft.Row([ft.Container(width=10, height=10, bgcolor=VERT_PATH,
                             border_radius=5), ft.Text("In path/cycle", size=11, color=TEXT_DIM)], spacing=4),
        ft.Row([ft.Container(width=10, height=10, bgcolor=VERT_SEL,
                             border_radius=5), ft.Text("Selected (edge mode)", size=11, color=TEXT_DIM)], spacing=4),
    ], spacing=16)

    layout = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Column([
                    toolbar,
                    canvas_gesture,
                    ft.Row([status_label, mode_badge], spacing=10),
                    algo_row,
                    result_row,
                    legend,
                ], spacing=10),
                bgcolor=BG_PANEL,
                border_radius=10,
                padding=16,
            )
        ]),
        padding=20)

    page.add(layout)

    # load example on start
    graph.load_example()
    update_status()
    redraw()


ft.app(target=main)
