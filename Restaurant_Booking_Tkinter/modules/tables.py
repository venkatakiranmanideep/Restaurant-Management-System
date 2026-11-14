import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection


class TablesWindow(tk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent, bg="#FFF8F0")
        self.db_path = db_path
        self.pack(fill="both", expand=True)
        self.build_ui()
        self.load_tables()

    def build_ui(self):
        header = tk.Frame(self, bg="#FFF8F0")
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text="Table Management", font=("Segoe UI", 16, "bold"), bg="#FFF8F0", fg="#4E342E").pack(anchor="w")
        tk.Label(header, text="Manage capacity, location, and availability", font=("Segoe UI", 10), bg="#FFF8F0", fg="#7D7D7D").pack(anchor="w")

        form = tk.LabelFrame(self, text="Table Details", bg="#FFFFFF", fg="#7B4B3A", padx=14, pady=14)
        form.pack(fill="x", pady=(0, 12))
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Table Name", bg="#FFFFFF", fg="#4E342E").grid(row=0, column=0, sticky="w", pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Capacity", bg="#FFFFFF", fg="#4E342E").grid(row=1, column=0, sticky="w", pady=4)
        self.capacity_var = tk.StringVar(value="2")
        ttk.Spinbox(form, from_=1, to=12, textvariable=self.capacity_var, width=10).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=4)

        tk.Label(form, text="Status", bg="#FFFFFF", fg="#4E342E").grid(row=2, column=0, sticky="w", pady=4)
        self.status_var = tk.StringVar(value="Available")
        ttk.Combobox(form, textvariable=self.status_var, values=["Available", "Reserved", "Maintenance"], state="readonly").grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Location", bg="#FFFFFF", fg="#4E342E").grid(row=3, column=0, sticky="w", pady=4)
        self.location_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.location_var).grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Button(form, text="Save Table", command=self.save_table).grid(row=4, column=1, sticky="e", pady=(12, 0))

        self.list_frame = tk.Frame(self, bg="#FFFFFF")
        self.list_frame.pack(fill="both", expand=True)
        tk.Label(self.list_frame, text="Dining Tables", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#4E342E").pack(anchor="w", padx=16, pady=(16, 8))

        self.tree = ttk.Treeview(self.list_frame, columns=("id", "Name", "Capacity", "Status", "Location"), show="headings", height=10)
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.tree.heading("id", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Capacity", text="Capacity")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Location", text="Location")

    def load_tables(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT id, name, capacity, status, location FROM Tables ORDER BY id DESC").fetchall()
        conn.close()
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))

    def save_table(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Validation", "Table name is required.")
            return
        conn = get_connection(self.db_path)
        conn.execute(
            "INSERT INTO Tables (name, capacity, status, location) VALUES (?, ?, ?, ?)",
            (name, int(self.capacity_var.get()), self.status_var.get(), self.location_var.get().strip()),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Table saved.")
        self.load_tables()
