import tkinter as tk
from tkinter import messagebox

# --- Graph as adjacency list ---
GRAPHS = {
    "Cycle (5 nodes)": {
        "nodes": [(300,100),(450,200),(400,350),(200,350),(150,200)],
        "edges": [(0,1),(1,2),(2,3),(3,4),(4,0)]
    },
    "Complete (4 nodes)": {
        "nodes": [(300,100),(450,280),(300,380),(150,280)],
        "edges": [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
    },
    "No Path (disconnected)": {
        "nodes": [(200,150),(350,150),(200,300),(350,300),(500,200)],
        "edges": [(0,1),(0,2),(1,3),(4,3)]
    },
}

class HamiltonianApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hamiltonian Path Finder")
        self.root.resizable(False, False)

        self.nodes = []
        self.edges = []
        self.adj   = {}
        self.path  = []
        self.found = False
        self._steps = []  # list of snapshots for step-through
        self._step_idx = 0

        self._build_ui()
        self._load_graph("Cycle (5 nodes)")

    def _build_ui(self):
        top = tk.Frame(self.root, pady=8, padx=8)
        top.pack(fill="x")

        tk.Label(top, text="Graph:").pack(side="left")
        self.graph_var = tk.StringVar(value="Cycle (5 nodes)")
        menu = tk.OptionMenu(top, self.graph_var, *GRAPHS.keys(),
                             command=self._load_graph)
        menu.pack(side="left", padx=6)

        tk.Button(top, text="Run Algorithm", command=self._run).pack(side="left", padx=4)
        tk.Button(top, text="← Prev Step",   command=self._prev_step).pack(side="left", padx=2)
        tk.Button(top, text="Next Step →",   command=self._next_step).pack(side="left", padx=2)
        tk.Button(top, text="Reset",         command=self._reset).pack(side="left", padx=4)

        self.status = tk.Label(top, text="Press 'Run Algorithm' to start.",
                               fg="blue", font=("Arial", 10, "italic"))
        self.status.pack(side="left", padx=10)

        self.canvas = tk.Canvas(self.root, width=620, height=420, bg="white",
                                relief="sunken", bd=2)
        self.canvas.pack(padx=8)

        bot = tk.Frame(self.root, pady=6, padx=8)
        bot.pack(fill="x")
        tk.Label(bot, text="Path so far:", font=("Arial", 10, "bold")).pack(side="left")
        self.path_label = tk.Label(bot, text="—", font=("Courier", 10), fg="#555")
        self.path_label.pack(side="left", padx=6)

        self.step_label = tk.Label(self.root, text="", font=("Arial", 9), fg="#777")
        self.step_label.pack(pady=(0,6))

        # legend
        leg = tk.Frame(self.root, pady=4)
        leg.pack()
        for color, txt in [("dodger blue","unvisited"),("orange","in path"),
                            ("green2","complete"),("red","backtrack")]:
            tk.Label(leg, text="●", fg=color, font=("Arial",14)).pack(side="left")
            tk.Label(leg, text=txt+"  ", font=("Arial",9), fg="#444").pack(side="left")

    # ── load graph ───────────────────────────────────────────────────────────
    def _load_graph(self, name):
        g = GRAPHS[name]
        self.nodes = g["nodes"]
        self.edges = g["edges"]
        self.adj   = {i: [] for i in range(len(self.nodes))}
        for a, b in self.edges:
            self.adj[a].append(b)
            self.adj[b].append(a)
        self._reset()

    def _reset(self):
        self.path      = []
        self.found     = False
        self._steps    = []
        self._step_idx = 0
        self.status.config(text="Press 'Run Algorithm' to start.", fg="blue")
        self.path_label.config(text="—")
        self.step_label.config(text="")
        self._draw()

    # ── Hamiltonian backtracking — collect all states ────────────────────────
    def _solve(self):
        n = len(self.nodes)
        path = [0]
        visited = {0}
        steps = []  # each entry: (path_copy, cur_edge, back_node, note)

        def record(cur_edge=None, back_node=None, note=""):
            steps.append((list(path), cur_edge, back_node, note))

        def bt():
            record(note=f"Trying to extend path of length {len(path)}")
            if len(path) == n:
                return True
            cur = path[-1]
            for nb in self.adj[cur]:
                if nb not in visited:
                    record(cur_edge=(cur,nb), note=f"Try edge {cur}→{nb}")
                    visited.add(nb); path.append(nb)
                    record(note=f"Added node {nb}, path length = {len(path)}")
                    if bt():
                        return True
                    # backtrack
                    path.pop(); visited.discard(nb)
                    record(back_node=nb, note=f"Backtrack: remove node {nb}")
            return False

        found = bt()
        if found:
            record(note="✓ Hamiltonian path found!")
        else:
            record(note="✗ No Hamiltonian path exists.")
        return found, steps

    def _run(self):
        self._reset()
        found, steps = self._solve()
        self.found    = found
        self._steps   = steps
        self._step_idx = 0
        self._show_step()
        msg = "Done! Use ← → buttons to step through." + (" Path FOUND ✓" if found else " No path ✗")
        self.status.config(text=msg, fg="green" if found else "red")

    # ── step navigation ───────────────────────────────────────────────────────
    def _show_step(self):
        if not self._steps:
            return
        path, cur_edge, back_node, note = self._steps[self._step_idx]
        total = len(self.path_label.master.master.winfo_children())  # unused, just drawing
        labels = [str(p) for p in path]
        self.path_label.config(text=" → ".join(labels) if path else "—")
        self.step_label.config(text=f"Step {self._step_idx+1}/{len(self._steps)}: {note}")
        self._draw(path=path, cur_edge=cur_edge, back_node=back_node)

    def _next_step(self):
        if not self._steps:
            messagebox.showinfo("Tip", "Click 'Run Algorithm' first!")
            return
        if self._step_idx < len(self._steps)-1:
            self._step_idx += 1
        self._show_step()

    def _prev_step(self):
        if not self._steps:
            return
        if self._step_idx > 0:
            self._step_idx -= 1
        self._show_step()

    # ── drawing ───────────────────────────────────────────────────────────────
    def _draw(self, path=None, cur_edge=None, back_node=None):
        c = self.canvas
        c.delete("all")
        if path is None:
            path = []
        n = len(self.nodes)
        complete = len(path) == n and n > 0

        path_edges = set()
        for i in range(len(path)-1):
            a, b = path[i], path[i+1]
            path_edges.add((min(a,b), max(a,b)))

        # draw edges
        for a, b in self.edges:
            key = (min(a,b), max(a,b))
            x1,y1 = self.nodes[a]; x2,y2 = self.nodes[b]
            if key in path_edges:
                color, width = ("green2" if complete else "orange"), 4
            else:
                color, width = "#cccccc", 1
            c.create_line(x1,y1,x2,y2, fill=color, width=width)

        # highlighted probing edge
        if cur_edge:
            a,b = cur_edge
            x1,y1 = self.nodes[a]; x2,y2 = self.nodes[b]
            col = "red" if back_node is not None else "orange"
            c.create_line(x1,y1,x2,y2, fill=col, width=3, dash=(6,4))

        # draw nodes
        R = 20
        path_set = set(path)
        for i, (x, y) in enumerate(self.nodes):
            if complete and i in path_set:
                fill = "green2"
            elif i == back_node:
                fill = "red"
            elif i in path_set:
                fill = "orange"
            elif path and i == path[0]:
                fill = "gray"
            else:
                fill = "dodger blue"

            c.create_oval(x-R,y-R,x+R,y+R, fill=fill, outline="white", width=2)
            c.create_text(x, y, text=str(i), fill="white", font=("Arial",11,"bold"))

root = tk.Tk()
app = HamiltonianApp(root)
root.mainloop()
