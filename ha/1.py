import flet as ft

def main(page: ft.Page):
    page.title = "Hamiltonian Graph Detector"
    page.window_width = 800
    page.window_height = 700
    page.scroll = "auto"

    vertices = []
    edges = []
    selected = []

    result_text = ft.Text(size=20, weight="bold")

    edge_list = ft.Text()

    graph_area = ft.Column()

    def update_edges():
        edge_list.value = "Edges:\n"

        for a, b in edges:
            edge_list.value += f"{vertices[a]} - {vertices[b]}\n"

        page.update()

    def add_edge(e):
        idx = int(e.control.data)

        if idx not in selected:
            selected.append(idx)

        if len(selected) == 2:
            a = selected[0]
            b = selected[1]

            if a != b:
                if (a, b) not in edges and (b, a) not in edges:
                    edges.append((a, b))

            selected.clear()
            update_edges()

    def generate_vertices(e):
        vertices.clear()
        edges.clear()
        selected.clear()

        graph_area.controls.clear()

        try:
            n = int(vertex_count.value)

            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

            for i in range(n):
                vertices.append(letters[i])

            row = ft.Row(wrap=True)

            for i in range(n):
                btn = ft.ElevatedButton(
                    text=vertices[i],
                    width=60,
                    data=i,
                    on_click=add_edge
                )
                row.controls.append(btn)

            graph_area.controls.append(
                ft.Text(
                    "Click TWO vertices to create an edge.",
                    size=16
                )
            )

            graph_area.controls.append(row)

            result_text.value = ""
            edge_list.value = ""

            page.update()

        except:
            result_text.value = "Enter a valid number."
            page.update()

    def hamiltonian_check(e):
        n = len(vertices)

        if n == 0:
            return

        graph = [[0 for _ in range(n)] for _ in range(n)]

        for a, b in edges:
            graph[a][b] = 1
            graph[b][a] = 1

        found_path = []

        def backtrack(path, visited):
            nonlocal found_path

            if len(path) == n:
                found_path = path.copy()
                return True

            current = path[-1]

            for v in range(n):
                if not visited[v] and graph[current][v] == 1:
                    visited[v] = True
                    path.append(v)

                    if backtrack(path, visited):
                        return True

                    path.pop()
                    visited[v] = False

            return False

        classification = "Neither"

        for start in range(n):

            visited = [False] * n
            visited[start] = True

            if backtrack([start], visited):

                if graph[found_path[-1]][found_path[0]] == 1:
                    classification = "Hamiltonian Circuit"

                    display_path = " → ".join(
                        vertices[v] for v in found_path
                    )

                    display_path += f" → {vertices[found_path[0]]}"

                else:
                    classification = "Hamiltonian Path"

                    display_path = " → ".join(
                        vertices[v] for v in found_path
                    )

                result_text.value = (
                    f"{classification}\n\nPath:\n{display_path}"
                )

                page.update()
                return

        result_text.value = "Neither"
        page.update()

    vertex_count = ft.TextField(
        label="Number of Vertices",
        width=200
    )

    page.add(
        ft.Text(
            "Hamiltonian Graph Detector",
            size=28,
            weight="bold"
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
            "Check Hamiltonian",
            on_click=hamiltonian_check
        ),

        edge_list,

        result_text
    )

ft.app(target=main)