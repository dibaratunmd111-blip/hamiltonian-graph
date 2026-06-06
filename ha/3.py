import flet as ft
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image
import io
import base64


def main(page: ft.Page):
    page.title = "Hamiltonian Graph Detector"
    page.window_width = 1000
    page.window_height = 800
    page.scroll = ft.ScrollMode.AUTO

    graph_image = ft.Image(width=600, height=400)

    result_text = ft.Text(size=18, weight=ft.FontWeight.BOLD)

    vertices_input = ft.TextField(
        label="Vertices",
        hint_text="A,B,C,D,E,F",
        width=500
    )

    edges_input = ft.TextField(
        label="Edges",
        hint_text="A-B\nB-C\nC-D",
        multiline=True,
        min_lines=8,
        max_lines=8,
        width=500
    )

    current_vertices = []
    current_edges = []

    def generate_graph(e):

        nonlocal current_vertices
        nonlocal current_edges

        try:
            current_vertices = [
                v.strip()
                for v in vertices_input.value.split(",")
                if v.strip()
            ]

            current_edges = []

            lines = edges_input.value.strip().split("\n")

            for line in lines:

                if "-" in line:
                    a, b = line.split("-")

                    current_edges.append(
                        (a.strip(), b.strip())
                    )

            G = nx.Graph()

            G.add_nodes_from(current_vertices)
            G.add_edges_from(current_edges)

            fig, ax = plt.subplots(figsize=(6, 4))

            pos = nx.spring_layout(G, seed=42)

            nx.draw(
                G,
                pos,
                with_labels=True,
                node_size=2000,
                font_size=12,
                ax=ax
            )

            buf = io.BytesIO()

            canvas = FigureCanvasAgg(fig)
            canvas.print_png(buf)

            plt.close(fig)

            img_base64 = base64.b64encode(
                buf.getvalue()
            ).decode()

            graph_image.src_base64 = img_base64

            page.update()

        except Exception as ex:
            result_text.value = f"Error: {ex}"
            page.update()

    def analyze_graph(e):

        n = len(current_vertices)

        if n == 0:
            result_text.value = "Generate graph first."
            page.update()
            return

        index = {}

        for i, v in enumerate(current_vertices):
            index[v] = i

        graph = [[0] * n for _ in range(n)]

        for a, b in current_edges:

            if a in index and b in index:

                i = index[a]
                j = index[b]

                graph[i][j] = 1
                graph[j][i] = 1

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

                names = [
                    current_vertices[i]
                    for i in final_path
                ]

                if graph[final_path[-1]][final_path[0]] == 1:

                    names.append(
                        current_vertices[
                            final_path[0]
                        ]
                    )

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

        vertices_input,

        edges_input,

        ft.Row(
            [
                ft.ElevatedButton(
                    "Generate Graph",
                    on_click=generate_graph
                ),

                ft.ElevatedButton(
                    "Analyze Graph",
                    on_click=analyze_graph
                )
            ]
        ),

        graph_image,

        result_text
    )


ft.app(target=main)