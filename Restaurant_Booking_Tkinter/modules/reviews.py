import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection


class ReviewsWindow(tk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent, bg="#FFF8F0")
        self.db_path = db_path
        self.pack(fill="both", expand=True)
        self.build_ui()
        self.load_reviews()

    def build_ui(self):
        header = tk.Frame(self, bg="#FFF8F0")
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text="Guest Reviews", font=("Segoe UI", 16, "bold"), bg="#FFF8F0", fg="#4E342E").pack(anchor="w")
        tk.Label(header, text="Capture guest feedback and service ratings", font=("Segoe UI", 10), bg="#FFF8F0", fg="#7D7D7D").pack(anchor="w")

        form = tk.LabelFrame(self, text="New Review", bg="#FFFFFF", fg="#7B4B3A", padx=14, pady=14)
        form.pack(fill="x", pady=(0, 12))
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Customer Name", bg="#FFFFFF", fg="#4E342E").grid(row=0, column=0, sticky="w", pady=4)
        self.customer_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.customer_var).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Rating", bg="#FFFFFF", fg="#4E342E").grid(row=1, column=0, sticky="w", pady=4)
        self.rating_var = tk.StringVar(value="5")
        ttk.Spinbox(form, from_=1, to=5, textvariable=self.rating_var, width=10).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=4)

        tk.Label(form, text="Comment", bg="#FFFFFF", fg="#4E342E").grid(row=2, column=0, sticky="w", pady=4)
        self.comment_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.comment_var).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Button(form, text="Submit Review", command=self.save_review).grid(row=3, column=1, sticky="e", pady=(12, 0))

        self.list_frame = tk.Frame(self, bg="#FFFFFF")
        self.list_frame.pack(fill="both", expand=True)
        tk.Label(self.list_frame, text="Review Feed", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#4E342E").pack(anchor="w", padx=16, pady=(16, 8))

        self.tree = ttk.Treeview(self.list_frame, columns=("id", "Customer", "Rating", "Comment"), show="headings", height=10)
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.tree.heading("id", text="ID")
        self.tree.heading("Customer", text="Customer")
        self.tree.heading("Rating", text="Rating")
        self.tree.heading("Comment", text="Comment")

    def load_reviews(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT id, customer_name, rating, comment FROM Reviews ORDER BY id DESC").fetchall()
        conn.close()
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3]))

    def save_review(self):
        if not self.customer_var.get().strip():
            messagebox.showerror("Validation", "Customer name is required.")
            return
        conn = get_connection(self.db_path)
        conn.execute(
            "INSERT INTO Reviews (customer_name, rating, comment) VALUES (?, ?, ?)",
            (self.customer_var.get().strip(), int(self.rating_var.get()), self.comment_var.get().strip()),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Review submitted.")
        self.load_reviews()
