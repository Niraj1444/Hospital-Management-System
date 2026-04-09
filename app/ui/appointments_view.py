import sqlite3
from tkinter import messagebox, ttk

from app.database import execute, fetch_all
from app.validators import is_empty, is_valid_date, is_valid_time


class AppointmentsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=12)
        self.selected_id = None
        self._build_form()
        self._build_table()
        self._load_combos()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Appointment Form", padding=10)
        form.pack(fill="x", pady=8)
        ttk.Label(form, text="Patient").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(form, text="Doctor").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(form, text="Time (HH:MM)").grid(row=3, column=0, sticky="w", padx=6, pady=4)

        self.patient_combo = ttk.Combobox(form, width=35, state="readonly")
        self.doctor_combo = ttk.Combobox(form, width=35, state="readonly")
        self.date_entry = ttk.Entry(form, width=38)
        self.time_entry = ttk.Entry(form, width=38)
        self.patient_combo.grid(row=0, column=1, padx=6, pady=4)
        self.doctor_combo.grid(row=1, column=1, padx=6, pady=4)
        self.date_entry.grid(row=2, column=1, padx=6, pady=4)
        self.time_entry.grid(row=3, column=1, padx=6, pady=4)

        ttk.Button(form, text="Book", command=self.add_appointment).grid(row=0, column=2, padx=8)
        ttk.Button(form, text="Update", command=self.update_appointment).grid(row=1, column=2, padx=8)
        ttk.Button(form, text="Delete", command=self.delete_appointment).grid(row=2, column=2, padx=8)

        ttk.Label(form, text="Filter Doctor").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(form, text="Filter Date").grid(row=5, column=0, sticky="w", padx=6, pady=4)
        self.filter_doctor = ttk.Combobox(form, width=35, state="readonly")
        self.filter_date = ttk.Entry(form, width=38)
        self.filter_doctor.grid(row=4, column=1, padx=6, pady=4)
        self.filter_date.grid(row=5, column=1, padx=6, pady=4)
        ttk.Button(form, text="Apply Filter", command=self.apply_filter).grid(row=4, column=2, padx=8)
        ttk.Button(form, text="Reset", command=self.refresh).grid(row=5, column=2, padx=8)

    def _build_table(self):
        cols = ("ID", "Patient ID", "Patient", "Doctor ID", "Doctor", "Date", "Time", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        self.tree.pack(fill="both", expand=True, pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)

    def _load_combos(self):
        patients = fetch_all("SELECT patient_id, name FROM patients ORDER BY name")
        doctors = fetch_all("SELECT doctor_id, name FROM doctors ORDER BY name")
        self.patient_combo["values"] = [f"{p[0]} - {p[1]}" for p in patients]
        self.doctor_combo["values"] = [f"{d[0]} - {d[1]}" for d in doctors]
        self.filter_doctor["values"] = ["All"] + [f"{d[0]} - {d[1]}" for d in doctors]
        self.filter_doctor.set("All")

    def _extract_id(self, combo_value):
        if not combo_value or " - " not in combo_value:
            return None
        return combo_value.split(" - ")[0]

    def _validate(self):
        patient_id = self._extract_id(self.patient_combo.get())
        doctor_id = self._extract_id(self.doctor_combo.get())
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        if any(is_empty(v) for v in (patient_id, doctor_id, date_str, time_str)):
            return "Patient, doctor, date, and time are required."
        if not is_valid_date(date_str):
            return "Date must be in YYYY-MM-DD format."
        if not is_valid_time(time_str):
            return "Time must be in HH:MM format."
        return None

    def add_appointment(self):
        error = self._validate()
        if error:
            messagebox.showerror("Validation Error", error)
            return
        patient_id = int(self._extract_id(self.patient_combo.get()))
        doctor_id = int(self._extract_id(self.doctor_combo.get()))
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        try:
            # Prevent same doctor being double-booked at same date/time.
            existing = fetch_all(
                "SELECT appointment_id FROM appointments WHERE doctor_id=? AND date=? AND time=?",
                (doctor_id, date_str, time_str),
            )
            if existing:
                messagebox.showerror(
                    "Slot Unavailable",
                    "This doctor already has an appointment at the selected date and time.",
                )
                return
            execute(
                "INSERT INTO appointments(patient_id, doctor_id, date, time, status) VALUES(?,?,?,?,?)",
                (patient_id, doctor_id, date_str, time_str, "Booked"),
            )
            messagebox.showinfo("Appointment", "Appointment confirmed.")
            self.refresh()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Reference Error",
                "Selected patient/doctor does not exist. Please refresh and try again.",
            )
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def update_appointment(self):
        if not self.selected_id:
            messagebox.showerror("Selection Error", "Select an appointment row to edit.")
            return
        error = self._validate()
        if error:
            messagebox.showerror("Validation Error", error)
            return
        patient_id = int(self._extract_id(self.patient_combo.get()))
        doctor_id = int(self._extract_id(self.doctor_combo.get()))
        try:
            date_str = self.date_entry.get().strip()
            time_str = self.time_entry.get().strip()
            existing = fetch_all(
                """
                SELECT appointment_id FROM appointments
                WHERE doctor_id=? AND date=? AND time=? AND appointment_id <> ?
                """,
                (doctor_id, date_str, time_str, self.selected_id),
            )
            if existing:
                messagebox.showerror(
                    "Slot Unavailable",
                    "This doctor already has an appointment at the selected date and time.",
                )
                return
            execute(
                "UPDATE appointments SET patient_id=?, doctor_id=?, date=?, time=? WHERE appointment_id=?",
                (patient_id, doctor_id, date_str, time_str, self.selected_id),
            )
            self.refresh()
        except sqlite3.IntegrityError:
            messagebox.showerror("Reference Error", "Invalid patient/doctor reference.")
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def delete_appointment(self):
        if not self.selected_id:
            messagebox.showerror("Selection Error", "Select an appointment row to delete.")
            return
        try:
            execute("DELETE FROM appointments WHERE appointment_id=?", (self.selected_id,))
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def apply_filter(self):
        doctor_value = self.filter_doctor.get()
        date_value = self.filter_date.get().strip()
        query = """
            SELECT a.appointment_id, p.patient_id, p.name, d.doctor_id, d.name, a.date, a.time, a.status
            FROM appointments a
            JOIN patients p ON p.patient_id = a.patient_id
            JOIN doctors d ON d.doctor_id = a.doctor_id
            WHERE 1=1
        """
        params = []
        if doctor_value and doctor_value != "All":
            query += " AND a.doctor_id = ?"
            params.append(int(self._extract_id(doctor_value)))
        if date_value:
            query += " AND a.date = ?"
            params.append(date_value)
        query += " ORDER BY a.appointment_id DESC"
        self._render(fetch_all(query, tuple(params)))

    def refresh(self):
        self._load_combos()
        rows = fetch_all(
            """
            SELECT a.appointment_id, p.patient_id, p.name, d.doctor_id, d.name, a.date, a.time, a.status
            FROM appointments a
            JOIN patients p ON p.patient_id = a.patient_id
            JOIN doctors d ON d.doctor_id = a.doctor_id
            ORDER BY a.appointment_id DESC
            """
        )
        self._render(rows)

    def _render(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def load_selected(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        row = self.tree.item(selected[0], "values")
        self.selected_id = row[0]
        patient_id = str(row[1])
        doctor_id = str(row[3])
        for value in self.patient_combo["values"]:
            if patient_id == value.split(" - ")[0]:
                self.patient_combo.set(value)
                break
        for value in self.doctor_combo["values"]:
            if doctor_id == value.split(" - ")[0]:
                self.doctor_combo.set(value)
                break
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, row[5])
        self.time_entry.delete(0, "end")
        self.time_entry.insert(0, row[6])
