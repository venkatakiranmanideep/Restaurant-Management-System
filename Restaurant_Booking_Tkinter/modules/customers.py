import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection


class CustomersWindow(tk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent, bg="#FFF8F0")
        self.db_path = db_path
        self.pack(fill="both", expand=True)
        self.build_ui()
        self.load_customers()

    def build_ui(self):
        header = tk.Frame(self, bg="#FFF8F0")
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text="Customer Management", font=("Segoe UI", 16, "bold"), bg="#FFF8F0", fg="#4E342E").pack(anchor="w")
        tk.Label(header, text="Maintain guest profiles and contact details", font=("Segoe UI", 10), bg="#FFF8F0", fg="#7D7D7D").pack(anchor="w")

        form = tk.LabelFrame(self, text="Customer Profile", bg="#FFFFFF", fg="#7B4B3A", padx=14, pady=14)
        form.pack(fill="x", pady=(0, 12))
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Full Name", bg="#FFFFFF", fg="#4E342E").grid(row=0, column=0, sticky="w", pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Email", bg="#FFFFFF", fg="#4E342E").grid(row=1, column=0, sticky="w", pady=4)
        self.email_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.email_var).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Phone", bg="#FFFFFF", fg="#4E342E").grid(row=2, column=0, sticky="w", pady=4)
        self.phone_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.phone_var).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Notes", bg="#FFFFFF", fg="#4E342E").grid(row=3, column=0, sticky="w", pady=4)
        self.notes_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.notes_var).grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Button(form, text="Save Customer", command=self.save_customer).grid(row=4, column=1, sticky="e", pady=(12, 0))

        self.list_frame = tk.Frame(self, bg="#FFFFFF")
        self.list_frame.pack(fill="both", expand=True)
        tk.Label(self.list_frame, text="Customer Directory", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#4E342E").pack(anchor="w", padx=16, pady=(16, 8))

        self.tree = ttk.Treeview(self.list_frame, columns=("id", "Name", "Email", "Phone", "Notes"), show="headings", height=10)
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.tree.heading("id", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Notes", text="Notes")

    def load_customers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT id, full_name, email, phone, notes FROM Customers ORDER BY id DESC").fetchall()
        conn.close()
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))

    def save_customer(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Validation", "Customer name is required.")
            return
        conn = get_connection(self.db_path)
        conn.execute(
            "INSERT INTO Customers (full_name, email, phone, notes) VALUES (?, ?, ?, ?)",
            (name, self.email_var.get().strip(), self.phone_var.get().strip(), self.notes_var.get().strip()),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer saved.")
        self.load_customers()
