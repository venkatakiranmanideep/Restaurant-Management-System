import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection, get_dashboard_stats
from modules.bookings import BookingsWindow
from modules.customers import CustomersWindow
from modules.menu import MenuWindow
from modules.reviews import ReviewsWindow
from modules.billing import BillingWindow
from modules.reports import ReportsWindow
from modules.tables import TablesWindow
from modules.settings import SettingsWindow


class DashboardWindow(tk.Frame):
    def __init__(self, parent, db_path, user):
        super().__init__(parent, bg="#FFF8F0")
        self.parent = parent
        self.db_path = db_path
        self.user = user
        self.dark_mode = False
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.build_ui()
        self.load_dashboard()

    def build_ui(self):
        self.parent.title("Hotel TAJ Management")
        self.parent.geometry("1400x900")
        self.configure(bg="#FFF8F0")

        self.sidebar = tk.Frame(self, width=240, bg="#7B4B3A")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="Hotel TAJ", font=("Segoe UI", 22, "bold"), fg="#FFF8F0", bg="#7B4B3A").pack(pady=(24, 4))
        tk.Label(self.sidebar, text="Fine Dining", font=("Segoe UI", 12), fg="#F8E2D5", bg="#7B4B3A").pack(pady=(0, 24))

        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Bookings", self.show_bookings),
            ("Customers", self.show_customers),
            ("Tables", self.show_tables),
            ("Menu", self.show_menu),
            ("Billing", self.show_billing),
            ("Reviews", self.show_reviews),
            ("Reports", self.show_reports),
            ("Settings", self.show_settings),
        ]
        for label, cmd in nav_items:
            ttk.Button(self.sidebar, text=label, command=cmd).pack(fill="x", padx=16, pady=4)
        ttk.Button(self.sidebar, text="Logout", command=self.handle_logout).pack(side="bottom", padx=16, pady=16)

        self.content = tk.Frame(self, bg="#FFF8F0")
        self.content.pack(side="right", fill="both", expand=True)

        self.header = tk.Frame(self.content, bg="#FFF8F0")
        self.header.pack(fill="x", padx=24, pady=(24, 14))
        self.header.columnconfigure(1, weight=1)
        tk.Label(self.header, text="Restaurant Operations Dashboard", font=("Segoe UI", 20, "bold"), fg="#4E342E", bg="#FFF8F0").grid(row=0, column=0, sticky="w")
        tk.Label(self.header, text=f"Signed in as {self.user['full_name'] or self.user['username']}", font=("Segoe UI", 10), fg="#7D7D7D", bg="#FFF8F0").grid(row=1, column=0, sticky="w")
        self.search_var = tk.StringVar()
        ttk.Entry(self.header, textvariable=self.search_var, width=32).grid(row=0, column=1, sticky="e", padx=(20, 8))
        ttk.Button(self.header, text="Global Search", command=self.perform_search).grid(row=0, column=2, sticky="e")
        ttk.Button(self.header, text="Dark Mode", command=self.toggle_theme).grid(row=1, column=2, sticky="e", pady=(6, 0))

        self.main_frame = tk.Frame(self.content, bg="#FFF8F0")
        self.main_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    def clear_content(self):
        for child in self.main_frame.winfo_children():
            child.destroy()

    def show_dashboard(self):
        self.clear_content()
        self.load_dashboard()

    def show_bookings(self):
        self.clear_content()
        BookingsWindow(self.main_frame, self.db_path)

    def show_customers(self):
        self.clear_content()
        CustomersWindow(self.main_frame, self.db_path)

    def show_tables(self):
        self.clear_content()
        TablesWindow(self.main_frame, self.db_path)

    def show_menu(self):
        self.clear_content()
        MenuWindow(self.main_frame, self.db_path)

    def show_reviews(self):
        self.clear_content()
        ReviewsWindow(self.main_frame, self.db_path)

    def show_reports(self):
        self.clear_content()
        ReportsWindow(self.main_frame, self.db_path)

    def show_billing(self):
        self.clear_content()
        BillingWindow(self.main_frame, self.db_path)

    def show_settings(self):
        self.clear_content()
        SettingsWindow(self.main_frame, self.db_path)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        bg = "#1F1A24" if self.dark_mode else "#FFF8F0"
        fg = "#F9EEDC" if self.dark_mode else "#4E342E"
        self.configure(bg=bg)
        self.sidebar.configure(bg="#4B3A34")
        self.content.configure(bg=bg)
        self.header.configure(bg=bg)
        self.main_frame.configure(bg=bg)
        self.apply_theme(self, bg, fg)

    def apply_theme(self, widget, bg, fg):
        for child in widget.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=bg, fg=fg)
            elif isinstance(child, tk.Frame):
                child.configure(bg=bg)
                self.apply_theme(child, bg, fg)
            elif isinstance(child, tk.Text):
                child.configure(bg="#FFFFFF" if not self.dark_mode else "#2C2733", fg=fg)
            elif isinstance(child, ttk.Treeview):
                child.configure(style="Treeview")
            self.apply_theme(child, bg, fg)

    def load_dashboard(self):
        self.clear_content()
        stats = get_dashboard_stats(get_connection(self.db_path))
        cards = [
            ("Total Bookings", stats["total_bookings"], "#EADCF8"),
            ("Available Tables", stats["available_tables"], "#D8F3DC"),
            ("Today's Reservations", stats["todays_reservations"], "#FFD8BE"),
            ("Revenue", f"₹{stats['revenue']:.2f}", "#FFF8F0"),
        ]
        card_frame = tk.Frame(self.main_frame, bg="#FFF8F0")
        card_frame.pack(fill="x")
        for title, value, color in cards:
            card = tk.Frame(card_frame, bg=color, bd=0, highlightthickness=0)
            card.pack(side="left", fill="both", expand=True, padx=8, pady=8)
            tk.Label(card, text=title, font=("Segoe UI", 11, "bold"), bg=color, fg="#4E342E").pack(anchor="w", padx=16, pady=(16, 4))
            tk.Label(card, text=str(value), font=("Segoe UI", 20, "bold"), bg=color, fg="#7B4B3A").pack(anchor="w", padx=16, pady=(0, 16))

        recent = tk.Frame(self.main_frame, bg="#FFFFFF")
        recent.pack(fill="both", expand=True, pady=(10, 0))
        tk.Label(recent, text="Recent Bookings", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#4E342E").pack(anchor="w", padx=16, pady=(16, 8))
        tree = ttk.Treeview(recent, columns=("Customer", "Date", "Time", "Guests", "Status"), show="headings", height=8)
        tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        for header, text in (("Customer", "Customer"), ("Date", "Date"), ("Time", "Time"), ("Guests", "Guests"), ("Status", "Status")):
            tree.heading(header, text=text)
        for row in stats["recent_bookings"]:
            tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))

    def perform_search(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Search", "Enter a term to search.")
            return
        conn = get_connection(self.db_path)
        results = []
        results.extend([f"Customer: {row[0]}" for row in conn.execute("SELECT full_name FROM Customers WHERE full_name LIKE ?", (f"%{query}%",)).fetchall()])
        results.extend([f"Table: {row[0]}" for row in conn.execute("SELECT name FROM Tables WHERE name LIKE ?", (f"%{query}%",)).fetchall()])
        results.extend([f"Booking: {row[0]} for {row[1]}" for row in conn.execute("SELECT customer_name, booking_date FROM Bookings WHERE customer_name LIKE ? OR booking_date LIKE ?", (f"%{query}%", f"%{query}%")).fetchall()])
        results.extend([f"Menu: {row[0]}" for row in conn.execute("SELECT name FROM MenuItems WHERE name LIKE ?", (f"%{query}%",)).fetchall()])
        conn.close()
        self.clear_content()
        panel = tk.Frame(self.main_frame, bg="#FFFFFF")
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Global Search Results", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#4E342E").pack(anchor="w", padx=16, pady=(16, 8))
        text = tk.Text(panel, height=16, bg="#FFF8F0", fg="#4E342E")
        text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        if results:
            text.insert(tk.END, "\n".join(results))
        else:
            text.insert(tk.END, "No matching records found.")

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Do you want to log out?"):
            from modules.login import LoginWindow
            LoginWindow(self.parent, self.db_path)
            self.destroy()
