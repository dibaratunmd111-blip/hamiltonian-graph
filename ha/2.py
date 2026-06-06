import flet as ft
import math

RADIUS = 20

def main(page: ft.Page):
    page.title = "Hamiltonian Graph Detector"
    page.window_width = 1000
    page.window_height = 700
    page.scroll = "auto"

    vertices = []
    edges = []
    selected_vertex = None

    result_text = ft.Text(size=18, weight=ft.FontWeight.BOLD)

    canvas = ft.Stack(width=900, height=500)

    def redraw():
        canvas.controls.clear()

        # Draw edges
        for a, b in edges:
            x1, y1 = vertices[a]["x"], vertices[a]["y"]
            x2, y2 = vertices[b]["x"], vertices[b]["y"]

            line = ft.Container(
                left=min(x1, x2),
                top=min(y1, y2),
                content=ft.Text(
                    "────────────",
                    size=20
                )
            )

            canvas.controls.append(line)

        # Draw vertices
        for i, vertex in enumerate(vertices):

            btn = ft.Container(
                width=40,
                height=40,
                bgcolor=ft.Colors.BLUE_200,
                border_radius=20,
                alignment=ft.alignment.center,
                left=vertex["x"],
                top=vertex["y"],
                content=ft.Text(vertex["name"]),
                on_click=lambda e, idx=i: vertex_click(idx)
            )

            canvas.controls.append(btn)

        page.update()

    def add_vertex_to_canvas(e):
        x = e.local_x
        y = e.local_y

        name = chr(65 + len(vertices))

        vertices.append({
            "name": name,
            "x": x,
            "y": y
        })

        redraw()

    def vertex_click(index):
        nonlocal selected_vertex

        if selected_vertex is None:
            selected_vertex = index
            return

        if selected_vertex != index:

            if (selected_vertex, index) not in edges and \
               (index, selected_vertex) not in edges:

                edges.append((selected_vertex, index))

        selected_vertex = None
        redraw()

    def analyze_graph(e):

        n = len(vertices)

        if n == 0:
            result_text.value = "No graph found."
            page.update()
            return

        graph = [[0] * n for _ in range(n)]

        for a, b in edges:
            graph[a][b] = 1
            graph[b][a] = 1

        final_path = []

        def solve(path, visited):
            nonlocal final_path

            if len(path) == n:
                final_path = path.copy()
                return True

            current = path[-1]

            for nxt in range(n):
                if graph[current][nxt] == 1 and not visited[nxt]:
                    visited[nxt] = True
                    path.append(nxt)

                    if solve(path, visited):
                        return True

                    path.pop()
                    visited[nxt] = False

            return False

        for start in range(n):

            visited = [False] * n
            visited[start] = True

            if solve([start], visited):

                names = [vertices[v]["name"] for v in final_path]

                if graph[final_path[-1]][final_path[0]] == 1:

                    names.append(vertices[final_path[0]]["name"])

                    result_text.value = (
                        "Classification: Hamiltonian Circuit\n\n"
                        + "Path:\n"
                        + " → ".join(names)
                    )

                else:

                    result_text.value = (
                        "Classification: Hamiltonian Path\n\n"
                        + "Path:\n"
                        + " → ".join(names)
                    )

                page.update()
                return

        result_text.value = "Classification: Neither"
        page.update()

    drawing_area = ft.GestureDetector(
        on_tap_down=add_vertex_to_canvas,
        content=ft.Container(
            width=900,
            height=500,
            border=ft.border.all(2),
            content=canvas
        )
    )

    page.add(
        ft.Text(
            "Hamiltonian Graph Detector",
            size=30,
            weight=ft.FontWeight.BOLD
        ),

        ft.Text(
            "Instructions:\n"
            "1. Click inside the canvas to create vertices.\n"
            "2. Click two vertices to connect them.\n"
            "3. Repeat until your graph is complete.\n"
            "4. Click Analyze Graph."
        ),

        drawing_area,

        ft.Row([
            ft.ElevatedButton(
                "Analyze Graph",
                on_click=analyze_graph
            )
        ]),

        result_text
    )

ft.app(target=main)