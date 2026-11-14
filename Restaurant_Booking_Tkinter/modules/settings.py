import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection


class SettingsWindow(tk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent, bg="#FFF8F0")
        self.db_path = db_path
        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self, bg="#FFF8F0")
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text="Restaurant Settings", font=("Segoe UI", 16, "bold"), bg="#FFF8F0", fg="#4E342E").pack(anchor="w")
        tk.Label(header, text="Manage profile, business details and preferences", font=("Segoe UI", 10), bg="#FFF8F0", fg="#7D7D7D").pack(anchor="w")

        form = tk.LabelFrame(self, text="Restaurant Information", bg="#FFFFFF", fg="#7B4B3A", padx=14, pady=14)
        form.pack(fill="x", pady=(0, 12))
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Restaurant Name", bg="#FFFFFF", fg="#4E342E").grid(row=0, column=0, sticky="w", pady=4)
        self.name_var = tk.StringVar(value="Hotel TAJ")
        ttk.Entry(form, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Opening Hours", bg="#FFFFFF", fg="#4E342E").grid(row=1, column=0, sticky="w", pady=4)
        self.hours_var = tk.StringVar(value="Mon-Sun: 11:00 AM - 11:00 PM")
        ttk.Entry(form, textvariable=self.hours_var).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Contact", bg="#FFFFFF", fg="#4E342E").grid(row=2, column=0, sticky="w", pady=4)
        self.contact_var = tk.StringVar(value="+91 98765 43210")
        ttk.Entry(form, textvariable=self.contact_var).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Button(form, text="Save Settings", command=self.save_settings).grid(row=3, column=1, sticky="e", pady=(12, 0))

    def save_settings(self):
        messagebox.showinfo("Settings", "Restaurant settings saved successfully.")
