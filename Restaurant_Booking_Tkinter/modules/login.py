import tkinter as tk
from tkinter import messagebox, ttk

from database import authenticate_user, get_connection


class LoginWindow(tk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent, bg="#FFF8F0")
        self.parent = parent
        self.db_path = db_path
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.build_ui()

    def build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        left = tk.Frame(self, bg="#FFF8F0")
        left.grid(row=0, column=0, rowspan=2, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        title = tk.Label(
            left,
            text="Hotel TAJ",
            font=("Segoe UI", 28, "bold"),
            fg="#7B4B3A",
            bg="#FFF8F0",
        )
        title.place(relx=0.5, rely=0.4, anchor="center")

        sub = tk.Label(
            left,
            text="Professional restaurant table booking and operations suite",
            font=("Segoe UI", 12),
            fg="#8D6E63",
            bg="#FFF8F0",
            wraplength=320,
        )
        sub.place(relx=0.5, rely=0.54, anchor="center")

        form = tk.Frame(self, bg="#FFFFFF", bd=0)
        form.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=60, pady=60)
        form.columnconfigure(0, weight=1)

        heading = tk.Label(form, text="Secure Staff Login", font=("Segoe UI", 22, "bold"), bg="#FFFFFF", fg="#4E342E")
        heading.grid(row=0, column=0, sticky="w", pady=(20, 8))

        subtitle = tk.Label(form, text="Access reservations, tables, menu and reports", font=("Segoe UI", 11), bg="#FFFFFF", fg="#7D7D7D")
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 24))

        tk.Label(form, text="Username", bg="#FFFFFF", fg="#4E342E").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(form, textvariable=self.username_var, width=38)
        self.username_entry.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        tk.Label(form, text="Password", bg="#FFFFFF", fg="#4E342E").grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form, textvariable=self.password_var, show="•", width=38)
        self.password_entry.grid(row=5, column=0, sticky="ew", pady=(0, 16))

        self.login_button = ttk.Button(form, text="Login", command=self.handle_login)
        self.login_button.grid(row=6, column=0, sticky="ew", pady=(0, 8))

        ttk.Button(form, text="Register", command=self.handle_register).grid(row=7, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(form, text="Forgot Password", command=self.handle_forgot).grid(row=8, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(form, text="Change Password", command=self.handle_change_password).grid(row=9, column=0, sticky="ew")

    def handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showerror("Validation", "Please enter both username and password.")
            return

        conn = get_connection(self.db_path)
        user = authenticate_user(conn, username, password)
        conn.close()
        if user:
            messagebox.showinfo("Welcome", f"Welcome back, {user['full_name'] or user['username']}")
            from modules.dashboard import DashboardWindow
            DashboardWindow(self.parent, self.db_path, user)
            self.destroy()
        else:
            messagebox.showerror("Access denied", "Invalid username or password.")

    def handle_register(self):
        dialog = tk.Toplevel(self)
        dialog.title("Register New User")
        dialog.geometry("360x260")
        dialog.transient(self.parent)
        dialog.grab_set()

        tk.Label(dialog, text="Username").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var).grid(row=0, column=1, padx=12, pady=(12, 4))

        tk.Label(dialog, text="Email").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        email_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=email_var).grid(row=1, column=1, padx=12, pady=4)

        tk.Label(dialog, text="Password").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        password_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=password_var, show="•").grid(row=2, column=1, padx=12, pady=4)

        tk.Label(dialog, text="Full Name").grid(row=3, column=0, sticky="w", padx=12, pady=4)
        full_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=full_name_var).grid(row=3, column=1, padx=12, pady=4)

        def submit():
            username = username_var.get().strip()
            email = email_var.get().strip()
            password = password_var.get().strip()
            full_name = full_name_var.get().strip()
            if not all([username, email, password, full_name]):
                messagebox.showerror("Validation", "All fields are required.")
                return
            conn = get_connection(self.db_path)
            if conn.execute("SELECT 1 FROM Users WHERE username = ? OR email = ?", (username, email)).fetchone():
                messagebox.showerror("Duplicate", "That username or email already exists.")
                conn.close()
                return
            conn.execute(
                "INSERT INTO Users (username, email, password, full_name, role) VALUES (?, ?, ?, ?, ?)",
                (username, email, password, full_name, "Staff"),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "User registered successfully.")
            dialog.destroy()

        ttk.Button(dialog, text="Create Account", command=submit).grid(row=4, column=1, sticky="e", padx=12, pady=(16, 0))

    def handle_forgot(self):
        dialog = tk.Toplevel(self)
        dialog.title("Reset Password")
        dialog.geometry("340x220")
        dialog.transient(self.parent)
        dialog.grab_set()

        tk.Label(dialog, text="Username").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var).grid(row=0, column=1, padx=12, pady=(12, 4))

        tk.Label(dialog, text="New Password").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        password_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=password_var, show="•").grid(row=1, column=1, padx=12, pady=4)

        def submit():
            username = username_var.get().strip()
            password = password_var.get().strip()
            if not username or not password:
                messagebox.showerror("Validation", "Username and password are required.")
                return
            conn = get_connection(self.db_path)
            user = conn.execute("SELECT id FROM Users WHERE username = ?", (username,)).fetchone()
            if not user:
                messagebox.showerror("Not Found", "No user found for that username.")
                conn.close()
                return
            conn.execute("UPDATE Users SET password = ? WHERE username = ?", (password, username))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Password updated successfully.")
            dialog.destroy()

        ttk.Button(dialog, text="Reset Password", command=submit).grid(row=2, column=1, sticky="e", padx=12, pady=(16, 0))

    def handle_change_password(self):
        dialog = tk.Toplevel(self)
        dialog.title("Change Password")
        dialog.geometry("360x240")
        dialog.transient(self.parent)
        dialog.grab_set()

        tk.Label(dialog, text="Username").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var).grid(row=0, column=1, padx=12, pady=(12, 4))

        tk.Label(dialog, text="Current Password").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        current_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=current_var, show="•").grid(row=1, column=1, padx=12, pady=4)

        tk.Label(dialog, text="New Password").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        new_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=new_var, show="•").grid(row=2, column=1, padx=12, pady=4)

        def submit():
            username = username_var.get().strip()
            current = current_var.get().strip()
            new_password = new_var.get().strip()
            if not all([username, current, new_password]):
                messagebox.showerror("Validation", "All fields are required.")
                return
            conn = get_connection(self.db_path)
            user = conn.execute("SELECT id FROM Users WHERE username = ? AND password = ?", (username, current)).fetchone()
            if not user:
                messagebox.showerror("Invalid", "Current credentials do not match.")
                conn.close()
                return
            conn.execute("UPDATE Users SET password = ? WHERE username = ?", (new_password, username))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Password changed successfully.")
            dialog.destroy()

        ttk.Button(dialog, text="Update Password", command=submit).grid(row=3, column=1, sticky="e", padx=12, pady=(16, 0))
