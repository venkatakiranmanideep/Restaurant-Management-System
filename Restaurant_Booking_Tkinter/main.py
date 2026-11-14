import os
import tkinter as tk
from tkinter import ttk

from database import initialize_database
from modules.login import LoginWindow


class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Restaurant Booking System")
        self.geometry("720x420")
        self.configure(bg="#FFF8F0")
        self.overrideredirect(True)
        self.center_window()
        tk.Label(
            self,
            text="Hotel TAJ",
            font=("Segoe UI", 26, "bold"),
            fg="#7B4B3A",
            bg="#FFF8F0",
        ).pack(expand=True)
        tk.Label(
            self,
            text="Preparing elegant dining management experience...",
            font=("Segoe UI", 11),
            fg="#6D4C41",
            bg="#FFF8F0",
        ).pack(pady=(0, 20))
        self.update_idletasks()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hotel TAJ Management")
        self.geometry("1400x900")
        self.minsize(1100, 780)
        self.configure(bg="#FFF8F0")
        self.configure_styles()
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(default=icon_path)
        self.db_path = initialize_database()
        self.withdraw()
        self.splash = SplashScreen(self)
        self.after(1800, self.show_login)

    def configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#FFF8F0")
        style.configure("TLabel", background="#FFF8F0", foreground="#4E342E")
        style.configure("TButton", padding=8, relief="flat")
        style.map(
            "TButton",
            background=[("active", "#FFD8BE"), ("!disabled", "#EADCF8")],
            foreground=[("!disabled", "#4E342E")],
        )
        style.configure("Accent.TButton", background="#D8F3DC", foreground="#4E342E")
        style.configure("Card.TFrame", background="#FFFFFF")

    def show_login(self):
        self.splash.destroy()
        self.deiconify()
        LoginWindow(self, self.db_path)


if __name__ == "__main__":
    app = App()
    app.mainloop()
