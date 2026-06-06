class Graph:

    def __init__(self):
        self.vertices = {}
        self.edges = []

    def add_vertex(self, name, x, y):
        self.vertices[name] = (x, y)

    def add_edge(self, v1, v2):
        if (v1, v2) not in self.edges and (v2, v1) not in self.edges:
            self.edges.append((v1, v2))

    def clear(self):
        self.vertices.clear()
        self.edges.clear()

    def adjacency_list(self):
        graph = {}

        for v in self.vertices:
            graph[v] = []

        for a, b in self.edges:
            graph[a].append(b)
            graph[b].append(a)

        return graph