import flet as ft
from graph import Graph
from hamiltonian import hamiltonian_cycle, hamiltonian_path

graph = Graph()

vertex_counter = 0
mode = "vertex"


def main(page: ft.Page):

    page.title = "Hamiltonian Graph Visualizer"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 900
    page.window_height = 700

    result_text = ft.Text("", color="lightgreen")

    canvas = ft.Stack(width=800, height=450)

    stats = ft.Text("Vertices: 0 | Edges: 0")

    selected_vertex = None

    def redraw():

        controls = []

        # draw edges
        for v1, v2 in graph.edges:

            x1, y1 = graph.vertices[v1]
            x2, y2 = graph.vertices[v2]

            controls.append(
                ft.Container(
                    left=min(x1, x2),
                    top=min(y1, y2),
                    content=ft.Text("")
                )
            )

        # draw vertices
        for name, (x, y) in graph.vertices.items():

            controls.append(
                ft.Container(
                    left=x,
                    top=y,
                    width=40,
                    height=40,
                    bgcolor="green",
                    border_radius=20,
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        name,
                        color="white",
                        weight=ft.FontWeight.BOLD
                    ),
                    on_click=lambda e, n=name: vertex_click(n)
                )
            )

        canvas.controls = controls

        stats.value = (
            f"Vertices: {len(graph.vertices)} | "
            f"Edges: {len(graph.edges)}"
        )

        page.update()

    def vertex_click(name):
        nonlocal selected_vertex

        if mode == "edge":

            if selected_vertex is None:
                selected_vertex = name
            else:
                graph.add_edge(selected_vertex, name)
                selected_vertex = None
                redraw()

    def add_vertex(e):
        global vertex_counter

        vertex_counter += 1

        letter = chr(64 + vertex_counter)

        x = 100 + vertex_counter * 60
        y = 150

        graph.add_vertex(letter, x, y)

        redraw()

    def set_edge_mode(e):
        global mode
        mode = "edge"

    def clear_graph(e):
        graph.clear()
        redraw()
        result_text.value = ""
        page.update()

    def load_example(e):

        graph.clear()

        graph.add_vertex("A", 350, 50)
        graph.add_vertex("B", 500, 150)
        graph.add_vertex("C", 450, 300)
        graph.add_vertex("D", 250, 300)
        graph.add_vertex("E", 200, 150)

        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "D")
        graph.add_edge("D", "E")
        graph.add_edge("E", "A")

        graph.add_edge("A", "C")
        graph.add_edge("B", "D")

        redraw()

    def find_cycle(e):

        g = graph.adjacency_list()

        cycle = hamiltonian_cycle(g)

        if cycle:
            result_text.value = (
                "Cycle Found: "
                + " → ".join(cycle)
            )
        else:
            result_text.value = "No Hamiltonian Cycle"

        page.update()

    def find_path(e):

        g = graph.adjacency_list()

        path = hamiltonian_path(g)

        if path:
            result_text.value = (
                "Path Found: "
                + " → ".join(path)
            )
        else:
            result_text.value = "No Hamiltonian Path"

        page.update()

    toolbar = ft.Row(
        [
            ft.ElevatedButton(
                "Add Vertex",
                on_click=add_vertex
            ),
            ft.ElevatedButton(
                "Add Edge",
                on_click=set_edge_mode
            ),
            ft.ElevatedButton(
                "Load Example",
                on_click=load_example
            ),
            ft.ElevatedButton(
                "Clear",
                on_click=clear_graph
            ),
        ]
    )

    actions = ft.Row(
        [
            ft.FilledButton(
                "Find Hamiltonian Path",
                on_click=find_path
            ),
            ft.FilledButton(
                "Find Hamiltonian Cycle",
                on_click=find_cycle
            ),
        ]
    )

    page.add(
        toolbar,
        ft.Container(
            canvas,
            border=ft.border.all(1, "gray"),
            padding=10
        ),
        stats,
        actions,
        ft.Container(
            result_text,
            padding=10,
            border=ft.border.all(1, "green")
        )
    )

    load_example(None)


ft.app(target=main)