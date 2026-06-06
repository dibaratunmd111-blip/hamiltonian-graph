import flet as ft
import math
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

        def _next_label(self) -> str:
            alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            used = set(self.vertices.keys())
            for ch in alpha:
                if ch not in used:
                    return ch
            i = 1
            while str(i) in used:
                i += 1
            return str(i)

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

        def edge_count(self) -> int:
            return sum(len(v) for v in self.adjacency.values()) // 2

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
        edge_draft= "#f9a825",       # edge being drawn (first vertex selected)
        vert_fill = "#152a20",
        vert_hi   = "#00c853",
        vert_sel  = "#e53935",
        vert_norm = "#2979ff",
        text      = "#ffffff",
        dim       = "#7a7a9a",
        badge_add = "#1565c0",
        badge_del = "#b71c1c",
        badge_edge= "#6a1eb0",
    )

    VERT_R   = 20
    CANVAS_W = 640
    CANVAS_H = 390


    # ─────────────────────────────────────────────
    #  App
    # ─────────────────────────────────────────────

    def main(page: ft.Page):
        page.title  = "Hamiltonian Graph Visualizer"
        page.bgcolor = C["bg"]
        page.padding = 0
        page.theme_mode = ft.ThemeMode.DARK
        page.window.width  = 780
        page.window.height = 700
        page.window.resizable = True

        # ── two graphs: draft (building) and loaded (locked) ──
        draft  = Graph()   # user is building this
        loaded = Graph()   # snapshot after pressing Load

        state = dict(
            mode      = "normal",   # normal | add_edge | delete
            edge_src  = None,
            is_loaded = False,      # True once Load has been pressed
        )

        hi_verts: set[str] = set()
        hi_edges: set[tuple] = set()

        # ── canvas widgets ───────────────────────
        cv      = ft.canvas.Canvas(width=CANVAS_W, height=CANVAS_H, shapes=[])
        overlay = ft.Stack(width=CANVAS_W, height=CANVAS_H, controls=[])

        hint = ft.Container(
            content=ft.Text(
                "Click on the canvas to place a vertex",
                color=C["dim"], size=13, italic=True,
                text_align=ft.TextAlign.CENTER),
            width=CANVAS_W, height=CANVAS_H,
            alignment=ft.alignment.center,
            visible=True)

        # ── which graph is active for display ───
        def active() -> Graph:
            return loaded if state["is_loaded"] else draft

        def redraw():
            g = active()
            hint.visible = len(g.vertices) == 0
            shapes = []

            # edges
            for a, nbrs in g.adjacency.items():
                va = g.vertices.get(a)
                for b in nbrs:
                    if b <= a:
                        continue
                    vb = g.vertices.get(b)
                    is_hi = (a, b) in hi_edges or (b, a) in hi_edges
                    shapes.append(ft.canvas.Line(
                        va.x, va.y, vb.x, vb.y,
                        paint=ft.Paint(
                            color=C["edge_hi"] if is_hi else C["edge_def"],
                            stroke_width=2.5 if is_hi else 1.5)))

            # vertices
            for lbl, v in g.vertices.items():
                in_hi  = lbl in hi_verts
                is_sel = state["edge_src"] == lbl and not state["is_loaded"]
                fill   = C["vert_fill"]
                ring   = C["vert_sel"] if is_sel else (C["vert_hi"] if in_hi else C["vert_norm"])

                if in_hi or is_sel:
                    shapes.append(ft.canvas.Circle(
                        v.x, v.y, VERT_R + 6,
                        paint=ft.Paint(color=ring + "33",
                                    style=ft.PaintingStyle.FILL)))
                shapes.append(ft.canvas.Circle(
                    v.x, v.y, VERT_R,
                    paint=ft.Paint(color=fill, style=ft.PaintingStyle.FILL)))
                shapes.append(ft.canvas.Circle(
                    v.x, v.y, VERT_R,
                    paint=ft.Paint(color=ring, stroke_width=2,
                                style=ft.PaintingStyle.STROKE)))

            cv.shapes = shapes

            label_controls = []
            for lbl, v in g.vertices.items():
                label_controls.append(ft.Container(
                    content=ft.Text(lbl, size=13, weight=ft.FontWeight.BOLD,
                                    color=C["text"],
                                    text_align=ft.TextAlign.CENTER),
                    left=v.x - VERT_R,
                    top=v.y - 10,
                    width=VERT_R * 2,
                    height=20))
            overlay.controls = label_controls
            page.update()

        # ── status / mode badge ──────────────────
        status_txt = ft.Text("Vertices: 0  Edges: 0", color=C["dim"], size=12)
        mode_badge = ft.Container(
            content=ft.Text("", size=11, color="#fff"),
            bgcolor=C["badge_add"], border_radius=4,
            padding=ft.padding.symmetric(3, 8), visible=False)
        loaded_badge = ft.Container(
            content=ft.Text("● Graph loaded", size=11, color="#fff"),
            bgcolor="#2e7d32", border_radius=4,
            padding=ft.padding.symmetric(3, 8), visible=False)

        def update_status():
            g = active()
            status_txt.value = (f"Vertices: {len(g.vertices)}"
                                f"  Edges: {g.edge_count()}")
            status_txt.update()

        def set_mode(m: str):
            state["mode"] = m
            state["edge_src"] = None
            if m == "normal":
                mode_badge.visible = False
            else:
                mode_badge.visible = True
                mode_badge.content.value = f"mode: {m.replace('_', ' ')}"
                if m == "delete":
                    mode_badge.bgcolor = C["badge_del"]
                elif m == "add_edge":
                    mode_badge.bgcolor = C["badge_edge"]
                else:
                    mode_badge.bgcolor = C["badge_add"]
            mode_badge.update()

        # ── result bar ───────────────────────────
        result_bar = ft.Container(visible=False, border_radius=6,
                                padding=ft.padding.symmetric(10, 14))

        def show_result(path, is_cycle: bool):
            result_bar.visible = True
            if path is None:
                what = "cycle" if is_cycle else "path"
                result_bar.bgcolor = "#2b1414"
                result_bar.border  = ft.border.all(1, "#ff525255")
                result_bar.content = ft.Row([
                    ft.Text("✗", color="#ff5252",
                            weight=ft.FontWeight.BOLD, size=14),
                    ft.Text(f"No Hamiltonian {what} found.",
                            color="#ff8a80", size=13)])
            else:
                arrow = " → ".join(path)
                label = "Cycle found" if is_cycle else "Path found"
                result_bar.bgcolor = "#0e2318"
                result_bar.border  = ft.border.all(1, C["accent"] + "55")
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
            hi_verts.clear()
            hi_edges.clear()

        # ── hit testing ──────────────────────────
        def vert_at(g: Graph, x, y) -> Optional[str]:
            for lbl, v in g.vertices.items():
                if math.hypot(v.x - x, v.y - y) <= VERT_R + 4:
                    return lbl
            return None

        def edge_at(g: Graph, x, y) -> Optional[tuple]:
            TOL = 9
            best, best_d = None, TOL
            for a, nbrs in g.adjacency.items():
                va = g.vertices[a]
                for b in nbrs:
                    if b <= a:
                        continue
                    vb = g.vertices[b]
                    dx, dy = vb.x - va.x, vb.y - va.y
                    L2 = dx*dx + dy*dy
                    if L2 == 0:
                        continue
                    t = max(0, min(1, ((x - va.x)*dx + (y - va.y)*dy) / L2))
                    d = math.hypot(va.x + t*dx - x, va.y + t*dy - y)
                    if d < best_d:
                        best_d, best = d, (a, b)
            return best

        # ── canvas tap ───────────────────────────
        def on_tap(e: ft.TapEvent):
            x, y = e.local_x, e.local_y
            m = state["mode"]

            # after Load is pressed, canvas is read-only except for algo buttons
            if state["is_loaded"]:
                return

            hit = vert_at(draft, x, y)

            if m == "normal":
                if hit is None:
                    draft.add_vertex(x, y)
                    clear_result(); update_status(); redraw()

            elif m == "add_edge":
                if hit is None:
                    return
                if state["edge_src"] is None:
                    state["edge_src"] = hit
                    redraw()
                else:
                    src = state["edge_src"]
                    state["edge_src"] = None
                    if src != hit and not draft.has_edge(src, hit):
                        draft.add_edge(src, hit)
                        clear_result(); update_status()
                    redraw()

            elif m == "delete":
                if hit:
                    if state["edge_src"] == hit:
                        state["edge_src"] = None
                    draft.remove_vertex(hit)
                else:
                    e2 = edge_at(draft, x, y)
                    if e2:
                        draft.remove_edge(*e2)
                clear_result(); update_status(); redraw()

        gesture = ft.GestureDetector(
            content=ft.Stack([
                ft.Container(width=CANVAS_W, height=CANVAS_H,
                            bgcolor=C["canvas"], border_radius=8),
                hint, cv, overlay,
            ]),
            on_tap=on_tap)

        # ── build buttons summary list ───────────
        summary_col = ft.Column([], spacing=4, visible=False)
        summary_box = ft.Container(
            content=ft.Column([
                ft.Text("Loaded graph summary", size=12,
                        weight=ft.FontWeight.BOLD, color=C["accent"]),
                summary_col,
            ], spacing=4),
            bgcolor="#12141f", border_radius=6,
            padding=ft.padding.symmetric(8, 12),
            border=ft.border.all(1, C["accent"] + "44"),
            visible=False)

        def build_summary():
            g = loaded
            rows = []
            vlist = ", ".join(sorted(g.vertices.keys()))
            rows.append(ft.Text(f"Vertices ({len(g.vertices)}): {vlist}",
                                size=11, color=C["dim"]))
            edge_list = []
            for a, nbrs in g.adjacency.items():
                for b in nbrs:
                    if b > a:
                        edge_list.append(f"{a}–{b}")
            rows.append(ft.Text(f"Edges ({g.edge_count()}): {', '.join(sorted(edge_list))}",
                                size=11, color=C["dim"]))
            summary_col.controls = rows
            summary_col.visible  = True
            summary_box.visible  = True
            summary_col.update()
            summary_box.update()

        # ── button helpers ───────────────────────
        def ebtn(label, onclick, bgcolor="#252840"):
            return ft.ElevatedButton(
                label, on_click=onclick,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=6),
                    padding=ft.padding.symmetric(8, 16),
                    bgcolor={"": bgcolor},
                    color={"": C["text"]}),
                height=34)

        def obtn(label, onclick):
            return ft.OutlinedButton(
                label, on_click=onclick,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=6),
                    padding=ft.padding.symmetric(8, 16),
                    color={"": C["text"]},
                    side={"": ft.BorderSide(1, "#444466")}),
                height=36)

        # ── toolbar handlers ─────────────────────

        def on_add_vertex(_):
            if state["is_loaded"]:
                page.open(ft.SnackBar(
                    content=ft.Text("Graph is locked. Press Reset to edit again.",
                                    color="#fff"),
                    bgcolor="#3a2200", duration=2000))
                return
            set_mode("normal")
            page.open(ft.SnackBar(
                content=ft.Text("Click anywhere on the canvas to place a vertex",
                                color="#fff"),
                bgcolor="#1a2a3a", duration=2000))

        def on_add_edge(_):
            if state["is_loaded"]:
                page.open(ft.SnackBar(
                    content=ft.Text("Graph is locked. Press Reset to edit again.",
                                    color="#fff"),
                    bgcolor="#3a2200", duration=2000))
                return
            if state["mode"] == "add_edge":
                set_mode("normal")
            else:
                set_mode("add_edge")
                page.open(ft.SnackBar(
                    content=ft.Text("Tap first vertex → then second vertex to connect",
                                    color="#fff"),
                    bgcolor="#1a2a3a", duration=2500))

        def on_delete(_):
            if state["is_loaded"]:
                page.open(ft.SnackBar(
                    content=ft.Text("Graph is locked. Press Reset to edit again.",
                                    color="#fff"),
                    bgcolor="#3a2200", duration=2000))
                return
            if state["mode"] == "delete":
                set_mode("normal")
            else:
                set_mode("delete")
                page.open(ft.SnackBar(
                    content=ft.Text("Tap a vertex or edge to delete it",
                                    color="#fff"),
                    bgcolor="#1a2a3a", duration=2500))

        def on_load(_):
            """Snapshot the draft graph into loaded, lock the canvas."""
            if len(draft.vertices) == 0:
                page.open(ft.SnackBar(
                    content=ft.Text("Nothing to load — add some vertices first!",
                                    color="#fff"),
                    bgcolor="#3a1a1a", duration=2000))
                return

            # copy draft → loaded
            loaded.clear()
            for lbl, v in draft.vertices.items():
                loaded.vertices[lbl] = Vertex(lbl, v.x, v.y)
                loaded.adjacency[lbl] = set(draft.adjacency[lbl])

            state["is_loaded"] = True
            set_mode("normal")
            clear_result()
            loaded_badge.visible = True
            loaded_badge.update()
            build_summary()
            update_status()
            redraw()

            page.open(ft.SnackBar(
                content=ft.Text(
                    f"Graph loaded! {len(loaded.vertices)} vertices, "
                    f"{loaded.edge_count()} edges. Ready to find paths.",
                    color="#fff"),
                bgcolor="#1a3a1a", duration=3000))

        def on_reset(_):
            """Go back to edit mode, keep draft as-is so user can modify."""
            state["is_loaded"] = False
            loaded_badge.visible = False
            loaded_badge.update()
            summary_box.visible = False
            summary_box.update()
            loaded.clear()
            clear_result()
            set_mode("normal")
            update_status()
            redraw()
            page.open(ft.SnackBar(
                content=ft.Text("Back to edit mode. Modify your graph then press Load again.",
                                color="#fff"),
                bgcolor="#1a2a3a", duration=2500))

        def on_clear(_):
            state["is_loaded"] = False
            loaded_badge.visible = False
            loaded_badge.update()
            summary_box.visible = False
            summary_box.update()
            draft.clear()
            loaded.clear()
            set_mode("normal")
            clear_result()
            update_status()
            redraw()

        def on_find_path(_):
            if not state["is_loaded"]:
                page.open(ft.SnackBar(
                    content=ft.Text("Press 'Load' first to confirm your graph!",
                                    color="#fff"),
                    bgcolor="#3a2200", duration=2500))
                return
            res = loaded.find_hamiltonian_path()
            hi_verts.clear(); hi_edges.clear()
            if res:
                hi_verts.update(res)
                for i in range(len(res) - 1):
                    hi_edges.add((res[i], res[i + 1]))
            show_result(res, False)
            redraw()

        def on_find_cycle(_):
            if not state["is_loaded"]:
                page.open(ft.SnackBar(
                    content=ft.Text("Press 'Load' first to confirm your graph!",
                                    color="#fff"),
                    bgcolor="#3a2200", duration=2500))
                return
            res = loaded.find_hamiltonian_cycle()
            hi_verts.clear(); hi_edges.clear()
            if res:
                hi_verts.update(res[:-1])
                for i in range(len(res) - 1):
                    hi_edges.add((res[i], res[i + 1]))
            show_result(res, True)
            redraw()

        # ── layout ───────────────────────────────
        toolbar = ft.Row([
            ebtn("Add vertex", on_add_vertex),
            ebtn("Add edge",   on_add_edge),
            ebtn("Delete",     on_delete,  bgcolor="#3a1515"),
            ebtn("Load",       on_load,    bgcolor="#1a3a1a"),
            ebtn("Reset",      on_reset,   bgcolor="#2a2200"),
            ebtn("Clear",      on_clear,   bgcolor="#2a1a1a"),
        ], spacing=6, wrap=True)

        algo_row = ft.Row([
            obtn("Find Hamiltonian path",  on_find_path),
            obtn("Find Hamiltonian cycle", on_find_cycle),
        ], spacing=8)

        def dot(color): return ft.Container(
            width=10, height=10, bgcolor=color, border_radius=5)

        legend = ft.Row([
            ft.Row([dot(C["vert_norm"]),
                    ft.Text("Normal vertex",        size=11, color=C["dim"])], spacing=4),
            ft.Row([dot(C["vert_hi"]),
                    ft.Text("In path/cycle",        size=11, color=C["dim"])], spacing=4),
            ft.Row([dot(C["vert_sel"]),
                    ft.Text("Selected (edge mode)", size=11, color=C["dim"])], spacing=4),
        ], spacing=16)

        instructions = ft.Container(
            content=ft.Column([
                ft.Text("How to use", size=12,
                        weight=ft.FontWeight.BOLD, color=C["accent"]),
                ft.Text("① Click canvas to place vertices  ② Click 'Add edge' then tap two vertices",
                        size=11, color=C["dim"]),
                ft.Text("③ Click 'Delete' to remove a vertex or edge  ④ Press 'Load' to confirm your graph",
                        size=11, color=C["dim"]),
                ft.Text("⑤ Click 'Find Hamiltonian path/cycle' to run the algorithm",
                        size=11, color=C["dim"]),
                ft.Text("  Press 'Reset' to go back and edit · 'Clear' wipes everything",
                        size=11, color=C["dim"]),
            ], spacing=3),
            bgcolor="#12141f", border_radius=6,
            padding=ft.padding.symmetric(8, 12),
            border=ft.border.all(1, "#2a2a4a"))

        layout = ft.Container(
            ft.Column([
                ft.Container(
                    ft.Column([
                        toolbar,
                        gesture,
                        ft.Row([status_txt, mode_badge, loaded_badge], spacing=10),
                        algo_row,
                        result_bar,
                        summary_box,
                        legend,
                        instructions,
                    ], spacing=10),
                    bgcolor=C["panel"], border_radius=10, padding=16)
            ]),
            padding=20)

        page.add(layout)
        redraw()


    ft.app(target=main)
