import flet as ft
import math
import random
from typing import Optional
import flet.canvas as cv    

# ─────────────────────────────────────────────
#  Graph data model
# ─────────────────────────────────────────────

class Vertex:
    def __init__(self, label: str, x: float, y: float):
        self.label = label
        self.x = x
        self.y = y


class Graph:
    def __init__(self):
        self.vertices: dict[str, Vertex] = {}
        self.adjacency: dict[str, set[str]] = {}
        self._counter = 0

    def _next_label(self) -> str:
        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        while self._counter < len(alpha):
            lbl = alpha[self._counter]
            self._counter += 1
            if lbl not in self.vertices:
                return lbl
        n = self._counter - len(alpha) + 1
        self._counter += 1
        return str(n)

    def add_vertex(self, x: float, y: float) -> str:
        lbl = self._next_label()
        self.vertices[lbl] = Vertex(lbl, x, y)
        self.adjacency[lbl] = set()
        return lbl

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
        for s in self.adjacency.values():
            s.discard(label)

    def remove_edge(self, a: str, b: str):
        self.adjacency.get(a, set()).discard(b)
        self.adjacency.get(b, set()).discard(a)

    def clear(self):
        self.vertices.clear()
        self.adjacency.clear()
        self._counter = 0

    def edge_count(self) -> int:
        return sum(len(v) for v in self.adjacency.values()) // 2

    def load_example(self):
        self.clear()
        cx, cy, r, n = 300, 180, 130, 5
        labels = []
        for i in range(n):
            angle = math.pi / 2 + 2 * math.pi * i / n
            x = cx + r * math.cos(angle)
            y = cy - r * math.sin(angle)
            labels.append(self.add_vertex(x, y))
        for i in range(n):
            self.add_edge(labels[i], labels[(i + 1) % n])
        self.add_edge(labels[0], labels[2])
        self.add_edge(labels[0], labels[3])

    # ── Hamiltonian algorithms ───────────────

    def find_hamiltonian_path(self) -> Optional[list[str]]:
        for start in self.vertices:
            path, visited = [start], {start}
            if self._path_bt(path, visited):
                return path
        return None

    def _path_bt(self, path, visited) -> bool:
        if len(path) == len(self.vertices):
            return True
        for nb in sorted(self.adjacency[path[-1]]):
            if nb not in visited:
                path.append(nb); visited.add(nb)
                if self._path_bt(path, visited):
                    return True
                path.pop(); visited.remove(nb)
        return False

    def find_hamiltonian_cycle(self) -> Optional[list[str]]:
        if len(self.vertices) < 3:
            return None
        for start in self.vertices:
            path, visited = [start], {start}
            if self._cycle_bt(path, visited, start):
                return path + [start]
        return None

    def _cycle_bt(self, path, visited, start) -> bool:
        if len(path) == len(self.vertices):
            return start in self.adjacency[path[-1]]
        for nb in sorted(self.adjacency[path[-1]]):
            if nb not in visited:
                path.append(nb); visited.add(nb)
                if self._cycle_bt(path, visited, start):
                    return True
                path.pop(); visited.remove(nb)
        return False


# ─────────────────────────────────────────────
#  Colours
# ─────────────────────────────────────────────
C = dict(
    bg        = "#0f1117",
    panel     = "#1a1d2e",
    canvas    = "#0d0f1a",
    accent    = "#00e676",
    edge_def  = "#3a3a5c",
    edge_hi   = "#00e676",
    vert_fill = "#1b3a2a",
    vert_hi   = "#00c853",
    vert_sel  = "#e53935",
    vert_ring = "#00e676",
    text      = "#ffffff",
    dim       = "#7a7a9a",
    badge_add = "#1565c0",
    badge_del = "#b71c1c",
)

VERT_R = 20   # vertex radius px


# ─────────────────────────────────────────────
#  App
# ─────────────────────────────────────────────

def main(page: ft.Page):
    page.title = "Hamiltonian Graph Visualizer"
    page.bgcolor = C["bg"]
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 780
    page.window.height = 640
    page.window.resizable = True
    page.fonts = {"Mono": "Courier New"}

    graph = Graph()

    # ── mutable state ───────────────────────
    state = dict(mode="normal", edge_src=None)
    hi_verts: set[str] = set()
    hi_edges: set[tuple] = set()

    # ── canvas + overlay ────────────────────
    CANVAS_W, CANVAS_H = 640, 370

    cv = ft.canvas.Canvas(
        width=CANVAS_W, height=CANVAS_H,
        shapes=[])

    # Overlay for vertex labels (ft.canvas has no Text shape)
    overlay = ft.Stack(width=CANVAS_W, height=CANVAS_H, controls=[])

    def redraw():
        shapes = []

        # edges
        for a, nbrs in graph.adjacency.items():
            va = graph.vertices.get(a)
            for b in nbrs:
                if b <= a:
                    continue
                vb = graph.vertices.get(b)
                is_hi = (a, b) in hi_edges or (b, a) in hi_edges
                shapes.append(ft.canvas.Line(
                    va.x, va.y, vb.x, vb.y,
                    paint=ft.Paint(
                        color=C["edge_hi"] if is_hi else C["edge_def"],
                        stroke_width=2.5 if is_hi else 1.5)))

        # vertex circles
        for lbl, v in graph.vertices.items():
            in_hi  = lbl in hi_verts
            is_sel = state["edge_src"] == lbl
            fill   = C["vert_sel"] if is_sel else (C["vert_hi"] if in_hi else C["vert_fill"])
            ring   = C["vert_sel"] if is_sel else C["vert_ring"]

            if in_hi or is_sel:
                shapes.append(ft.canvas.Circle(
                    v.x, v.y, VERT_R + 5,
                    paint=ft.Paint(color=ring + "33",
                                   style=ft.PaintingStyle.FILL)))
            shapes.append(ft.canvas.Circle(
                v.x, v.y, VERT_R,
                paint=ft.Paint(color=fill,
                               style=ft.PaintingStyle.FILL)))
            shapes.append(ft.canvas.Circle(
                v.x, v.y, VERT_R,
                paint=ft.Paint(color=ring, stroke_width=2,
                               style=ft.PaintingStyle.STROKE)))

        cv.shapes = shapes

        # rebuild text overlay
        labels = []
        for lbl, v in graph.vertices.items():
            labels.append(ft.Container(
                content=ft.Text(lbl, size=13, weight=ft.FontWeight.BOLD,
                                color=C["text"], text_align=ft.TextAlign.CENTER),
                left=v.x - VERT_R,
                top=v.y - 10,
                width=VERT_R * 2,
                height=20))
        overlay.controls = labels

        page.update()

    # ── status / mode badge ─────────────────
    status_txt = ft.Text("Vertices: 0  Edges: 0",
                         color=C["dim"], size=12)
    mode_badge = ft.Container(
        content=ft.Text("", size=11, color="#fff"),
        bgcolor=C["badge_add"], border_radius=4,
        padding=ft.padding.symmetric(3, 8), visible=False)

    def update_status():
        status_txt.value = (f"Vertices: {len(graph.vertices)}"
                            f"  Edges: {graph.edge_count()}")
        status_txt.update()

    def set_mode(m: str):
        state["mode"] = m
        state["edge_src"] = None
        if m == "normal":
            mode_badge.visible = False
        else:
            mode_badge.visible = True
            mode_badge.content.value = f"mode: {m.replace('_', ' ')}"
            mode_badge.bgcolor = C["badge_del"] if m == "delete" else C["badge_add"]
        mode_badge.update()

    # ── result bar ──────────────────────────
    result_bar = ft.Container(visible=False, border_radius=6,
                              padding=ft.padding.symmetric(10, 14))

    def show_result(path, is_cycle: bool):
        result_bar.visible = True
        if path is None:
            what = "cycle" if is_cycle else "path"
            result_bar.bgcolor = "#2b1414"
            result_bar.border = ft.border.all(1, "#ff525255")
            result_bar.content = ft.Row([
                ft.Text("✗", color="#ff5252", weight=ft.FontWeight.BOLD, size=14),
                ft.Text(f"No Hamiltonian {what} found.",
                        color="#ff8a80", size=13)])
        else:
            arrow = " → ".join(path)
            label = "Cycle found" if is_cycle else "Path found"
            result_bar.bgcolor = "#0e2318"
            result_bar.border = ft.border.all(1, C["accent"] + "55")
            result_bar.content = ft.Row([
                ft.Text(label, color=C["accent"],
                        weight=ft.FontWeight.BOLD, size=13),
                ft.Text(arrow, color=C["text"],
                        weight=ft.FontWeight.BOLD, size=13),
            ], wrap=True)
        result_bar.update()

    def clear_result():
        result_bar.visible = False
        result_bar.update()
        hi_verts.clear(); hi_edges.clear()

    # ── hit testing ─────────────────────────
    def vert_at(x, y) -> Optional[str]:
        for lbl, v in graph.vertices.items():
            if math.hypot(v.x - x, v.y - y) <= VERT_R + 4:
                return lbl
        return None

    def edge_at(x, y) -> Optional[tuple]:
        TOL = 9
        best, best_d = None, TOL
        for a, nbrs in graph.adjacency.items():
            va = graph.vertices[a]
            for b in nbrs:
                if b <= a: continue
                vb = graph.vertices[b]
                dx, dy = vb.x - va.x, vb.y - va.y
                L2 = dx*dx + dy*dy
                if L2 == 0: continue
                t = max(0, min(1, ((x-va.x)*dx + (y-va.y)*dy) / L2))
                d = math.hypot(va.x+t*dx-x, va.y+t*dy-y)
                if d < best_d:
                    best_d, best = d, (a, b)
        return best

    # ── canvas tap handler ──────────────────
    def on_tap(e: ft.TapEvent):
        x, y = e.local_x, e.local_y
        hit = vert_at(x, y)
        m   = state["mode"]

        if m == "normal":
            if hit is None:
                graph.add_vertex(x, y)
                clear_result(); update_status(); redraw()

        elif m == "add_edge":
            if hit is None: return
            if state["edge_src"] is None:
                state["edge_src"] = hit
                redraw()
            else:
                src = state["edge_src"]; state["edge_src"] = None
                if src != hit and not graph.has_edge(src, hit):
                    graph.add_edge(src, hit)
                    clear_result(); update_status()
                redraw()

        elif m == "delete":
            if hit:
                if state["edge_src"] == hit: state["edge_src"] = None
                graph.remove_vertex(hit)
            else:
                e2 = edge_at(x, y)
                if e2: graph.remove_edge(*e2)
            clear_result(); update_status(); redraw()

    gesture = ft.GestureDetector(
        content=ft.Stack([
            ft.Container(width=CANVAS_W, height=CANVAS_H,
                         bgcolor=C["canvas"], border_radius=8),
            cv,
            overlay,
        ]),
        on_tap=on_tap)

    # ── toolbar ──────────────────────────────
    def tbtn(label, onclick, outlined=False):
        style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(8, 16),
            bgcolor={"": "#252840"} if not outlined else None,
            color={"": C["text"]},
            side={"": ft.BorderSide(1, "#444466")} if outlined else None)
        cls = ft.OutlinedButton if outlined else ft.ElevatedButton
        return cls(label, on_click=onclick, style=style, height=34)

    def on_add_vertex(_):
        set_mode("normal")
        x = random.randint(60, CANVAS_W-60)
        y = random.randint(50, CANVAS_H-50)
        graph.add_vertex(x, y)
        clear_result(); update_status(); redraw()

    def on_add_edge(_):
        set_mode("normal" if state["mode"] == "add_edge" else "add_edge")

    def on_delete(_):
        set_mode("normal" if state["mode"] == "delete" else "delete")

    def on_load(_):
        graph.load_example(); set_mode("normal")
        clear_result(); update_status(); redraw()

    def on_clear(_):
        graph.clear(); set_mode("normal")
        clear_result(); update_status(); redraw()

    def on_find_path(_):
        res = graph.find_hamiltonian_path()
        hi_verts.clear(); hi_edges.clear()
        if res:
            hi_verts.update(res)
            for i in range(len(res)-1):
                hi_edges.add((res[i], res[i+1]))
        show_result(res, False); redraw()

    def on_find_cycle(_):
        res = graph.find_hamiltonian_cycle()
        hi_verts.clear(); hi_edges.clear()
        if res:
            hi_verts.update(res[:-1])
            for i in range(len(res)-1):
                hi_edges.add((res[i], res[i+1]))
        show_result(res, True); redraw()

    toolbar = ft.Row([
        tbtn("Add vertex",    on_add_vertex),
        tbtn("Add edge",      on_add_edge),
        tbtn("Delete",        on_delete),
        tbtn("Load example",  on_load),
        tbtn("Clear",         on_clear),
    ], spacing=6)

    algo_row = ft.Row([
        tbtn("Find Hamiltonian path",  on_find_path,  outlined=True),
        tbtn("Find Hamiltonian cycle", on_find_cycle, outlined=True),
    ], spacing=8)

    def dot(color): return ft.Container(
        width=10, height=10, bgcolor=color, border_radius=5)

    legend = ft.Row([
        ft.Row([dot("#2979ff"), ft.Text("Normal vertex",       size=11, color=C["dim"])], spacing=4),
        ft.Row([dot(C["vert_hi"]),  ft.Text("In path/cycle",   size=11, color=C["dim"])], spacing=4),
        ft.Row([dot(C["vert_sel"]), ft.Text("Selected (edge mode)", size=11, color=C["dim"])], spacing=4),
    ], spacing=16)

    layout = ft.Container(
        ft.Column([
            ft.Container(
                ft.Column([
                    toolbar,
                    gesture,
                    ft.Row([status_txt, mode_badge], spacing=10),
                    algo_row,
                    result_bar,
                    legend,
                ], spacing=10),
                bgcolor=C["panel"], border_radius=10, padding=16)
        ]),
        padding=20)

    page.add(layout)

    # load example on start
    graph.load_example()
    update_status()
    redraw()


ft.app(target=main)
