import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import csv
import hashlib
from datetime import datetime
from collections import defaultdict

DB_NAME = "diabetes_tracker.db"

# ─────────────────────────────────────────
# CULORI SI STIL
# ─────────────────────────────────────────
BG         = "#0f1923"
BG2        = "#162330"
BG3        = "#1e3045"
ACCENT     = "#00c9a7"
ACCENT2    = "#0099cc"
TEXT       = "#e8f4f8"
TEXT_DIM   = "#7a9ab0"
RED        = "#e05c5c"
YELLOW     = "#f0c060"
GREEN      = "#00c9a7"
FONT       = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_BIG   = ("Segoe UI", 14, "bold")
FONT_TITLE = ("Segoe UI", 18, "bold")

# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────

def get_conn():
    return sqlite3.connect(DB_NAME)

def create_tables():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, date TEXT,
            fasting_glucose REAL, water_glasses INTEGER,
            steps INTEGER, carbs INTEGER)""")
        c.execute("""CREATE TABLE IF NOT EXISTS hba1c (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, date TEXT, value REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS weight (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, date TEXT, kg REAL)""")

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def glycemia_state(g):
    if g < 70:   return "Hipoglicemie", RED
    if g <= 130: return "Normal", GREEN
    return "Hiperglicemie", RED

def hba1c_state(v):
    if v <= 5.6: return "Normal", GREEN
    if v <= 6.4: return "Prediabet", YELLOW
    if v <= 7.0: return "Control bun", YELLOW
    return "Consultati medicul", RED

# ─────────────────────────────────────────
# WIDGET HELPERS
# ─────────────────────────────────────────

def styled_frame(parent, **kw):
    kw.setdefault("bg", BG2)
    kw.setdefault("relief", "flat")
    return tk.Frame(parent, **kw)

def styled_label(parent, text, font=FONT, fg=TEXT, **kw):
    kw.setdefault("bg", BG2)
    return tk.Label(parent, text=text, font=font, fg=fg, **kw)

def styled_entry(parent, **kw):
    e = tk.Entry(parent, bg=BG3, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", font=FONT,
                 highlightthickness=1, highlightcolor=ACCENT,
                 highlightbackground=BG3, **kw)
    return e

def styled_button(parent, text, command, color=ACCENT, **kw):
    b = tk.Button(parent, text=text, command=command,
                  bg=color, fg=BG, font=FONT_BOLD,
                  relief="flat", cursor="hand2",
                  activebackground=ACCENT2, activeforeground=BG,
                  padx=12, pady=6, **kw)
    return b

def section_label(parent, text):
    f = tk.Frame(parent, bg=BG2)
    tk.Label(f, text=text, font=FONT_BIG, fg=ACCENT, bg=BG2).pack(anchor="w")
    tk.Frame(f, bg=ACCENT, height=2).pack(fill="x", pady=(2, 8))
    return f

# ─────────────────────────────────────────
# FEREASTRA LOGIN / REGISTER
# ─────────────────────────────────────────

class AuthWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Diabetes Tracker — Login")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.user_id = None
        self.username = None
        self._center(400, 480)
        self._build()
        self.root.mainloop()

    def _center(self, w, h):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build(self):
        main = tk.Frame(self.root, bg=BG, padx=40, pady=40)
        main.pack(fill="both", expand=True)

        # Logo
        tk.Label(main, text="🩺", font=("Segoe UI", 40), bg=BG, fg=ACCENT).pack()
        tk.Label(main, text="Diabetes Tracker", font=FONT_TITLE, bg=BG, fg=TEXT).pack()
        tk.Label(main, text="v2.0", font=FONT, bg=BG, fg=TEXT_DIM).pack(pady=(0, 20))

        # Tab buttons
        tab_frame = tk.Frame(main, bg=BG3, relief="flat")
        tab_frame.pack(fill="x", pady=(0, 20))
        self.mode = tk.StringVar(value="login")
        for text, val in [("Login", "login"), ("Register", "register")]:
            tk.Radiobutton(tab_frame, text=text, variable=self.mode,
                           value=val, command=self._switch_mode,
                           bg=BG3, fg=TEXT, selectcolor=ACCENT,
                           activebackground=BG3, font=FONT_BOLD,
                           indicatoron=False, relief="flat",
                           padx=20, pady=8).pack(side="left", fill="x", expand=True)

        # Form
        form = tk.Frame(main, bg=BG)
        form.pack(fill="x")

        tk.Label(form, text="Username", font=FONT, bg=BG, fg=TEXT_DIM).pack(anchor="w")
        self.entry_user = styled_entry(form)
        self.entry_user.pack(fill="x", pady=(2, 10))

        tk.Label(form, text="Parola", font=FONT, bg=BG, fg=TEXT_DIM).pack(anchor="w")
        self.entry_pw = styled_entry(form, show="●")
        self.entry_pw.pack(fill="x", pady=(2, 10))

        self.label_confirm = tk.Label(form, text="Confirma parola", font=FONT, bg=BG, fg=TEXT_DIM)
        self.entry_confirm = styled_entry(form, show="●")

        self.btn = styled_button(form, "Login", self._submit)
        self.btn.pack(fill="x", pady=(10, 0))

        self.msg = tk.Label(form, text="", font=FONT, bg=BG, fg=RED, wraplength=300)
        self.msg.pack(pady=5)

        self.entry_user.bind("<Return>", lambda e: self.entry_pw.focus())
        self.entry_pw.bind("<Return>", lambda e: self._submit())

    def _switch_mode(self):
        if self.mode.get() == "register":
            self.label_confirm.pack(anchor="w", before=self.btn)
            self.entry_confirm.pack(fill="x", pady=(2, 10), before=self.btn)
            self.btn.config(text="Creeaza cont")
        else:
            self.label_confirm.pack_forget()
            self.entry_confirm.pack_forget()
            self.btn.config(text="Login")

    def _submit(self):
        user = self.entry_user.get().strip()
        pw   = self.entry_pw.get().strip()
        if not user or not pw:
            self.msg.config(text="Completati toate campurile.")
            return

        if self.mode.get() == "login":
            with get_conn() as conn:
                row = conn.cursor().execute(
                    "SELECT id FROM users WHERE username=? AND password_hash=?",
                    (user, hash_pw(pw))
                ).fetchone()
            if row:
                self.user_id = row[0]
                self.username = user
                self.root.destroy()
            else:
                self.msg.config(text="Username sau parola incorecte.")
        else:
            confirm = self.entry_confirm.get().strip()
            if pw != confirm:
                self.msg.config(text="Parolele nu coincid.")
                return
            if len(pw) < 4:
                self.msg.config(text="Parola trebuie sa aiba minim 4 caractere.")
                return
            try:
                with get_conn() as conn:
                    c = conn.cursor()
                    c.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",
                              (user, hash_pw(pw)))
                    self.user_id = c.lastrowid
                    self.username = user
                self.root.destroy()
            except sqlite3.IntegrityError:
                self.msg.config(text="Username deja exista.")

# ─────────────────────────────────────────
# FEREASTRA PRINCIPALA
# ─────────────────────────────────────────

class App:
    def __init__(self, user_id, username):
        self.user_id  = user_id
        self.username = username

        self.root = tk.Tk()
        self.root.title(f"Diabetes Tracker — {username}")
        self.root.configure(bg=BG)
        self.root.minsize(900, 620)
        self._center(1000, 680)
        self._build()
        self.show_page("measurements")
        self.root.mainloop()

    def _center(self, w, h):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build(self):
        # ── Sidebar ──
        sidebar = tk.Frame(self.root, bg=BG, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🩺", font=("Segoe UI", 28), bg=BG, fg=ACCENT).pack(pady=(20, 2))
        tk.Label(sidebar, text="Diabetes\nTracker", font=FONT_BOLD, bg=BG, fg=TEXT, justify="center").pack()
        tk.Label(sidebar, text=f"👤 {self.username}", font=FONT, bg=BG, fg=TEXT_DIM).pack(pady=(4, 20))

        tk.Frame(sidebar, bg=BG3, height=1).pack(fill="x", padx=10)

        self.nav_buttons = {}
        nav_items = [
            ("measurements", "📋  Masuratori"),
            ("hba1c",        "🧪  HbA1c"),
            ("weight",       "⚖️   Greutate"),
            ("analysis",     "📊  Analiza"),
            ("export",       "📄  Export CSV"),
        ]
        for key, label in nav_items:
            b = tk.Button(sidebar, text=label, font=FONT,
                          bg=BG, fg=TEXT_DIM, relief="flat",
                          anchor="w", padx=20, pady=10,
                          cursor="hand2", activebackground=BG3,
                          activeforeground=TEXT,
                          command=lambda k=key: self.show_page(k))
            b.pack(fill="x")
            self.nav_buttons[key] = b

        tk.Frame(sidebar, bg=BG3, height=1).pack(fill="x", padx=10, pady=10)
        tk.Button(sidebar, text="🚪  Logout", font=FONT,
                  bg=BG, fg=RED, relief="flat",
                  anchor="w", padx=20, pady=8,
                  cursor="hand2", command=self._logout).pack(fill="x")

        # ── Content ──
        self.content = tk.Frame(self.root, bg=BG2)
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {}

    def _logout(self):
        self.root.destroy()

    def show_page(self, name):
        # highlight nav
        for k, b in self.nav_buttons.items():
            b.config(bg=BG if k != name else BG3, fg=TEXT_DIM if k != name else ACCENT)

        # destroy old page
        for w in self.content.winfo_children():
            w.destroy()

        pages = {
            "measurements": MeasurementsPage,
            "hba1c":        HbA1cPage,
            "weight":       WeightPage,
            "analysis":     AnalysisPage,
            "export":       ExportPage,
        }
        pages[name](self.content, self.user_id)

# ─────────────────────────────────────────
# PAGINA MASURATORI
# ─────────────────────────────────────────

class MeasurementsPage:
    def __init__(self, parent, user_id):
        self.parent  = parent
        self.user_id = user_id
        self._build()

    def _build(self):
        pad = tk.Frame(self.parent, bg=BG2, padx=30, pady=20)
        pad.pack(fill="both", expand=True)

        section_label(pad, "📋  Masuratori zilnice").pack(fill="x")

        # Form
        form = styled_frame(pad)
        form.pack(fill="x", pady=(0, 15))

        fields = [
            ("Data (YYYY-MM-DD)", "date"),
            ("Glucoza (mg/dL)", "glucose"),
            ("Pahare apa", "water"),
            ("Pasi", "steps"),
            ("Carbohidrati (g)", "carbs"),
        ]
        self.entries = {}
        cols = tk.Frame(form, bg=BG2)
        cols.pack(fill="x")
        for i, (label, key) in enumerate(fields):
            col = tk.Frame(cols, bg=BG2)
            col.pack(side="left", fill="x", expand=True, padx=(0, 8))
            tk.Label(col, text=label, font=FONT, fg=TEXT_DIM, bg=BG2).pack(anchor="w")
            e = styled_entry(col)
            e.pack(fill="x", pady=(2, 0))
            self.entries[key] = e

        # default date
        self.entries["date"].insert(0, datetime.now().strftime("%Y-%m-%d"))

        btn_row = tk.Frame(pad, bg=BG2)
        btn_row.pack(fill="x", pady=(8, 0))
        styled_button(btn_row, "➕  Adauga", self._add).pack(side="left", padx=(0, 8))
        styled_button(btn_row, "🗑  Sterge selectat", self._delete, color=RED).pack(side="left", padx=(0, 8))
        styled_button(btn_row, "✏️  Modifica selectat", self._modify, color=ACCENT2).pack(side="left")

        # Table
        cols_def = ("Data", "Glucoza", "Apa", "Pasi", "Carbs", "Status")
        self.tree = self._make_tree(pad, cols_def)
        self.tree.pack(fill="both", expand=True, pady=(10, 0))

        self._load()

    def _make_tree(self, parent, columns):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
            background=BG3, foreground=TEXT,
            fieldbackground=BG3, rowheight=28,
            font=FONT, borderwidth=0)
        style.configure("Custom.Treeview.Heading",
            background=BG, foreground=ACCENT,
            font=FONT_BOLD, relief="flat")
        style.map("Custom.Treeview",
            background=[("selected", ACCENT2)],
            foreground=[("selected", BG)])

        frame = tk.Frame(parent, bg=BG3)
        tree = ttk.Treeview(frame, columns=columns, show="headings",
                            style="Custom.Treeview")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return frame

    def _load(self):
        # get the actual Treeview widget inside the frame
        tv = self.tree.winfo_children()[0]
        for row in tv.get_children():
            tv.delete(row)
        with get_conn() as conn:
            rows = conn.cursor().execute(
                "SELECT date, fasting_glucose, water_glasses, steps, carbs FROM measurements WHERE user_id=? ORDER BY date DESC",
                (self.user_id,)
            ).fetchall()
        for r in rows:
            status, color = glycemia_state(r[1])
            tv.insert("", "end", values=(r[0], f"{r[1]} mg/dL", f"{r[2]} pahare", r[3], f"{r[4]}g", status))

    def _get_tv(self):
        return self.tree.winfo_children()[0]

    def _add(self):
        try:
            date    = self.entries["date"].get().strip()
            glucose = float(self.entries["glucose"].get())
            water   = int(self.entries["water"].get())
            steps   = int(self.entries["steps"].get())
            carbs   = int(self.entries["carbs"].get())
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Eroare", "Verificati valorile introduse.")
            return
        with get_conn() as conn:
            conn.cursor().execute(
                "INSERT INTO measurements(user_id,date,fasting_glucose,water_glasses,steps,carbs) VALUES(?,?,?,?,?,?)",
                (self.user_id, date, glucose, water, steps, carbs)
            )
        for key in ["glucose","water","steps","carbs"]:
            self.entries[key].delete(0, "end")
        self._load()
        messagebox.showinfo("Succes", "Masurare adaugata!")

    def _delete(self):
        tv = self._get_tv()
        sel = tv.selection()
        if not sel:
            messagebox.showwarning("Atentie", "Selectati un rand.")
            return
        date = tv.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmare", f"Stergi inregistrarea din {date}?"):
            with get_conn() as conn:
                conn.cursor().execute(
                    "DELETE FROM measurements WHERE user_id=? AND date=?",
                    (self.user_id, date)
                )
            self._load()

    def _modify(self):
        tv = self._get_tv()
        sel = tv.selection()
        if not sel:
            messagebox.showwarning("Atentie", "Selectati un rand.")
            return
        vals = tv.item(sel[0])["values"]
        date = vals[0]

        win = tk.Toplevel()
        win.title("Modifica masurare")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text=f"Modifica: {date}", font=FONT_BOLD, bg=BG, fg=ACCENT).pack(pady=(15,5))

        with get_conn() as conn:
            rec = conn.cursor().execute(
                "SELECT fasting_glucose, water_glasses, steps, carbs FROM measurements WHERE user_id=? AND date=?",
                (self.user_id, date)
            ).fetchone()

        frame = tk.Frame(win, bg=BG, padx=20, pady=10)
        frame.pack()
        labels = ["Glucoza", "Apa (pahare)", "Pasi", "Carbs (g)"]
        entries = []
        for i, (lbl, val) in enumerate(zip(labels, rec)):
            tk.Label(frame, text=lbl, font=FONT, bg=BG, fg=TEXT_DIM).grid(row=i, column=0, sticky="w", pady=4)
            e = styled_entry(frame, width=15)
            e.insert(0, str(val))
            e.grid(row=i, column=1, padx=(10,0), pady=4)
            entries.append(e)

        def save():
            try:
                g = float(entries[0].get())
                w = int(entries[1].get())
                s = int(entries[2].get())
                c = int(entries[3].get())
            except ValueError:
                messagebox.showerror("Eroare", "Valori invalide.")
                return
            with get_conn() as conn:
                conn.cursor().execute(
                    "UPDATE measurements SET fasting_glucose=?,water_glasses=?,steps=?,carbs=? WHERE user_id=? AND date=?",
                    (g, w, s, c, self.user_id, date)
                )
            win.destroy()
            self._load()

        styled_button(frame, "Salveaza", save).grid(row=len(labels), column=0, columnspan=2, pady=15)

# ─────────────────────────────────────────
# PAGINA HbA1c
# ─────────────────────────────────────────

class HbA1cPage:
    def __init__(self, parent, user_id):
        self.parent  = parent
        self.user_id = user_id
        self._build()

    def _build(self):
        pad = tk.Frame(self.parent, bg=BG2, padx=30, pady=20)
        pad.pack(fill="both", expand=True)
        section_label(pad, "🧪  HbA1c (la 3 luni)").pack(fill="x")

        form = tk.Frame(pad, bg=BG2)
        form.pack(fill="x", pady=(0,15))

        tk.Label(form, text="Data", font=FONT, fg=TEXT_DIM, bg=BG2).grid(row=0, column=0, sticky="w")
        self.e_date = styled_entry(form, width=15)
        self.e_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.e_date.grid(row=1, column=0, padx=(0,10))

        tk.Label(form, text="Valoare HbA1c (%)", font=FONT, fg=TEXT_DIM, bg=BG2).grid(row=0, column=1, sticky="w")
        self.e_val = styled_entry(form, width=10)
        self.e_val.grid(row=1, column=1, padx=(0,10))

        styled_button(form, "➕ Adauga", self._add).grid(row=1, column=2, padx=(0,8))
        styled_button(form, "🗑 Sterge", self._delete, color=RED).grid(row=1, column=3)

        style = ttk.Style()
        style.configure("Custom.Treeview", background=BG3, foreground=TEXT,
                        fieldbackground=BG3, rowheight=28, font=FONT)
        style.configure("Custom.Treeview.Heading", background=BG, foreground=ACCENT, font=FONT_BOLD)

        frame = tk.Frame(pad, bg=BG3)
        frame.pack(fill="both", expand=True)
        self.tv = ttk.Treeview(frame, columns=("Data","Valoare","Status"), show="headings", style="Custom.Treeview")
        for col in ("Data","Valoare","Status"):
            self.tv.heading(col, text=col)
            self.tv.column(col, width=200, anchor="center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tv.yview)
        self.tv.configure(yscrollcommand=sb.set)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._load()

    def _load(self):
        for r in self.tv.get_children(): self.tv.delete(r)
        with get_conn() as conn:
            rows = conn.cursor().execute(
                "SELECT date, value FROM hba1c WHERE user_id=? ORDER BY date DESC",
                (self.user_id,)
            ).fetchall()
        for r in rows:
            status, _ = hba1c_state(r[1])
            self.tv.insert("", "end", values=(r[0], f"{r[1]}%", status))

    def _add(self):
        try:
            date = self.e_date.get().strip()
            val  = float(self.e_val.get())
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Eroare", "Verificati valorile.")
            return
        with get_conn() as conn:
            conn.cursor().execute(
                "INSERT INTO hba1c(user_id,date,value) VALUES(?,?,?)",
                (self.user_id, date, val)
            )
        self.e_val.delete(0,"end")
        self._load()
        messagebox.showinfo("Succes", f"HbA1c adaugat! Status: {hba1c_state(val)[0]}")

    def _delete(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Atentie","Selectati un rand.")
            return
        date = self.tv.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmare", f"Stergi inregistrarea din {date}?"):
            with get_conn() as conn:
                conn.cursor().execute("DELETE FROM hba1c WHERE user_id=? AND date=?", (self.user_id, date))
            self._load()

# ─────────────────────────────────────────
# PAGINA GREUTATE
# ─────────────────────────────────────────

class WeightPage:
    def __init__(self, parent, user_id):
        self.parent  = parent
        self.user_id = user_id
        self._build()

    def _build(self):
        pad = tk.Frame(self.parent, bg=BG2, padx=30, pady=20)
        pad.pack(fill="both", expand=True)
        section_label(pad, "⚖️  Greutate (lunar)").pack(fill="x")

        form = tk.Frame(pad, bg=BG2)
        form.pack(fill="x", pady=(0,15))

        tk.Label(form, text="Data", font=FONT, fg=TEXT_DIM, bg=BG2).grid(row=0, column=0, sticky="w")
        self.e_date = styled_entry(form, width=15)
        self.e_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.e_date.grid(row=1, column=0, padx=(0,10))

        tk.Label(form, text="Greutate (kg)", font=FONT, fg=TEXT_DIM, bg=BG2).grid(row=0, column=1, sticky="w")
        self.e_kg = styled_entry(form, width=10)
        self.e_kg.grid(row=1, column=1, padx=(0,10))

        styled_button(form, "➕ Adauga", self._add).grid(row=1, column=2, padx=(0,8))
        styled_button(form, "🗑 Sterge", self._delete, color=RED).grid(row=1, column=3)

        style = ttk.Style()
        style.configure("Custom.Treeview", background=BG3, foreground=TEXT,
                        fieldbackground=BG3, rowheight=28, font=FONT)
        style.configure("Custom.Treeview.Heading", background=BG, foreground=ACCENT, font=FONT_BOLD)

        frame = tk.Frame(pad, bg=BG3)
        frame.pack(fill="both", expand=True)
        self.tv = ttk.Treeview(frame, columns=("Data","Greutate","Diferenta"), show="headings", style="Custom.Treeview")
        for col, w in [("Data",200),("Greutate",150),("Diferenta",200)]:
            self.tv.heading(col, text=col)
            self.tv.column(col, width=w, anchor="center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tv.yview)
        self.tv.configure(yscrollcommand=sb.set)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._load()

    def _load(self):
        for r in self.tv.get_children(): self.tv.delete(r)
        with get_conn() as conn:
            rows = conn.cursor().execute(
                "SELECT date, kg FROM weight WHERE user_id=? ORDER BY date DESC",
                (self.user_id,)
            ).fetchall()
        prev = None
        for r in rows:
            if prev is not None:
                diff = r[1] - prev
                diff_str = f"+{diff:.1f} kg" if diff > 0 else f"{diff:.1f} kg"
            else:
                diff_str = "—"
            self.tv.insert("", "end", values=(r[0], f"{r[1]} kg", diff_str))
            prev = r[1]

    def _add(self):
        try:
            date = self.e_date.get().strip()
            kg   = float(self.e_kg.get())
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Eroare", "Verificati valorile.")
            return
        with get_conn() as conn:
            conn.cursor().execute("INSERT INTO weight(user_id,date,kg) VALUES(?,?,?)",
                                  (self.user_id, date, kg))
        self.e_kg.delete(0,"end")
        self._load()
        messagebox.showinfo("Succes", "Greutate adaugata!")

    def _delete(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Atentie","Selectati un rand.")
            return
        date = self.tv.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmare", f"Stergi inregistrarea din {date}?"):
            with get_conn() as conn:
                conn.cursor().execute("DELETE FROM weight WHERE user_id=? AND date=?", (self.user_id, date))
            self._load()

# ─────────────────────────────────────────
# PAGINA ANALIZA
# ─────────────────────────────────────────

class AnalysisPage:
    def __init__(self, parent, user_id):
        self.parent  = parent
        self.user_id = user_id
        self._build()

    def _build(self):
        pad = tk.Frame(self.parent, bg=BG2, padx=30, pady=20)
        pad.pack(fill="both", expand=True)
        section_label(pad, "📊  Analiza & Statistici").pack(fill="x")

        # scroll area
        canvas = tk.Canvas(pad, bg=BG2, highlightthickness=0)
        sb = ttk.Scrollbar(pad, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG2)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._build_stats(scroll_frame)

    def _card(self, parent, title, content_fn):
        card = tk.Frame(parent, bg=BG3, padx=20, pady=15)
        card.pack(fill="x", pady=(0, 12))
        tk.Label(card, text=title, font=FONT_BOLD, fg=ACCENT, bg=BG3).pack(anchor="w")
        tk.Frame(card, bg=BG3, height=1).pack(fill="x", pady=5)
        content_fn(card)
        return card

    def _row(self, parent, label, value, color=TEXT):
        f = tk.Frame(parent, bg=BG3)
        f.pack(fill="x", pady=2)
        tk.Label(f, text=label, font=FONT, fg=TEXT_DIM, bg=BG3, width=30, anchor="w").pack(side="left")
        tk.Label(f, text=value, font=FONT_BOLD, fg=color, bg=BG3).pack(side="left")

    def _build_stats(self, parent):
        with get_conn() as conn:
            c = conn.cursor()
            m_rows = c.execute(
                "SELECT fasting_glucose, water_glasses, steps, carbs, date FROM measurements WHERE user_id=? ORDER BY date",
                (self.user_id,)
            ).fetchall()
            h_rows = c.execute(
                "SELECT date, value FROM hba1c WHERE user_id=? ORDER BY date DESC LIMIT 5",
                (self.user_id,)
            ).fetchall()
            w_rows = c.execute(
                "SELECT date, kg FROM weight WHERE user_id=? ORDER BY date DESC LIMIT 5",
                (self.user_id,)
            ).fetchall()

        # ── Glucoza ──
        def glucose_content(card):
            if not m_rows:
                tk.Label(card, text="Nu exista date.", font=FONT, fg=TEXT_DIM, bg=BG3).pack(anchor="w")
                return
            vals = [r[0] for r in m_rows]
            avg = sum(vals) / len(vals)
            mn  = min(vals)
            mx  = max(vals)
            total = len(vals)
            low    = sum(1 for v in vals if v < 70)
            normal = sum(1 for v in vals if 70 <= v <= 130)
            high   = sum(1 for v in vals if v > 130)
            s, color = glycemia_state(avg)
            self._row(card, "Medie glucoza:", f"{avg:.1f} mg/dL  ({s})", color)
            self._row(card, "Minim:", f"{mn:.1f} mg/dL")
            self._row(card, "Maxim:", f"{mx:.1f} mg/dL")
            self._row(card, "In range (70-130):", f"{normal}/{total}  ({normal/total*100:.1f}%)", GREEN)
            self._row(card, "Sub 70 (hipoglicemie):", f"{low}/{total}  ({low/total*100:.1f}%)", RED if low > 0 else TEXT)
            self._row(card, "Peste 130 (hiperglicemie):", f"{high}/{total}  ({high/total*100:.1f}%)", RED if high > 0 else TEXT)

        self._card(parent, "🩸  Statistici Glucoza", glucose_content)

        # ── HbA1c trend ──
        def hba1c_content(card):
            if len(h_rows) < 2:
                tk.Label(card, text="Minim 2 inregistrari necesare.", font=FONT, fg=TEXT_DIM, bg=BG3).pack(anchor="w")
                if h_rows:
                    s, color = hba1c_state(h_rows[0][1])
                    self._row(card, h_rows[0][0], f"{h_rows[0][1]:.1f}%  {s}", color)
                return
            for r in h_rows:
                s, color = hba1c_state(r[1])
                self._row(card, r[0], f"{r[1]:.1f}%  —  {s}", color)
            diff = h_rows[0][1] - h_rows[1][1]
            if diff > 0:
                msg, c = f"↑ Crescut cu {diff:.1f}% fata de ultima masurare", RED
            elif diff < 0:
                msg, c = f"↓ Imbunatatit cu {abs(diff):.1f}% fata de ultima masurare", GREEN
            else:
                msg, c = "→ Nicio schimbare", TEXT_DIM
            tk.Label(card, text=msg, font=FONT_BOLD, fg=c, bg=BG3).pack(anchor="w", pady=(8,0))

        self._card(parent, "🧪  Trend HbA1c", hba1c_content)

        # ── Greutate trend ──
        def weight_content(card):
            if len(w_rows) < 2:
                tk.Label(card, text="Minim 2 inregistrari necesare.", font=FONT, fg=TEXT_DIM, bg=BG3).pack(anchor="w")
                if w_rows:
                    self._row(card, w_rows[0][0], f"{w_rows[0][1]:.1f} kg")
                return
            for r in w_rows:
                self._row(card, r[0], f"{r[1]:.1f} kg")
            diff = w_rows[0][1] - w_rows[1][1]
            if diff > 0:
                msg, c = f"↑ Crescut cu {diff:.1f} kg", YELLOW
            elif diff < 0:
                msg, c = f"↓ Scazut cu {abs(diff):.1f} kg", GREEN
            else:
                msg, c = "→ Nicio schimbare", TEXT_DIM
            tk.Label(card, text=msg, font=FONT_BOLD, fg=c, bg=BG3).pack(anchor="w", pady=(8,0))

        self._card(parent, "⚖️  Trend Greutate", weight_content)

        # ── Corelatie ──
        def corr_content(card):
            if len(m_rows) < 5:
                tk.Label(card, text="Minim 5 masuratori necesare.", font=FONT, fg=TEXT_DIM, bg=BG3).pack(anchor="w")
                return
            glucoses = [r[0] for r in m_rows]
            carbs    = [r[3] for r in m_rows]
            steps    = [r[2] for r in m_rows]
            waters   = [r[1] for r in m_rows]

            def pearson(x, y):
                n = len(x); mx, my = sum(x)/n, sum(y)/n
                num = sum((xi-mx)*(yi-my) for xi,yi in zip(x,y))
                den = (sum((xi-mx)**2 for xi in x) * sum((yi-my)**2 for yi in y))**0.5
                return num/den if den else 0

            def interp(r):
                if r > 0.6:  return "Corelatie puternica pozitiva ↑", RED
                if r > 0.3:  return "Corelatie moderata pozitiva", YELLOW
                if r > 0:    return "Corelatie slaba pozitiva", TEXT
                if r > -0.3: return "Corelatie slaba negativa", TEXT
                if r > -0.6: return "Corelatie moderata negativa", GREEN
                return "Corelatie puternica negativa ↓", GREEN

            for label, vals in [("Glucoza ↔ Carbs", carbs), ("Glucoza ↔ Pasi", steps), ("Glucoza ↔ Apa", waters)]:
                r = pearson(glucoses, vals)
                msg, color = interp(r)
                self._row(card, f"{label}  (r={r:+.2f})", msg, color)

        self._card(parent, "🔗  Corelatie", corr_content)

# ─────────────────────────────────────────
# PAGINA EXPORT
# ─────────────────────────────────────────

class ExportPage:
    def __init__(self, parent, user_id):
        self.parent  = parent
        self.user_id = user_id
        self._build()

    def _build(self):
        pad = tk.Frame(self.parent, bg=BG2, padx=30, pady=20)
        pad.pack(fill="both", expand=True)
        section_label(pad, "📄  Export Date").pack(fill="x")

        info = tk.Frame(pad, bg=BG3, padx=20, pady=15)
        info.pack(fill="x", pady=(0,20))
        tk.Label(info, text="Exporta datele tale in format CSV.\nFisierele vor fi salvate in folderul curent.",
                 font=FONT, fg=TEXT, bg=BG3, justify="left").pack(anchor="w")

        for label, key in [
            ("📋  Export Masuratori", "measurements"),
            ("🧪  Export HbA1c", "hba1c"),
            ("⚖️   Export Greutate", "weight"),
            ("📦  Export TOT", "all"),
        ]:
            styled_button(pad, label, lambda k=key: self._export(k)).pack(fill="x", pady=4)

        self.log = tk.Text(pad, bg=BG3, fg=GREEN, font=FONT,
                           height=8, relief="flat", state="disabled")
        self.log.pack(fill="x", pady=(15,0))

    def _log(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _export(self, which):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        tables = {
            "measurements": ("measurements", ["Data","Glucoza","Apa","Pasi","Carbs"],
                             "SELECT date,fasting_glucose,water_glasses,steps,carbs FROM measurements WHERE user_id=? ORDER BY date"),
            "hba1c": ("hba1c", ["Data","HbA1c (%)"],
                      "SELECT date,value FROM hba1c WHERE user_id=? ORDER BY date"),
            "weight": ("weight", ["Data","Greutate (kg)"],
                       "SELECT date,kg FROM weight WHERE user_id=? ORDER BY date"),
        }
        keys = list(tables.keys()) if which == "all" else [which]
        for k in keys:
            name, headers, query = tables[k]
            with get_conn() as conn:
                rows = conn.cursor().execute(query, (self.user_id,)).fetchall()
            if not rows:
                self._log(f"⚠  {name}: fara date.")
                continue
            fname = f"export_{name}_{ts}.csv"
            with open(fname, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            self._log(f"✅  Salvat: {fname}  ({len(rows)} randuri)")

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

if __name__ == "__main__":
    create_tables()
    auth = AuthWindow()
    if auth.user_id:
        App(auth.user_id, auth.username)
