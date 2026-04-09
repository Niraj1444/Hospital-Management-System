import sqlite3
from tkinter import messagebox, ttk

from app.database import execute, fetch_all
from app.validators import is_empty, is_valid_date, is_valid_phone


class PatientsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=12)
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Patient Form", padding=10)
        form.pack(fill="x", pady=8)
        labels = ["Name", "Age", "Gender", "Contact", "Disease", "Admission Date (YYYY-MM-DD)"]
        self.entries = {}
        for i, text in enumerate(labels):
            ttk.Label(form, text=text).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            entry = ttk.Entry(form, width=35)
            entry.grid(row=i, column=1, padx=6, pady=4)
            self.entries[text] = entry

        ttk.Button(form, text="Add", command=self.add_patient).grid(row=0, column=2, padx=8)
        ttk.Button(form, text="Update", command=self.update_patient).grid(row=1, column=2, padx=8)
        ttk.Button(form, text="Delete", command=self.delete_patient).grid(row=2, column=2, padx=8)
        ttk.Button(form, text="Clear", command=self.clear).grid(row=3, column=2, padx=8)

        ttk.Label(form, text="Search (Name/ID)").grid(row=6, column=0, sticky="w", padx=6, pady=4)
        self.search_entry = ttk.Entry(form, width=35)
        self.search_entry.grid(row=6, column=1, padx=6, pady=4)
        ttk.Button(form, text="Search", command=self.search).grid(row=6, column=2, padx=8)

    def _build_table(self):
        cols = ("ID", "Name", "Age", "Gender", "Contact", "Disease", "Date")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        self.tree.pack(fill="both", expand=True, pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)

    def _validate(self):
        values = [e.get().strip() for e in self.entries.values()]
        if any(is_empty(v) for v in values):
            return "All fields are required."
        if not values[1].isdigit():
            return "Age must be a number."
        if not is_valid_phone(values[3]):
            return "Contact must be numeric (10-12 digits)."
        if not is_valid_date(values[5]):
            return "Admission date must be YYYY-MM-DD."
        return None

    def add_patient(self):
        error = self._validate()
        if error:
            messagebox.showerror("Validation Error", error)
            return
        values = [e.get().strip() for e in self.entries.values()]
        try:
            execute(
                "INSERT INTO patients(name, age, gender, contact, disease, admission_date) VALUES(?,?,?,?,?,?)",
                (values[0], int(values[1]), values[2], values[3], values[4], values[5]),
            )
            self.refresh()
            self.clear()
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def update_patient(self):
        if not self.selected_id:
            messagebox.showerror("Selection Error", "Select a patient row to edit.")
            return
        error = self._validate()
        if error:
            messagebox.showerror("Validation Error", error)
            return
        values = [e.get().strip() for e in self.entries.values()]
        try:
            execute(
                "UPDATE patients SET name=?, age=?, gender=?, contact=?, disease=?, admission_date=? WHERE patient_id=?",
                (values[0], int(values[1]), values[2], values[3], values[4], values[5], self.selected_id),
            )
            self.refresh()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Contact", "This contact number is already assigned to another patient.")
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def delete_patient(self):
        if not self.selected_id:
            messagebox.showerror("Selection Error", "Select a patient row to delete.")
            return
        try:
            execute("DELETE FROM patients WHERE patient_id=?", (self.selected_id,))
            self.refresh()
            self.clear()
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def search(self):
        key = self.search_entry.get().strip()
        if not key:
            self.refresh()
            return
        rows = fetch_all(
            "SELECT * FROM patients WHERE name LIKE ? OR CAST(patient_id AS TEXT) LIKE ?",
            (f"%{key}%", f"%{key}%"),
        )
        self._render(rows)

    def refresh(self):
        self._render(fetch_all("SELECT * FROM patients ORDER BY patient_id DESC"))

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
        for entry, value in zip(self.entries.values(), row[1:]):
            entry.delete(0, "end")
            entry.insert(0, value)

    def clear(self):
        self.selected_id = None
        for entry in self.entries.values():
            entry.delete(0, "end")
