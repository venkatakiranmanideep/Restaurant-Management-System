import os
import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table as RLTable
from reportlab.lib.styles import getSampleStyleSheet
from database import get_connection


class BillingWindow(tk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent, bg="#FFF8F0")
        self.db_path = db_path
        self.pack(fill="both", expand=True)
        self.order_items = []  # list of dicts: {id, name, qty, price}
        self.build_ui()
        self.load_bookings()
        self.load_menu_items()

    def build_ui(self):
        header = tk.Frame(self, bg="#FFF8F0")
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text="Billing", font=("Segoe UI", 16, "bold"), bg="#FFF8F0", fg="#4E342E").pack(anchor="w")
        tk.Label(header, text="Create and print bills for table bookings", font=("Segoe UI", 10), bg="#FFF8F0", fg="#7D7D7D").pack(anchor="w")

        form = tk.Frame(self, bg="#FFFFFF")
        form.pack(fill="x", padx=12, pady=(0, 12))
        tk.Label(form, text="Select Booking", bg="#FFFFFF", fg="#4E342E").grid(row=0, column=0, sticky="w", pady=6)
        self.booking_var = tk.StringVar()
        self.booking_combo = ttk.Combobox(form, textvariable=self.booking_var, state="readonly", width=48)
        self.booking_combo.grid(row=0, column=1, sticky="w", padx=8, pady=6)

        tk.Label(form, text="Menu Item", bg="#FFFFFF", fg="#4E342E").grid(row=1, column=0, sticky="w", pady=6)
        self.menu_var = tk.StringVar()
        self.menu_combo = ttk.Combobox(form, textvariable=self.menu_var, state="readonly", width=36)
        self.menu_combo.grid(row=1, column=1, sticky="w", padx=8, pady=6)
        tk.Label(form, text="Qty", bg="#FFFFFF", fg="#4E342E").grid(row=1, column=2, sticky="w", pady=6)
        self.qty_var = tk.IntVar(value=1)
        ttk.Spinbox(form, from_=1, to=20, textvariable=self.qty_var, width=6).grid(row=1, column=3, sticky="w", padx=8, pady=6)
        ttk.Button(form, text="Add Item", command=self.add_item).grid(row=1, column=4, sticky="w", padx=8)

        self.tree = ttk.Treeview(self, columns=("Item", "Qty", "Price", "Total"), show="headings", height=8)
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        for col, text in (("Item", "Item"), ("Qty", "Qty"), ("Price", "Unit Price"), ("Total", "Line Total")):
            self.tree.heading(col, text=text)

        totals = tk.Frame(self, bg="#FFF8F0")
        totals.pack(fill="x", padx=16, pady=(0, 12))
        self.subtotal_var = tk.StringVar(value="₹0.00")
        self.tax_var = tk.StringVar(value="₹0.00")
        self.service_var = tk.StringVar(value="₹0.00")
        self.total_var = tk.StringVar(value="₹0.00")
        tk.Label(totals, text="Subtotal:", bg="#FFF8F0").grid(row=0, column=0, sticky="e")
        tk.Label(totals, textvariable=self.subtotal_var, bg="#FFF8F0").grid(row=0, column=1, sticky="w", padx=8)
        tk.Label(totals, text="Tax (18%):", bg="#FFF8F0").grid(row=1, column=0, sticky="e")
        tk.Label(totals, textvariable=self.tax_var, bg="#FFF8F0").grid(row=1, column=1, sticky="w", padx=8)
        tk.Label(totals, text="Service (5%):", bg="#FFF8F0").grid(row=2, column=0, sticky="e")
        tk.Label(totals, textvariable=self.service_var, bg="#FFF8F0").grid(row=2, column=1, sticky="w", padx=8)
        tk.Label(totals, text="Total:", font=("Segoe UI", 11, "bold"), bg="#FFF8F0").grid(row=3, column=0, sticky="e", pady=(6,0))
        tk.Label(totals, textvariable=self.total_var, font=("Segoe UI", 11, "bold"), bg="#FFF8F0").grid(row=3, column=1, sticky="w", padx=8, pady=(6,0))

        actions = tk.Frame(self, bg="#FFF8F0")
        actions.pack(fill="x", padx=16)
        ttk.Button(actions, text="Print Bill", command=self.print_bill).pack(side="right", padx=8)
        ttk.Button(actions, text="Clear", command=self.clear_order).pack(side="right")

    def load_bookings(self):
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT id, customer_name, table_id, booking_date, booking_time FROM Bookings WHERE status != 'Cancelled' ORDER BY booking_date DESC").fetchall()
        conn.close()
        display = [f"{r['id']} - {r['customer_name']} | Table {r['table_id']} | {r['booking_date']} {r['booking_time']}" for r in rows]
        self.booking_map = {display[i]: rows[i]['id'] for i in range(len(rows))}
        self.booking_combo['values'] = display
        if display:
            self.booking_var.set(display[0])

    def load_menu_items(self):
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT id, name, price FROM MenuItems WHERE availability = 'Available'").fetchall()
        conn.close()
        display = [f"{r['id']} - {r['name']} (₹{r['price']:.2f})" for r in rows]
        self.menu_map = {display[i]: (rows[i]['id'], rows[i]['name'], rows[i]['price']) for i in range(len(rows))}
        self.menu_combo['values'] = display
        if display:
            self.menu_var.set(display[0])

    def add_item(self):
        sel = self.menu_var.get()
        if not sel:
            messagebox.showwarning("Select", "Choose a menu item first.")
            return
        item_id, name, price = self.menu_map[sel]
        qty = int(self.qty_var.get())
        line_total = price * qty
        self.order_items.append({'id': item_id, 'name': name, 'qty': qty, 'price': price, 'total': line_total})
        self.refresh_tree()

    def refresh_tree(self):
        for it in self.tree.get_children():
            self.tree.delete(it)
        subtotal = 0.0
        for item in self.order_items:
            subtotal += item['total']
            self.tree.insert('', 'end', values=(item['name'], item['qty'], f"₹{item['price']:.2f}", f"₹{item['total']:.2f}"))
        tax = subtotal * 0.18
        service = subtotal * 0.05
        total = subtotal + tax + service
        self.subtotal_var.set(f"₹{subtotal:.2f}")
        self.tax_var.set(f"₹{tax:.2f}")
        self.service_var.set(f"₹{service:.2f}")
        self.total_var.set(f"₹{total:.2f}")

    def clear_order(self):
        self.order_items = []
        self.refresh_tree()

    def print_bill(self):
        if not self.order_items:
            messagebox.showwarning("Empty", "Add at least one item to print a bill.")
            return
        booking_display = self.booking_var.get()
        booking_id = self.booking_map.get(booking_display)
        if not booking_id:
            messagebox.showwarning("Booking", "Select a valid booking.")
            return
        # Build PDF
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'bills')
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"bill_{booking_id}.pdf")
        doc = SimpleDocTemplate(path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        elements.append(Paragraph("Hotel TAJ", styles['Title']))
        elements.append(Paragraph(f"Booking: {booking_display}", styles['Normal']))
        elements.append(Spacer(1, 12))
        data = [["Item", "Qty", "Unit", "Total"]]
        subtotal = 0.0
        for it in self.order_items:
            data.append([it['name'], str(it['qty']), f"₹{it['price']:.2f}", f"₹{it['total']:.2f}"])
            subtotal += it['total']
        tax = subtotal * 0.18
        service = subtotal * 0.05
        total = subtotal + tax + service
        data.append(["", "", "Subtotal", f"₹{subtotal:.2f}"])
        data.append(["", "", "Tax (18%)", f"₹{tax:.2f}"])
        data.append(["", "", "Service (5%)", f"₹{service:.2f}"])
        data.append(["", "", "Total", f"₹{total:.2f}"])
        table = RLTable(data, hAlign='LEFT')
        elements.append(table)
        doc.build(elements)
        messagebox.showinfo("Printed", f"Bill exported to {path}")

