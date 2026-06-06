def hamiltonian_circuit(graph):
    n = len(graph)

    def backtrack(path):
        if len(path) == n:
            if graph[path[-1]][path[0]] == 1:
                return path + [path[0]]
            return None

        for v in range(n):
            if v not in path and graph[path[-1]][v] == 1:
                result = backtrack(path + [v])
                if result:
                    return result
        return None

    return backtrack([0])


def hamiltonian_path(graph):
    n = len(graph)

    def backtrack(path):
        if len(path) == n:
            return path

        for v in range(n):
            if v not in path and graph[path[-1]][v] == 1:
                result = backtrack(path + [v])
                if result:
                    return result
        return None

    for start in range(n):
        result = backtrack([start])
        if result:
            return result

    return None


n = int(input("Number of Vertices: "))

print("\nEnter Adjacency Matrix:")

graph = []
for i in range(n):
    row = list(map(int, input().split()))
    graph.append(row)

circuit = hamiltonian_circuit(graph)

if circuit:
    print("\nClassification: Hamiltonian Circuit")
    print("Circuit:", " -> ".join(map(str, circuit)))

else:
    path = hamiltonian_path(graph)

    if path:
        print("\nClassification: Hamiltonian Path")
        print("Path:", " -> ".join(map(str, path)))
    else:
        print("\nClassification: Neither")