import flet as ft

RADIUS = 25

def main(page: ft.Page):
    page.title = "Hamiltonian Graph Detector"
    page.window_width = 1000
    page.window_height = 700
    page.scroll = ft.ScrollMode.AUTO

    vertices = []
    edges = []
    selected = None

    graph_area = ft.Column()
    result_text = ft.Text(size=20, weight=ft.FontWeight.BOLD)

    vertex_count = ft.TextField(
        label="Number of Vertices",
        width=200
    )

    def refresh_graph():
        graph_area.controls.clear()

        graph_area.controls.append(
            ft.Text(
                "Click two vertices to connect them",
                size=16
            )
        )

        row = ft.Row(wrap=True)

        for i, v in enumerate(vertices):
            row.controls.append(
                ft.ElevatedButton(
                    text=v,
                    data=i,
                    on_click=vertex_clicked,
                    width=70,
                    height=70
                )
            )

        graph_area.controls.append(row)

        edge_text = "Edges:\n"

        for a, b in edges:
            edge_text += f"{vertices[a]} - {vertices[b]}\n"

        graph_area.controls.append(ft.Text(edge_text))

        page.update()

    def generate_vertices(e):
        vertices.clear()
        edges.clear()

        try:
            n = int(vertex_count.value)

            for i in range(n):
                vertices.append(chr(65 + i))

            result_text.value = ""

            refresh_graph()

        except:
            result_text.value = "Enter a valid number."
            page.update()

    def vertex_clicked(e):
        nonlocal selected

        current = int(e.control.data)

        if selected is None:
            selected = current
            return

        if selected != current:

            if (selected, current) not in edges and \
               (current, selected) not in edges:

                edges.append((selected, current))

        selected = None

        refresh_graph()

    def analyze_graph(e):

        n = len(vertices)

        if n == 0:
            result_text.value = "Generate vertices first."
            page.update()
            return

        graph = [[0] * n for _ in range(n)]

        for a, b in edges:
            graph[a][b] = 1
            graph[b][a] = 1

        final_path = []

        def backtrack(path, visited):
            nonlocal final_path

            if len(path) == n:
                final_path = path.copy()
                return True

            current = path[-1]

            for nxt in range(n):

                if graph[current][nxt] == 1 and not visited[nxt]:

                    visited[nxt] = True
                    path.append(nxt)

                    if backtrack(path, visited):
                        return True

                    path.pop()
                    visited[nxt] = False

            return False

        for start in range(n):

            visited = [False] * n
            visited[start] = True

            if backtrack([start], visited):

                names = [vertices[i] for i in final_path]

                if graph[final_path[-1]][final_path[0]] == 1:

                    names.append(vertices[final_path[0]])

                    result_text.value = (
                        "Classification: Hamiltonian Circuit\n\n"
                        "Path:\n"
                        + " → ".join(names)
                    )

                else:

                    result_text.value = (
                        "Classification: Hamiltonian Path\n\n"
                        "Path:\n"
                        + " → ".join(names)
                    )

                page.update()
                return

        result_text.value = (
            "Classification: Neither"
        )

        page.update()

    page.add(
        ft.Text(
            "Hamiltonian Graph Detector",
            size=30,
            weight=ft.FontWeight.BOLD
        ),

        ft.Row(
            [
                vertex_count,
                ft.ElevatedButton(
                    "Generate Vertices",
                    on_click=generate_vertices
                )
            ]
        ),

        graph_area,

        ft.ElevatedButton(
            "Analyze Graph",
            on_click=analyze_graph
        ),

        result_text
    )

ft.app(target=main)