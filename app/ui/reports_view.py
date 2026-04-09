from datetime import datetime
from tkinter import messagebox, ttk

from app.database import fetch_all
from app.utils import export_rows_to_csv


class ReportsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=12)
        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=8)

        ttk.Label(controls, text="Report Date (YYYY-MM-DD)").pack(side="left", padx=6)
        self.date_entry = ttk.Entry(controls, width=18)
        self.date_entry.pack(side="left", padx=6)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ttk.Button(controls, text="Daily Appointments", command=self.daily_appointments).pack(side="left", padx=6)
        ttk.Button(controls, text="Total Revenue", command=self.total_revenue).pack(side="left", padx=6)
        ttk.Button(controls, text="Export Current", command=self.export_current).pack(side="left", padx=6)

        self.tree = ttk.Treeview(self, show="headings", height=14)
        self.tree.pack(fill="both", expand=True, pady=8)
        self.current_headers = []
        self.current_rows = []

    def _render(self, headers, rows):
        self.tree["columns"] = headers
        for col in headers:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)
        self.current_headers = headers
        self.current_rows = rows

    def daily_appointments(self):
        date_str = self.date_entry.get().strip()
        rows = fetch_all(
            """
            SELECT a.appointment_id, p.name AS patient, d.name AS doctor, a.date, a.time, a.status
            FROM appointments a
            JOIN patients p ON p.patient_id = a.patient_id
            JOIN doctors d ON d.doctor_id = a.doctor_id
            WHERE a.date = ?
            ORDER BY a.time
            """,
            (date_str,),
        )
        self._render(["ID", "Patient", "Doctor", "Date", "Time", "Status"], rows)

    def total_revenue(self):
        rows = fetch_all(
            "SELECT bill_date, ROUND(SUM(total_amount), 2) AS revenue FROM billing GROUP BY bill_date ORDER BY bill_date DESC"
        )
        self._render(["Date", "Revenue"], rows)

    def export_current(self):
        if not self.current_rows:
            messagebox.showerror("Export", "Generate a report first.")
            return
        path = export_rows_to_csv(self.current_headers, self.current_rows)
        if path:
            messagebox.showinfo("Export", f"Report exported to:\n{path}")
