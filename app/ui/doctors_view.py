import sqlite3
from tkinter import messagebox, ttk

from app.database import execute, fetch_all
from app.validators import is_empty, is_valid_phone


class DoctorsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=12)
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Doctor Form", padding=10)
        form.pack(fill="x", pady=8)
        labels = ["Name", "Specialization", "Phone", "Fees"]
        self.entries = {}
        for i, text in enumerate(labels):
            ttk.Label(form, text=text).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            entry = ttk.Entry(form, width=35)
            entry.grid(row=i, column=1, padx=6, pady=4)
            self.entries[text] = entry
        ttk.Button(form, text="Add", command=self.add_doctor).grid(row=0, column=2, padx=8)
        ttk.Button(form, text="Update", command=self.update_doctor).grid(row=1, column=2, padx=8)
        ttk.Button(form, text="Delete", command=self.delete_doctor).grid(row=2, column=2, padx=8)
        ttk.Label(form, text="Search (Name/ID)").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        self.search_entry = ttk.Entry(form, width=35)
        self.search_entry.grid(row=4, column=1, padx=6, pady=4)
        ttk.Button(form, text="Search", command=self.search).grid(row=4, column=2, padx=8)

    def _build_table(self):
        cols = ("ID", "Name", "Specialization", "Phone", "Fees")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)
        self.tree.pack(fill="both", expand=True, pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)

    def _validate(self):
        values = [e.get().strip() for e in self.entries.values()]
        if any(is_empty(v) for v in values):
            return "All fields are required."
        if not is_valid_phone(values[2]):
            return "Phone must be numeric (10-12 digits)."
        try:
            float(values[3])
        except ValueError:
            return "Fees must be a number."
        return None

    def add_doctor(self):
        error = self._validate()
        if error:
            messagebox.showerror("Validation Error", error)
            return
        values = [e.get().strip() for e in self.entries.values()]
        try:
            execute(
                "INSERT INTO doctors(name, specialization, phone, fees) VALUES(?,?,?,?)",
                (values[0], values[1], values[2], float(values[3])),
            )
            self.refresh()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Phone", "This phone number is already assigned to another doctor.")
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def update_doctor(self):
        if not self.selected_id:
            messagebox.showerror("Selection Error", "Select a doctor row to edit.")
            return
        error = self._validate()
        if error:
            messagebox.showerror("Validation Error", error)
            return
        values = [e.get().strip() for e in self.entries.values()]
        try:
            execute(
                "UPDATE doctors SET name=?, specialization=?, phone=?, fees=? WHERE doctor_id=?",
                (values[0], values[1], values[2], float(values[3]), self.selected_id),
            )
            self.refresh()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Phone", "This phone number is already assigned to another doctor.")
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def delete_doctor(self):
        if not self.selected_id:
            messagebox.showerror("Selection Error", "Select a doctor row to delete.")
            return
        try:
            execute("DELETE FROM doctors WHERE doctor_id=?", (self.selected_id,))
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def search(self):
        key = self.search_entry.get().strip()
        if not key:
            self.refresh()
            return
        rows = fetch_all(
            "SELECT * FROM doctors WHERE name LIKE ? OR CAST(doctor_id AS TEXT) LIKE ?",
            (f"%{key}%", f"%{key}%"),
        )
        self._render(rows)

    def refresh(self):
        self._render(fetch_all("SELECT * FROM doctors ORDER BY doctor_id DESC"))

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
