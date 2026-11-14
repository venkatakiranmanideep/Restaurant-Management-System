import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from database import get_connection


class MenuWindow(tk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent, bg="#FFF8F0")
        self.db_path = db_path
        self.pack(fill="both", expand=True)
        self.build_ui()
        self.load_menu()

    def build_ui(self):
        header = tk.Frame(self, bg="#FFF8F0")
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text="Menu Management", font=("Segoe UI", 16, "bold"), bg="#FFF8F0", fg="#4E342E").pack(anchor="w")
        tk.Label(header, text="Curate dishes with pricing and availability", font=("Segoe UI", 10), bg="#FFF8F0", fg="#7D7D7D").pack(anchor="w")

        form = tk.LabelFrame(self, text="Dish Details", bg="#FFFFFF", fg="#7B4B3A", padx=14, pady=14)
        form.pack(fill="x", pady=(0, 12))
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Category", bg="#FFFFFF", fg="#4E342E").grid(row=0, column=0, sticky="w", pady=4)
        self.category_var = tk.StringVar(value="Starters")
        ttk.Combobox(form, textvariable=self.category_var, values=["Starters", "Main Course", "Desserts", "Drinks"], state="readonly").grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Name", bg="#FFFFFF", fg="#4E342E").grid(row=1, column=0, sticky="w", pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Price", bg="#FFFFFF", fg="#4E342E").grid(row=2, column=0, sticky="w", pady=4)
        self.price_var = tk.StringVar(value="0.00")
        ttk.Entry(form, textvariable=self.price_var).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Description", bg="#FFFFFF", fg="#4E342E").grid(row=3, column=0, sticky="w", pady=4)
        self.description_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.description_var).grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Availability", bg="#FFFFFF", fg="#4E342E").grid(row=4, column=0, sticky="w", pady=4)
        self.availability_var = tk.StringVar(value="Available")
        ttk.Combobox(form, textvariable=self.availability_var, values=["Available", "Out of Stock"], state="readonly").grid(row=4, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Button(form, text="Choose Image", command=self.choose_image).grid(row=5, column=0, sticky="w", pady=(12, 0))
        self.image_path = None
        ttk.Button(form, text="Save Item", command=self.save_item).grid(row=5, column=1, sticky="e", pady=(12, 0))

        self.list_frame = tk.Frame(self, bg="#FFFFFF")
        self.list_frame.pack(fill="both", expand=True)
        tk.Label(self.list_frame, text="Menu Items", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#4E342E").pack(anchor="w", padx=16, pady=(16, 8))

        self.tree = ttk.Treeview(self.list_frame, columns=("id", "Category", "Name", "Price", "Availability"), show="headings", height=10)
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.tree.heading("id", text="ID")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Availability", text="Availability")

    def choose_image(self):
        path = filedialog.askopenfilename(title="Select Menu Image", filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if path:
            self.image_path = path
            messagebox.showinfo("Image Selected", os.path.basename(path))

    def load_menu(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = get_connection(self.db_path)
        rows = conn.execute(
            "SELECT m.id, c.name AS category_name, m.name, m.price, m.availability FROM MenuItems m JOIN MenuCategories c ON c.id = m.category_id ORDER BY m.id DESC"
        ).fetchall()
        conn.close()
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], f"₹{row[3]:.2f}", row[4]))

    def save_item(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Validation", "Dish name is required.")
            return
        conn = get_connection(self.db_path)
        category = conn.execute("SELECT id FROM MenuCategories WHERE name = ?", (self.category_var.get(),)).fetchone()
        if not category:
            conn.execute("INSERT INTO MenuCategories (name, description) VALUES (?, ?)", (self.category_var.get(), "Custom category"))
            category = conn.execute("SELECT id FROM MenuCategories WHERE name = ?", (self.category_var.get(),)).fetchone()
        conn.execute(
            "INSERT INTO MenuItems (category_id, name, price, description, availability, image_path) VALUES (?, ?, ?, ?, ?, ?)",
            (category[0], name, float(self.price_var.get()), self.description_var.get().strip(), self.availability_var.get(), self.image_path),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Menu item saved.")
        self.load_menu()
