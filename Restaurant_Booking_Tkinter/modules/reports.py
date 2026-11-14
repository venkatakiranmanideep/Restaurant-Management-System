import os
import tkinter as tk
from tkinter import messagebox, ttk

import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

from database import get_connection


class ReportsWindow(tk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent, bg="#FFF8F0")
        self.db_path = db_path
        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self, bg="#FFF8F0")
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text="Reports Center", font=("Segoe UI", 16, "bold"), bg="#FFF8F0", fg="#4E342E").pack(anchor="w")
        tk.Label(header, text="Daily, monthly and customer insights", font=("Segoe UI", 10), bg="#FFF8F0", fg="#7D7D7D").pack(anchor="w")

        actions = tk.LabelFrame(self, text="Generate Reports", bg="#FFFFFF", fg="#7B4B3A", padx=14, pady=14)
        actions.pack(fill="x", pady=(0, 12))
        ttk.Button(actions, text="Daily Bookings", command=self.daily_report).pack(side="left", padx=6)
        ttk.Button(actions, text="Monthly Bookings", command=self.monthly_report).pack(side="left", padx=6)
        ttk.Button(actions, text="Revenue Report", command=self.revenue_report).pack(side="left", padx=6)
        ttk.Button(actions, text="Customer Report", command=self.customer_report).pack(side="left", padx=6)
        ttk.Button(actions, text="Export PDF", command=self.export_pdf).pack(side="left", padx=6)
        ttk.Button(actions, text="Export Excel", command=self.export_excel).pack(side="left", padx=6)

        self.output = tk.Text(self, bg="#FFFFFF", fg="#4E342E", height=18)
        self.output.pack(fill="both", expand=True, pady=(0, 12))

    def daily_report(self):
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT booking_date, COUNT(*) FROM Bookings GROUP BY booking_date ORDER BY booking_date").fetchall()
        conn.close()
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "Daily Bookings\n")
        for row in rows:
            self.output.insert(tk.END, f"{row[0]} -> {row[1]} booking(s)\n")
        messagebox.showinfo("Report", "Daily report generated.")

    def monthly_report(self):
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT substr(booking_date, 1, 7), COUNT(*) FROM Bookings GROUP BY substr(booking_date, 1, 7) ORDER BY substr(booking_date, 1, 7)").fetchall()
        conn.close()
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "Monthly Bookings\n")
        for row in rows:
            self.output.insert(tk.END, f"{row[0]} -> {row[1]} booking(s)\n")
        messagebox.showinfo("Report", "Monthly report generated.")

    def revenue_report(self):
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT booking_date, SUM(guests * 20) FROM Bookings WHERE status != 'Cancelled' GROUP BY booking_date ORDER BY booking_date").fetchall()
        conn.close()
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "Revenue Report\n")
        for row in rows:
            self.output.insert(tk.END, f"{row[0]} -> ₹{row[1]:.2f}\n")
        messagebox.showinfo("Report", "Revenue report generated.")

    def customer_report(self):
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT customer_name, COUNT(*) FROM Bookings GROUP BY customer_name ORDER BY COUNT(*) DESC").fetchall()
        conn.close()
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "Customer Report\n")
        for row in rows:
            self.output.insert(tk.END, f"{row[0]} -> {row[1]} reservation(s)\n")
        messagebox.showinfo("Report", "Customer report generated.")

    def export_pdf(self):
        content = self.output.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Export", "Generate a report first.")
            return
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "reports", "report.pdf")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="ReportTitle", fontName="Helvetica-Bold", fontSize=16, leading=20, spaceAfter=12))
        styles.add(ParagraphStyle(name="ReportBody", fontName="Helvetica", fontSize=10, leading=14, spaceAfter=4))
        doc = SimpleDocTemplate(path, pagesize=letter)
        lines = [Paragraph("Hotel TAJ Report", style="ReportTitle")]
        for line in content.splitlines():
            lines.append(Paragraph(line, style="ReportBody"))
        doc.build(lines)
        messagebox.showinfo("Export", f"PDF exported to {path}")

    def export_excel(self):
        content = self.output.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Export", "Generate a report first.")
            return
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "reports", "report.xlsx")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Report"
        for row_index, line in enumerate(content.splitlines(), start=1):
            sheet.cell(row=row_index, column=1, value=line)
        workbook.save(path)
        messagebox.showinfo("Export", f"Excel exported to {path}")
