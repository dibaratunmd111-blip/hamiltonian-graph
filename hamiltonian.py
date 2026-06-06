def hamiltonian_cycle(graph):
    n = len(graph)

    def backtrack(path):
        if len(path) == n:
            if path[0] in graph[path[-1]]:
                return path + [path[0]]
            return None

        for neighbor in graph[path[-1]]:
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


def hamiltonian_path(graph):
    n = len(graph)

    def backtrack(path):
        if len(path) == n:
            return path

        for neighbor in graph[path[-1]]:
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