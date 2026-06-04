import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
import threading
import random

# ── colour palette ──────────────────────────────────────────────────────────
BG        = "#0f1117"
PANEL     = "#161b27"
BORDER    = "#252d3f"
NODE_DEF  = "#2563EB"   # unvisited
NODE_PATH = "#F59E0B"   # in current path
NODE_DONE = "#10B981"   # complete path
NODE_BACK = "#EF4444"   # backtracking
NODE_START= "#6B7280"   # start node highlight
EDGE_DEF  = "#252d3f"
EDGE_PATH = "#F59E0B"
EDGE_DONE = "#10B981"
TEXT_PRI  = "#F1F5F9"
TEXT_SEC  = "#64748B"
ACCENT    = "#3B82F6"
FONT_MONO = ("Courier New", 11)
FONT_HEAD = ("Courier New", 13, "bold")
FONT_SM   = ("Courier New", 10)

# ── preset graphs ────────────────────────────────────────────────────────────
def make_cycle(n, cx, cy, r):
    nodes, edges = [], []
    for i in range(n):
        a = 2*math.pi*i/n - math.pi/2
        nodes.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    edges = [(i, (i+1)%n) for i in range(n)]
    return nodes, edges

def make_complete(n, cx, cy, r):
    nodes, edges = [], []
    for i in range(n):
        a = 2*math.pi*i/n - math.pi/4
        nodes.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    edges = [(i,j) for i in range(n) for j in range(i+1,n)]
    return nodes, edges

def make_grid(rows, cols, cx, cy, gap):
    nodes, edges = [], []
    for r in range(rows):
        for c in range(cols):
            x = cx + (c - cols//2) * gap
            y = cy + (r - rows//2) * gap
            nodes.append((x, y))
    for r in range(rows):
        for c in range(cols):
            idx = r*cols+c
            if c+1 < cols: edges.append((idx, idx+1))
            if r+1 < rows: edges.append((idx, idx+cols))
    return nodes, edges

def make_petersen(cx, cy):
    nodes, edges = [], []
    for i in range(5):
        a = 2*math.pi*i/5 - math.pi/2
        nodes.append((cx+130*math.cos(a), cy+130*math.sin(a)))
    for i in range(5):
        a = 2*math.pi*i/5 - math.pi/2
        nodes.append((cx+60*math.cos(a), cy+60*math.sin(a)))
    for i in range(5):
        edges += [(i,(i+1)%5), (i,i+5)]
    for i in range(5):
        edges.append((i+5,(i+2)%5+5))
    return nodes, edges

def make_random(n, cx, cy, r, seed=42):
    random.seed(seed)
    nodes, edges = [], []
    for i in range(n):
        a = 2*math.pi*i/n
        nodes.append((cx+r*math.cos(a), cy+r*math.sin(a)))
    edge_set = {(i,(i+1)%n) for i in range(n)}
    extras = [(0,3),(1,5),(2,6),(3,7),(4,1),(6,2),(0,5),(2,7)]
    for a,b in extras:
        if random.random() < 0.65:
            edge_set.add((min(a,b),max(a,b)))
    return nodes, list(edge_set)

def make_impossible(cx, cy):
    nodes = [(cx,cy-120),(cx-100,cy),(cx+100,cy),(cx-100,cy+110),(cx+100,cy+110)]
    edges = [(0,1),(0,2),(1,2),(3,4)]
    return nodes, edges

PRESETS = {
    "Cycle (5)":        lambda cx,cy: make_cycle(5, cx, cy, 130),
    "Complete (4)":     lambda cx,cy: make_complete(4, cx, cy, 110),
    "Grid 3×3":         lambda cx,cy: make_grid(3, 3, cx, cy, 100),
    "Petersen-like":    lambda cx,cy: make_petersen(cx, cy),
    "Random (8)":       lambda cx,cy: make_random(8, cx, cy, 130),
    "No Ham. Path":     lambda cx,cy: make_impossible(cx, cy),
}

class HamiltonianApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hamiltonian Path — Backtracking Visualizer")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.nodes = []
        self.edges = []
        self.adj   = {}
        self.path       = []
        self.visited    = set()
        self.step_count = 0
        self.bt_count   = 0
        self.cur_edge   = None
        self.back_node  = None
        self.running    = False
        self.paused     = False
        self._thread    = None
        self._stop_evt  = threading.Event()

        self._build_ui()
        self._load_preset("Cycle (5)")

    # ── UI construction ──────────────────────────────────────────────────────
    def _build_ui(self):
        # left panel
        left = tk.Frame(self, bg=PANEL, width=210)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="HAMILTONIAN\nPATH FINDER",
                 font=("Courier New",14,"bold"), fg=ACCENT, bg=PANEL,
                 justify="left").pack(anchor="w", padx=18, pady=(22,4))
        tk.Label(left, text="backtracking algorithm",
                 font=FONT_SM, fg=TEXT_SEC, bg=PANEL).pack(anchor="w", padx=18, pady=(0,18))

        self._sep(left)

        tk.Label(left, text="GRAPH", font=FONT_SM, fg=TEXT_SEC, bg=PANEL).pack(anchor="w", padx=18, pady=(14,4))
        self.preset_var = tk.StringVar(value="Cycle (5)")
        for name in PRESETS:
            rb = tk.Radiobutton(left, text=name, variable=self.preset_var,
                                value=name, font=FONT_SM, fg=TEXT_PRI, bg=PANEL,
                                activebackground=PANEL, activeforeground=ACCENT,
                                selectcolor=BG, indicatoron=True,
                                command=lambda n=name: self._load_preset(n))
            rb.pack(anchor="w", padx=18, pady=1)

        self._sep(left)

        tk.Label(left, text="SPEED", font=FONT_SM, fg=TEXT_SEC, bg=PANEL).pack(anchor="w", padx=18, pady=(14,4))
        self.speed_var = tk.IntVar(value=5)
        spd = tk.Scale(left, from_=1, to=10, orient="horizontal",
                       variable=self.speed_var, bg=PANEL, fg=TEXT_PRI,
                       highlightthickness=0, troughcolor=BORDER, activebackground=ACCENT,
                       font=FONT_SM, sliderlength=16, bd=0, relief="flat")
        spd.pack(fill="x", padx=18)

        self._sep(left)

        # stats
        tk.Label(left, text="STATS", font=FONT_SM, fg=TEXT_SEC, bg=PANEL).pack(anchor="w", padx=18, pady=(14,4))
        self.lbl_nodes  = self._stat_row(left, "Nodes")
        self.lbl_edges  = self._stat_row(left, "Edges")
        self.lbl_steps  = self._stat_row(left, "Steps")
        self.lbl_bt     = self._stat_row(left, "Backtracks")
        self.lbl_status = self._stat_row(left, "Status")

        self._sep(left)

        # buttons
        btn_cfg = dict(font=FONT_MONO, fg=TEXT_PRI, bg=BORDER,
                       activebackground=ACCENT, activeforeground="#fff",
                       bd=0, relief="flat", cursor="hand2", pady=8)
        self.btn_run   = tk.Button(left, text="▶  Run", **btn_cfg, command=self._toggle_run)
        self.btn_run.pack(fill="x", padx=18, pady=(14,4))
        self.btn_step  = tk.Button(left, text="→  Step", **btn_cfg, command=self._do_step)
        self.btn_step.pack(fill="x", padx=18, pady=4)
        self.btn_reset = tk.Button(left, text="↺  Reset", **btn_cfg, command=self._reset)
        self.btn_reset.pack(fill="x", padx=18, pady=4)

        # right: canvas + log
        right = tk.Frame(self, bg=BG)
        right.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(right, width=620, height=380,
                                bg=BG, highlightthickness=0, bd=0)
        self.canvas.pack(padx=18, pady=(18,0))

        # path display
        path_f = tk.Frame(right, bg=PANEL, bd=0)
        path_f.pack(fill="x", padx=18, pady=(10,0))
        tk.Label(path_f, text="PATH →", font=FONT_SM, fg=TEXT_SEC, bg=PANEL).pack(side="left", padx=10, pady=6)
        self.path_lbl = tk.Label(path_f, text="—", font=FONT_MONO, fg=NODE_PATH, bg=PANEL, anchor="w")
        self.path_lbl.pack(side="left", padx=4, pady=6)

        # legend
        leg_f = tk.Frame(right, bg=BG)
        leg_f.pack(fill="x", padx=18, pady=(8,0))
        for col, txt in [(NODE_DEF,"unvisited"),(NODE_PATH,"in path"),(NODE_DONE,"found"),(NODE_BACK,"backtrack")]:
            c = tk.Canvas(leg_f, width=12, height=12, bg=BG, highlightthickness=0)
            c.create_oval(0,0,12,12,fill=col,outline="")
            c.pack(side="left", padx=(0,3))
            tk.Label(leg_f, text=txt, font=FONT_SM, fg=TEXT_SEC, bg=BG).pack(side="left", padx=(0,14))

        # log box
        log_f = tk.Frame(right, bg=PANEL)
        log_f.pack(fill="x", padx=18, pady=10)
        self.log_text = tk.Text(log_f, height=5, bg=PANEL, fg=TEXT_SEC,
                                font=FONT_SM, bd=0, relief="flat",
                                insertbackground=TEXT_PRI, state="disabled",
                                wrap="word")
        sb = tk.Scrollbar(log_f, command=self.log_text.yview, bg=PANEL, troughcolor=BORDER)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(fill="x", padx=8, pady=6)
        self.log_text.tag_configure("hi",  foreground=TEXT_PRI)
        self.log_text.tag_configure("ok",  foreground=NODE_DONE)
        self.log_text.tag_configure("err", foreground=NODE_BACK)

    def _sep(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=14, pady=6)

    def _stat_row(self, parent, label):
        f = tk.Frame(parent, bg=PANEL)
        f.pack(fill="x", padx=18, pady=1)
        tk.Label(f, text=label, font=FONT_SM, fg=TEXT_SEC, bg=PANEL, width=10, anchor="w").pack(side="left")
        val = tk.Label(f, text="—", font=FONT_MONO, fg=TEXT_PRI, bg=PANEL)
        val.pack(side="right")
        return val

    # ── graph loading ────────────────────────────────────────────────────────
    def _load_preset(self, name):
        self._stop_thread()
        cx, cy = 310, 185
        self.nodes, self.edges = PRESETS[name](cx, cy)
        self._build_adj()
        self._reset(redraw_only=False)

    def _build_adj(self):
        self.adj = {i: [] for i in range(len(self.nodes))}
        for a, b in self.edges:
            self.adj[a].append(b)
            self.adj[b].append(a)

    # ── state helpers ─────────────────────────────────────────────────────────
    def _reset(self, redraw_only=True):
        self._stop_thread()
        self.path       = []
        self.visited    = set()
        self.step_count = 0
        self.bt_count   = 0
        self.cur_edge   = None
        self.back_node  = None
        self._gen       = None
        self.lbl_nodes.config(text=str(len(self.nodes)))
        self.lbl_edges.config(text=str(len(self.edges)))
        self._update_stats()
        self._set_status("idle", TEXT_SEC)
        self.path_lbl.config(text="—", fg=NODE_PATH)
        self._clear_log()
        self.btn_run.config(text="▶  Run")
        self._draw()

    def _update_stats(self):
        self.lbl_steps.config(text=str(self.step_count))
        self.lbl_bt.config(text=str(self.bt_count))

    def _set_status(self, txt, color=TEXT_PRI):
        self.lbl_status.config(text=txt, fg=color)

    def _update_path_label(self):
        if not self.path:
            self.path_lbl.config(text="—")
            return
        labels = [chr(65+i) if len(self.nodes)<=26 else str(i) for i in self.path]
        self.path_lbl.config(text=" → ".join(labels))

    def _log(self, msg, tag=""):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg+"\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0","end")
        self.log_text.configure(state="disabled")

    # ── drawing ───────────────────────────────────────────────────────────────
    def _draw(self):
        c = self.canvas
        c.delete("all")
        n = len(self.nodes)
        complete = len(self.path) == n and n > 0
        path_set = set(self.path)
        path_edges = set()
        for i in range(len(self.path)-1):
            a,b = self.path[i], self.path[i+1]
            path_edges.add((min(a,b),max(a,b)))

        # edges
        for a, b in self.edges:
            key = (min(a,b), max(a,b))
            xa,ya = self.nodes[a]; xb,yb = self.nodes[b]
            if key in path_edges:
                col = EDGE_DONE if complete else EDGE_PATH
                w = 3
            else:
                col = EDGE_DEF
                w = 1
            c.create_line(xa,ya,xb,yb, fill=col, width=w)

        # highlighted edge (probing)
        if self.cur_edge:
            a,b = self.cur_edge
            xa,ya = self.nodes[a]; xb,yb = self.nodes[b]
            col = NODE_BACK if self.back_node is not None else "#F59E0B44"
            c.create_line(xa,ya,xb,yb, fill=col, width=3, dash=(6,4))

        # nodes
        R = 18
        for i, (x, y) in enumerate(self.nodes):
            if complete and i in path_set:
                col = NODE_DONE
            elif i == self.back_node:
                col = NODE_BACK
            elif i in path_set:
                col = NODE_PATH
            elif self.path and i == self.path[0]:
                col = NODE_START
            else:
                col = NODE_DEF
            c.create_oval(x-R,y-R,x+R,y+R, fill=col, outline="#ffffff22", width=2)
            lbl = chr(65+i) if n <= 26 else str(i)
            c.create_text(x, y, text=lbl, fill="#ffffff", font=("Courier New",11,"bold"))

    # ── algorithm (generator) ────────────────────────────────────────────────
    def _hamiltonian_gen(self):
        n = len(self.nodes)
        self.path = [0]
        self.visited = {0}

        def bt():
            self.step_count += 1
            self._update_stats()
            if len(self.path) == n:
                return True
            cur = self.path[-1]
            for nb in self.adj[cur]:
                if nb not in self.visited:
                    self.cur_edge = (cur, nb)
                    self.back_node = None
                    self._draw(); self._update_path_label()
                    lbl = lambda i: chr(65+i) if n<=26 else str(i)
                    self._log(f"  try {lbl(cur)}→{lbl(nb)}", "hi")
                    yield  # pause point
                    self.visited.add(nb); self.path.append(nb)
                    self._draw(); self._update_path_label()
                    yield
                    result = yield from bt()
                    if result:
                        return True
                    self.path.pop(); self.visited.discard(nb)
                    self.bt_count += 1
                    self.back_node = nb
                    self.cur_edge = None
                    self._log(f"  ↩ backtrack from {lbl(nb)}", "err")
                    self._draw(); self._update_path_label()
                    yield
                    self.back_node = None
            return False

        found = yield from bt()
        self.cur_edge = None; self.back_node = None
        if found:
            self._set_status("found ✓", NODE_DONE)
            self._log("✓ Hamiltonian path found!", "ok")
        else:
            self.path = []
            self._set_status("no path ✗", NODE_BACK)
            self._log("✗ No Hamiltonian path exists.", "err")
            self._update_path_label()
        self._draw()

    # ── controls ──────────────────────────────────────────────────────────────
    def _ensure_gen(self):
        if not hasattr(self, '_gen') or self._gen is None:
            self._gen = self._hamiltonian_gen()
            self._set_status("running", NODE_PATH)

    def _do_step(self):
        self._stop_thread()
        self.btn_run.config(text="▶  Run")
        self._ensure_gen()
        try:
            next(self._gen)
        except StopIteration:
            self._gen = None

    def _toggle_run(self):
        if self.running:
            self.running = False
            self._stop_evt.set()
            self.btn_run.config(text="▶  Run")
        else:
            self._ensure_gen()
            self.running = True
            self._stop_evt.clear()
            self.btn_run.config(text="⏸  Pause")
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def _run_loop(self):
        while self.running and not self._stop_evt.is_set():
            try:
                self.after(0, self._step_once)
                delay = max(0.03, 0.65 / self.speed_var.get())
                time.sleep(delay)
            except Exception:
                break

    def _step_once(self):
        if self._gen is None:
            return
        try:
            next(self._gen)
        except StopIteration:
            self._gen = None
            self.running = False
            self.btn_run.config(text="▶  Run")

    def _stop_thread(self):
        self.running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        self._thread = None
        self._stop_evt.clear()

    def on_close(self):
        self._stop_thread()
        self.destroy()

if __name__ == "__main__":
    app = HamiltonianApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()