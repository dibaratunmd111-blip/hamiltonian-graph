import flet as ft

# =====================================
# EXAMPLE GRAPHS
# =====================================

EXAMPLES = {
    "Hexagonal Web": {
        "vertices": [
            (250, 50),
            (350, 100),
            (350, 220),
            (250, 280),
            (150, 220),
            (150, 100)
        ],
        "edges": [
            (0,1),(1,2),(2,3),(3,4),(4,5),(5,0),
            (0,4),(0,2),(4,2)
        ]
    },

    "Wheel W5": {
        "vertices": [
            (250,150),
            (250,50),
            (350,120),
            (320,250),
            (180,250),
            (150,120)
        ],
        "edges": [
            (1,2),(2,3),(3,4),(4,5),(5,1),
            (0,1),(0,2),(0,3),(0,4),(0,5)
        ]
    },

    "Triangle Chain": {
        "vertices": [
            (120,180),
            (180,80),
            (240,180),
            (300,100),
            (360,180),
            (320,40),
            (420,120)
        ],
        "edges": [
            (0,1),(1,2),(2,0),
            (2,3),(3,4),(4,2),
            (4,5),(5,6),(6,4)
        ]
    },

    "Octagram Path": {
        "vertices": [
            (250,50),
            (350,90),
            (390,180),
            (340,270),
            (250,310),
            (160,270),
            (110,180),
            (150,90)
        ],
        "edges": [
            (0,1),(1,2),(2,3),(3,4),
            (4,5),(5,6),(6,7),(7,0),
            (0,4)
        ]
    }
}


# =====================================
# HAMILTONIAN ALGORITHMS
# =====================================

def create_graph(vertices, edges):
    graph = {i: [] for i in range(len(vertices))}

    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    return graph


def find_hamiltonian_path(graph):

    n = len(graph)

    def dfs(v, visited, path):

        if len(path) == n:
            return path

        for neighbor in graph[v]:

            if neighbor not in visited:

                visited.add(neighbor)
                path.append(neighbor)

                result = dfs(neighbor, visited, path)

                if result:
                    return result

                visited.remove(neighbor)
                path.pop()

        return None

    for start in graph:

        result = dfs(start, {start}, [start])

        if result:
            return result

    return None


def find_hamiltonian_cycle(graph):

    n = len(graph)

    def dfs(v, start, visited, path):

        if len(path) == n:

            if start in graph[v]:
                return path + [start]

            return None

        for neighbor in graph[v]:

            if neighbor not in visited:

                visited.add(neighbor)
                path.append(neighbor)

                result = dfs(
                    neighbor,
                    start,
                    visited,
                    path
                )

                if result:
                    return result

                visited.remove(neighbor)
                path.pop()

        return None

    for start in graph:

        result = dfs(
            start,
            start,
            {start},
            [start]
        )

        if result:
            return result

    return None


# =====================================
# APP
# =====================================

def main(page: ft.Page):

    page.title = "Hamiltonian Graph Visualizer"
    page.bgcolor = "#162447"
    page.padding = 20

    vertices = []
    edges = []

    highlighted = []

    canvas = ft.Stack(
        width=650,
        height=400,
    )

    info_text = ft.Text(
        "Vertices: 0   Edges: 0",
        color="white"
    )

    result_text = ft.Text(
        color="lightgreen",
        size=18
    )

    # -----------------------------
    # DRAW GRAPH
    # -----------------------------

    def draw_graph():

        canvas.controls.clear()

        # Draw edges

        for u, v in edges:

            x1, y1 = vertices[u]
            x2, y2 = vertices[v]

            color = "white"

            for i in range(len(highlighted)-1):

                a = highlighted[i]
                b = highlighted[i+1]

                if (
                    (u == a and v == b)
                    or
                    (u == b and v == a)
                ):
                    color = "lime"

            canvas.controls.append(

                ft.Container(
                    left=min(x1, x2),
                    top=min(y1, y2),
                    content=ft.Text(
                        "────────",
                        color=color
                    )
                )

            )

        # Draw vertices

        for i, (x, y) in enumerate(vertices):

            color = "#4285F4"

            if i in highlighted:
                color = "lime"

            canvas.controls.append(

                ft.Container(
                    left=x,
                    top=y,
                    width=35,
                    height=35,
                    bgcolor=color,
                    border_radius=20,
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        chr(65 + i),
                        color="white",
                        weight="bold"
                    )
                )

            )

        info_text.value = (
            f"Vertices: {len(vertices)}   "
            f"Edges: {len(edges)}"
        )

        page.update()

    # -----------------------------
    # LOAD GRAPH
    # -----------------------------

    graph_dropdown = ft.Dropdown(
        width=250,
        label="Example Graph",
        options=[
            ft.dropdown.Option(x)
            for x in EXAMPLES.keys()
        ]
    )

    def load_graph(e):

        if not graph_dropdown.value:
            return

        vertices.clear()
        edges.clear()
        highlighted.clear()

        graph = EXAMPLES[graph_dropdown.value]

        vertices.extend(graph["vertices"])
        edges.extend(graph["edges"])

        result_text.value = ""

        draw_graph()

    # -----------------------------
    # HAMILTON PATH
    # -----------------------------

    def solve_path(e):

        highlighted.clear()

        graph = create_graph(
            vertices,
            edges
        )

        result = find_hamiltonian_path(graph)

        if result:

            highlighted.extend(result)

            letters = [
                chr(65+i)
                for i in result
            ]

            result_text.value = (
                "Hamiltonian Path:\n"
                + " → ".join(letters)
            )

        else:

            result_text.value = (
                "No Hamiltonian Path"
            )

        draw_graph()

    # -----------------------------
    # HAMILTON CYCLE
    # -----------------------------

    def solve_cycle(e):

        highlighted.clear()

        graph = create_graph(
            vertices,
            edges
        )

        result = find_hamiltonian_cycle(graph)

        if result:

            highlighted.extend(result)

            letters = [
                chr(65+i)
                for i in result
            ]

            result_text.value = (
                "Hamiltonian Cycle:\n"
                + " → ".join(letters)
            )

        else:

            result_text.value = (
                "No Hamiltonian Cycle"
            )

        draw_graph()

    # -----------------------------
    # UI
    # -----------------------------

    page.add(

        ft.Text(
            "Hamiltonian Graph Visualizer",
            size=28,
            weight="bold",
            color="white"
        ),

        ft.Row([
            graph_dropdown,

            ft.ElevatedButton(
                "Load Example",
                on_click=load_graph
            ),
        ]),

        ft.Container(
            content=canvas,
            bgcolor="black",
            border_radius=10,
            padding=10
        ),

        info_text,

        ft.Row([

            ft.ElevatedButton(
                "Find Hamiltonian Path",
                on_click=solve_path
            ),

            ft.ElevatedButton(
                "Find Hamiltonian Cycle",
                on_click=solve_cycle
            ),

        ]),

        result_text
    )


ft.app(target=main)