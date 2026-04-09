from tkinter import messagebox, ttk

from app.database import fetch_all
from app.ui.appointments_view import AppointmentsView
from app.ui.billing_view import BillingView
from app.ui.doctors_view import DoctorsView
from app.ui.patients_view import PatientsView
from app.ui.reports_view import ReportsView
from app.utils import backup_database, restore_database


class DashboardView(ttk.Frame):
    def __init__(self, parent, username, on_logout, on_toggle_dark):
        super().__init__(parent, padding=10)
        self.username = username
        self.on_logout = on_logout
        self.on_toggle_dark = on_toggle_dark
        self.pack(fill="both", expand=True)
        self._build_header()
        self._build_stats()
        self._build_tabs()

    def _build_header(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=4)
        ttk.Label(top, text=f"Welcome, {self.username}", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="Dark Mode", command=self.on_toggle_dark).pack(side="right", padx=4)
        ttk.Button(top, text="Logout", command=self.on_logout).pack(side="right", padx=4)
        ttk.Button(top, text="Backup DB", command=self._backup).pack(side="right", padx=4)
        ttk.Button(top, text="Restore DB", command=self._restore).pack(side="right", padx=4)

    def _build_stats(self):
        stats = ttk.Frame(self)
        stats.pack(fill="x", pady=8)
        total_patients = fetch_all("SELECT COUNT(*) FROM patients")[0][0]
        total_doctors = fetch_all("SELECT COUNT(*) FROM doctors")[0][0]
        total_appointments = fetch_all("SELECT COUNT(*) FROM appointments")[0][0]
        total_revenue = fetch_all("SELECT COALESCE(SUM(total_amount), 0) FROM billing")[0][0]
        for txt in [
            f"Patients: {total_patients}",
            f"Doctors: {total_doctors}",
            f"Appointments: {total_appointments}",
            f"Revenue: {total_revenue:.2f}",
        ]:
            ttk.Label(stats, text=txt).pack(side="left", padx=10)

    def _build_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        pages = [
            ("Patients", PatientsView(notebook)),
            ("Doctors", DoctorsView(notebook)),
            ("Appointments", AppointmentsView(notebook)),
            ("Billing", BillingView(notebook)),
            ("Reports", ReportsView(notebook)),
        ]
        for title, frame in pages:
            notebook.add(frame, text=title)

    def _backup(self):
        path = backup_database()
        if path:
            messagebox.showinfo("Backup", f"Database backed up to:\n{path}")

    def _restore(self):
        path = restore_database()
        if path:
            messagebox.showinfo("Restore", f"Database restored from:\n{path}\nPlease restart app.")
