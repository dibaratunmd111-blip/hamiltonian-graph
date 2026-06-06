# Enter Vertices: 5

# [ Generate Graph ]

#       0

#   4       1

#   3       2


# Click:
# 0 → 1
# 1 → 2
# 2 → 3
# 3 → 4
# 4 → 0

# [ Check Hamiltonian ]

# Result:
# Hamiltonian Circuit
# Path: 0 → 1 → 2 → 3 → 4 → 0

import flet as ft
import math


def main(page: ft.Page):
    page.title = "Hamiltonian Graph Checker"
    page.window_width = 900
    page.window_height = 700
    page.scroll = "auto"

    graph = {}
    vertices = []
    edges = []
    selected_vertex = None

    result_text = ft.Text(size=20, weight="bold")

    graph_area = ft.Stack(width=700, height=500)

    # --------------------------
    # Hamiltonian Circuit
    # --------------------------
    def find_hamiltonian_circuit(graph):
        n = len(graph)

        def backtrack(path):
            if len(path) == n:
                if path[0] in graph[path[-1]]:
                    return path + [path[0]]
                return None

            current = path[-1]

            for neighbor in graph[current]:
                if neighbor not in path:
                    result = backtrack(path + [neighbor])
                    if result:
                        return result

            return None

        for start in graph:
            result = backtrack([start])
            if result:
                return result

        return None

    # --------------------------
    # Hamiltonian Path
    # --------------------------
    def find_hamiltonian_path(graph):
        n = len(graph)

        def backtrack(path):
            if len(path) == n:
                return path

            current = path[-1]

            for neighbor in graph[current]:
                if neighbor not in path:
                    result = backtrack(path + [neighbor])
                    if result:
                        return result

            return None

        for start in graph:
            result = backtrack([start])
            if result:
                return result

        return None

    # --------------------------
    # Draw Edges
    # --------------------------
    def refresh_graph():

        graph_area.controls.clear()

        # Draw edges first
        for u, v in edges:

            x1, y1 = vertices[u]
            x2, y2 = vertices[v]

            dx = x2 - x1
            dy = y2 - y1

            length = math.sqrt(dx * dx + dy * dy)

            angle = math.degrees(math.atan2(dy, dx))

            line = ft.Container(
                width=length,
                height=3,
                bgcolor=ft.Colors.BLACK,
                left=x1 + 20,
                top=y1 + 20,
                rotate=ft.transform.Rotate(math.radians(angle)),
            )

            graph_area.controls.append(line)

        # Draw vertices
        for i, (x, y) in enumerate(vertices):

            def create_click(index):
                return lambda e: vertex_clicked(index)

            vertex = ft.Container(
                content=ft.Text(
                    str(i),
                    color=ft.Colors.WHITE,
                    size=18,
                    text_align="center",
                ),
                width=40,
                height=40,
                bgcolor=ft.Colors.BLUE,
                border_radius=20,
                alignment=ft.alignment.center,
                left=x,
                top=y,
                on_click=create_click(i),
            )

            graph_area.controls.append(vertex)

        page.update()

    # --------------------------
    # Vertex Click
    # --------------------------
    def vertex_clicked(index):
        nonlocal selected_vertex

        if selected_vertex is None:
            selected_vertex = index

        else:

            if selected_vertex != index:

                edge = (selected_vertex, index)
                reverse_edge = (index, selected_vertex)

                if edge not in edges and reverse_edge not in edges:

                    edges.append(edge)

                    graph[selected_vertex].append(index)
                    graph[index].append(selected_vertex)

            selected_vertex = None

            refresh_graph()

    # --------------------------
    # Generate Graph
    # --------------------------
    def generate_graph(e):

        nonlocal graph
        nonlocal vertices
        nonlocal edges
        nonlocal selected_vertex

        try:
            n = int(vertex_input.value)

            graph = {}
            vertices = []
            edges = []
            selected_vertex = None

            graph_area.controls.clear()

            center_x = 300
            center_y = 220
            radius = 180

            for i in range(n):
                graph[i] = []

                angle = (2 * math.pi * i) / n

                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)

                vertices.append((x, y))

            refresh_graph()

            result_text.value = ""

            page.update()

        except:
            result_text.value = "Invalid number of vertices"
            page.update()

    # --------------------------
    # Check Hamiltonian
    # --------------------------
    def check_graph(e):

        if len(graph) == 0:
            return

        circuit = find_hamiltonian_circuit(graph)

        if circuit:
            result_text.value = (
                "Hamiltonian Circuit\nPath: "
                + " → ".join(map(str, circuit))
            )

        else:

            path = find_hamiltonian_path(graph)

            if path:
                result_text.value = (
                    "Hamiltonian Path\nPath: "
                    + " → ".join(map(str, path))
                )

            else:
                result_text.value = "Neither Hamiltonian Path nor Circuit"

        page.update()

    # --------------------------
    # Controls
    # --------------------------
    vertex_input = ft.TextField(
        label="Number of Vertices",
        width=200,
    )

    generate_button = ft.ElevatedButton(
        "Generate Graph",
        on_click=generate_graph,
    )

    check_button = ft.ElevatedButton(
        "Check Hamiltonian",
        on_click=check_graph,
    )

    page.add(
        ft.Text(
            "Hamiltonian Graph Checker",
            size=28,
            weight="bold",
        ),
        ft.Row(
            [
                vertex_input,
                generate_button,
                check_button,
            ]
        ),
        graph_area,
        result_text,
    )


ft.app(target=main)