import tkinter as tk

# Graph as an adjacency list (0-indexed)
graph = {
    0: [1, 2],
    1: [0, 2, 3],
    2: [0, 1, 4],
    3: [1, 4],
    4: [2, 3]
}

def find_hamiltonian_path(graph, path, visited):
    if len(path) == len(graph):
        return True  # all nodes visited!

    current = path[-1]
    for neighbor in graph[current]:
        if neighbor not in visited:
            path.append(neighbor)
            visited.add(neighbor)

            if find_hamiltonian_path(graph, path, visited):
                return True

            # backtrack
            path.pop()
            visited.remove(neighbor)

    return False

def run():
    start = int(start_var.get())
    path = [start]
    visited = {start}

    if find_hamiltonian_path(graph, path, visited):
        result_label.config(text="Path found: " + " → ".join(str(n) for n in path), fg="green")
    else:
        result_label.config(text="No Hamiltonian path found.", fg="red")

# --- Simple UI ---
window = tk.Tk()
window.title("Hamiltonian Path")
window.geometry("400x200")

tk.Label(window, text="Hamiltonian Path Finder", font=("Arial", 14, "bold")).pack(pady=10)
tk.Label(window, text="Start node (0–4):").pack()

start_var = tk.StringVar(value="0")
tk.Entry(window, textvariable=start_var, width=5).pack()

tk.Button(window, text="Find Path", command=run).pack(pady=10)

result_label = tk.Label(window, text="", font=("Arial", 11))
result_label.pack()

window.mainloop()
