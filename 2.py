import flet as ft
import flet.canvas as cv


# =====================================
# EXAMPLE GRAPHS (FROM YOUR IMAGES)
# =====================================

EXAMPLES = {
    "Hexagonal Web": {
        "vertices": [
            (250, 60),   # A
            (350, 120),  # B
            (320, 220),  # C
            (250, 280),  # D
            (180, 220),  # E
            (150, 120),  # F
        ],
        "edges": [
            (0,1),(1,2),(2,3),(3,4),(4,5),(5,0),
            (0,4),(0,2),(4,2)
        ]
    },

    "Ladder Spine": {
        "vertices": [
            (120, 220),  # A
            (120, 80),   # B
            (230, 140),  # C
            (350, 80),   # D
            (350, 220),  # E
            (230, 280),  # F
        ],
        "edges": [
            (0,1),
            (1,3),
            (3,4),

            (0,2),
            (1,2),
            (2,3),

            (2,4),
            (4,5),
            (5,2)
        ]
    },

    "Wheel W5": {
        "vertices": [
            (250, 170),  # A center
            (250, 60),   # B
            (350, 130),  # C
            (310, 260),  # D
            (190, 260),  # E
            (150, 130),  # F
        ],
        "edges": [
            (1,2),(2,3),(3,4),(4,5),(5,1),
            (0,1),(0,2),(0,3),(0,4),(0,5)
        ]
    },

    "Triangle Chain": {
        "vertices": [
            (100, 150),  # A
            (170, 70),   # B
            (240, 150),  # C
            (240, 80),   # D
            (310, 150),  # E
            (310, 60),   # F
            (380, 120),  # G
        ],
        "edges": [
            (0,1),(1,2),(2,0),
            (2,3),(3,4),(4,2),
            (4,5),(5,6),(6,4)
        ]
    }
}


# =====================================
# HAMILTONIAN ALGORITHM
# =====================================

def create_graph(vertices, edges):
    g = {i: [] for i in range(len(vertices))}
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    return g


def hamiltonian_path(graph):
    n = len(graph)

    def dfs(v, visited, path):
        if len(path) == n:
            return path

        for nxt in graph[v]:
            if nxt not in visited:
                visited.add(nxt)
                path.append(nxt)

                res = dfs(nxt, visited, path)
                if res:
                    return res

                visited.remove(nxt)
                path.pop()
        return None

    for start in graph:
        res = dfs(start, {start}, [start])
        if res:
            return res
    return None


def hamiltonian_cycle(graph):
    n = len(graph)

    def dfs(v, start, visited, path):
        if len(path) == n:
            if start in graph[v]:
                return path + [start]
            return None

        for nxt in graph[v]:
            if nxt not in visited:
                visited.add(nxt)
                path.append(nxt)

                res = dfs(nxt, start, visited, path)
                if res:
                    return res

                visited.remove(nxt)
                path.pop()
        return None

    for start in graph:
        res = dfs(start, start, {start}, [start])
        if res:
            return res
    return None


# =====================================
# APP
# =====================================

def main(page: ft.Page):

    page.title = "Hamiltonian Graph Visualizer"
    page.bgcolor = "#2750AB"

    vertices = []
    edges = []
    highlighted = []

    canvas_container = ft.Container(
        width=650,
        height=450,
        bgcolor="green",
        border_radius=10
    )

    info = ft.Text(color="white")
    result = ft.Text(color="lightgreen", size=16)

    # =====================================
    # DRAW GRAPH (REAL CANVAS VERSION)
    # =====================================

    def draw():

        shapes = []

        # ----- DRAW EDGES -----
        for u, v in edges:

            x1, y1 = vertices[u]
            x2, y2 = vertices[v]

            color = "white"

            for i in range(len(highlighted)-1):
                a, b = highlighted[i], highlighted[i+1]
                if (u == a and v == b) or (u == b and v == a):
                    color = "lime"

            shapes.append(
                cv.Line(
                    x1=x1, y1=y1,
                    x2=x2, y2=y2,
                    paint=ft.Paint(color=color, stroke_width=3)
                )
            )

        # ----- DRAW NODES -----
        for i, (x, y) in enumerate(vertices):

            color = "dodgerblue"
            if i in highlighted:
                color = "lime"

            shapes.append(
                cv.Circle(
                    x=x,
                    y=y,
                    radius=18,
                    paint=ft.Paint(color=color)
                )
            )

            shapes.append(
                cv.Text(
                    x=x-6,
                    y=y-7,
                    text=chr(65+i),
                    style=ft.TextStyle(color="white", size=14)
                )
            )

        canvas_container.content = cv.Canvas(
            shapes=shapes
        )

        info.value = f"Vertices: {len(vertices)} | Edges: {len(edges)}"
        page.update()

    # =====================================
    # LOAD EXAMPLE
    # =====================================

    dropdown = ft.Dropdown(
        width=250,
        label="Example Graph",
        options=[ft.dropdown.Option(k) for k in EXAMPLES.keys()]
    )

    def load(e):
        g = EXAMPLES[dropdown.value]
        vertices.clear()
        edges.clear()
        highlighted.clear()

        vertices.extend(g["vertices"])
        edges.extend(g["edges"])

        result.value = ""
        draw()

    # =====================================
    # SOLVERS
    # =====================================

    def solve_path(e):
        highlighted.clear()
        g = create_graph(vertices, edges)
        res = hamiltonian_path(g)

        if res:
            highlighted.extend(res)
            result.value = "Path: " + " → ".join(chr(65+i) for i in res)
        else:
            result.value = "No Hamiltonian Path"

        draw()

    def solve_cycle(e):
        highlighted.clear()
        g = create_graph(vertices, edges)
        res = hamiltonian_cycle(g)

        if res:
            highlighted.extend(res)
            result.value = "Cycle: " + " → ".join(chr(65+i) for i in res)
        else:
            result.value = "No Hamiltonian Cycle"

        draw()

    # =====================================
    # UI
    # =====================================

    page.add(
        ft.Text(
            "Hamiltonian Graph Visualizer",
            size=26,
            color="white",
            weight="bold"
        ),

        ft.Row([
            dropdown,
            ft.ElevatedButton("Load Example", on_click=load)
        ]),

        canvas_container,

        info,

        ft.Row([
            ft.ElevatedButton("Find Hamiltonian Path", on_click=solve_path),
            ft.ElevatedButton("Find Hamiltonian Cycle", on_click=solve_cycle),
        ]),

        result
    )


ft.app(target=main)