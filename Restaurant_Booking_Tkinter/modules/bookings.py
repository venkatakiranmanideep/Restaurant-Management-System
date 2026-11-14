import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from tkcalendar import Calendar

from database import get_connection, validate_booking_slot


class BookingsWindow(tk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent, bg="#FFF8F0")
        self.parent = parent
        self.db_path = db_path
        self.selected_booking_id = None
        self.pack(fill="both", expand=True)
        self.build_ui()
        self.load_bookings()

    def build_ui(self):
        self.configure(bg="#FFF8F0")
        header = tk.Frame(self, bg="#FFF8F0")
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text="Booking Management", font=("Segoe UI", 16, "bold"), bg="#FFF8F0", fg="#4E342E").pack(anchor="w")
        tk.Label(header, text="Create, edit, and review table reservations", font=("Segoe UI", 10), bg="#FFF8F0", fg="#7D7D7D").pack(anchor="w")

        form = tk.LabelFrame(self, text="New Reservation", bg="#FFFFFF", fg="#7B4B3A", padx=14, pady=14)
        form.pack(fill="x", pady=(0, 12))
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Customer", bg="#FFFFFF", fg="#4E342E").grid(row=0, column=0, sticky="w", pady=4)
        self.customer_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.customer_var).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Table", bg="#FFFFFF", fg="#4E342E").grid(row=1, column=0, sticky="w", pady=4)
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(form, textvariable=self.table_var, state="readonly", width=30)
        self.table_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Date", bg="#FFFFFF", fg="#4E342E").grid(row=2, column=0, sticky="w", pady=4)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(form, textvariable=self.date_var).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)
        ttk.Button(form, text="Pick", command=self.pick_date).grid(row=2, column=2, padx=(8, 0))

        tk.Label(form, text="Time", bg="#FFFFFF", fg="#4E342E").grid(row=3, column=0, sticky="w", pady=4)
        self.time_var = tk.StringVar(value="19:00")
        ttk.Combobox(form, textvariable=self.time_var, values=["18:00", "19:00", "20:00", "21:00"], state="readonly").grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Guests", bg="#FFFFFF", fg="#4E342E").grid(row=4, column=0, sticky="w", pady=4)
        self.guests_var = tk.StringVar(value="2")
        ttk.Spinbox(form, from_=1, to=10, textvariable=self.guests_var, width=10).grid(row=4, column=1, sticky="w", padx=(8, 0), pady=4)

        ttk.Button(form, text="Book Table", command=self.save_booking).grid(row=5, column=1, sticky="e", pady=(12, 0))

        self.list_frame = tk.Frame(self, bg="#FFFFFF")
        self.list_frame.pack(fill="both", expand=True)
        tk.Label(self.list_frame, text="Booking History", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#4E342E").pack(anchor="w", padx=16, pady=(16, 8))

        self.tree = ttk.Treeview(self.list_frame, columns=("id", "Customer", "Table", "Date", "Time", "Guests", "Status"), show="headings", height=10)
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        for name, text in (("id", "ID"), ("Customer", "Customer"), ("Table", "Table"), ("Date", "Date"), ("Time", "Time"), ("Guests", "Guests"), ("Status", "Status")):
            self.tree.heading(name, text=text)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        ttk.Button(self.list_frame, text="Print Receipt", command=self.print_receipt).pack(anchor="e", padx=16, pady=(0, 16))
        ttk.Button(self.list_frame, text="Cancel Selected", command=self.cancel_booking).pack(anchor="e", padx=16, pady=(0, 16))

        # Context menu for treeview (right-click)
        self.ctx_menu = tk.Menu(self, tearoff=0)
        self.ctx_menu.add_command(label="Cancel Booking", command=self.cancel_booking)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if selected:
            self.selected_booking_id = self.tree.item(selected[0], "values")[0]

    def pick_date(self):
        top = tk.Toplevel(self)
        top.title("Select Date")
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack()
        ttk.Button(top, text="Apply", command=lambda: self.set_date(cal, top)).pack(pady=8)

    def set_date(self, cal, top):
        self.date_var.set(cal.get_date())
        top.destroy()

    def load_bookings(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = get_connection(self.db_path)
        rows = conn.execute(
            "SELECT b.id, b.customer_name, t.name AS table_name, b.booking_date, b.booking_time, b.guests, b.status FROM Bookings b JOIN Tables t ON t.id = b.table_id ORDER BY b.id DESC"
        ).fetchall()
        conn.close()
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

        conn = get_connection(self.db_path)
        tables = conn.execute("SELECT id, name FROM Tables").fetchall()
        conn.close()
        values = [f"{table['id']} - {table['name']}" for table in tables]
        self.table_combo.configure(values=values)
        if values:
            self.table_var.set(values[0])

    def save_booking(self):
        customer_name = self.customer_var.get().strip()
        table_value = self.table_var.get().strip()
        booking_date = self.date_var.get().strip()
        booking_time = self.time_var.get().strip()
        guests = int(self.guests_var.get())

        if not customer_name or not table_value or not booking_date:
            messagebox.showerror("Validation", "Please fill in customer, table, and date.")
            return

        try:
            table_id = int(table_value.split(" - ")[0])
        except ValueError:
            messagebox.showerror("Validation", "Please select a valid table.")
            return

        if guests < 1 or guests > 10:
            messagebox.showerror("Validation", "Guest count must be between 1 and 10.")
            return

        conn = get_connection(self.db_path)
        if not validate_booking_slot(conn, table_id, booking_date, booking_time):
            messagebox.showerror("Conflict", "This table is already booked for the selected slot.")
            conn.close()
            return
        conn.execute(
            "INSERT INTO Bookings (customer_name, table_id, booking_date, booking_time, guests, status) VALUES (?, ?, ?, ?, ?, ?)",
            (customer_name, table_id, booking_date, booking_time, guests, "Confirmed"),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Booking created successfully.")
        self.load_bookings()

    def cancel_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a booking first.")
            return
        booking_id = self.tree.item(selected[0], "values")[0]
        # Confirm cancellation
        if not messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel the selected booking?"):
            return
        conn = get_connection(self.db_path)
        conn.execute("UPDATE Bookings SET status = 'Cancelled' WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()
        # store last cancelled for undo
        self._last_cancelled = {'id': booking_id, 'previous_status': 'Confirmed'}
        messagebox.showinfo("Updated", "Booking cancelled.")
        self.load_bookings()
        # show undo snackbar
        self.show_undo_snackbar()

    def show_undo_snackbar(self):
        try:
            if hasattr(self, '_undo_win') and self._undo_win.winfo_exists():
                self._undo_win.destroy()
        except Exception:
            pass
        self._undo_win = tk.Toplevel(self)
        self._undo_win.overrideredirect(True)
        self._undo_win.configure(bg="#333333")
        label = tk.Label(self._undo_win, text="Booking cancelled", fg="#FFFFFF", bg="#333333")
        label.pack(side="left", padx=8, pady=6)
        undo_btn = ttk.Button(self._undo_win, text="Undo", command=self.undo_last_cancellation)
        undo_btn.pack(side="right", padx=8, pady=6)
        # position at bottom-right of parent
        self._undo_win.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() - self._undo_win.winfo_width() - 24
        y = self.winfo_rooty() + self.winfo_height() - self._undo_win.winfo_height() - 24
        self._undo_win.geometry(f"+{x}+{y}")
        # auto-dismiss after 8 seconds
        self._undo_win.after(8000, lambda: self._undo_win.destroy() if self._undo_win.winfo_exists() else None)

    def undo_last_cancellation(self):
        if not getattr(self, '_last_cancelled', None):
            return
        booking_id = self._last_cancelled['id']
        conn = get_connection(self.db_path)
        conn.execute("UPDATE Bookings SET status = 'Confirmed' WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Undo", "Booking restored.")
        self.load_bookings()
        try:
            if hasattr(self, '_undo_win') and self._undo_win.winfo_exists():
                self._undo_win.destroy()
        except Exception:
            pass

    def show_context_menu(self, event):
        # select the row under cursor
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            try:
                self.ctx_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.ctx_menu.grab_release()

    def print_receipt(self):
        if self.selected_booking_id is None:
            messagebox.showwarning("Selection", "Select a booking first.")
            return
        conn = get_connection(self.db_path)
        booking = conn.execute(
            "SELECT b.id, b.customer_name, t.name, b.booking_date, b.booking_time, b.guests, b.status FROM Bookings b JOIN Tables t ON t.id = b.table_id WHERE b.id = ?",
            (self.selected_booking_id,),
        ).fetchone()
        conn.close()
        if not booking:
            messagebox.showwarning("Receipt", "Booking not found.")
            return
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "receipts")
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"receipt_{booking['id']}.pdf")
        doc = SimpleDocTemplate(path, pagesize=letter)
        elements = [Paragraph("Hotel TAJ Receipt", style="Title"), Spacer(1, 12)]
        elements.append(Paragraph(f"Customer: {booking['customer_name']}", style="BodyText"))
        elements.append(Paragraph(f"Table: {booking['name']}", style="BodyText"))
        elements.append(Paragraph(f"Date: {booking['booking_date']}", style="BodyText"))
        elements.append(Paragraph(f"Time: {booking['booking_time']}", style="BodyText"))
        elements.append(Paragraph(f"Guests: {booking['guests']}", style="BodyText"))
        elements.append(Paragraph(f"Status: {booking['status']}", style="BodyText"))
        doc.build(elements)
        messagebox.showinfo("Receipt", f"Receipt saved to {path}")
