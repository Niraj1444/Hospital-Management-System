from datetime import datetime
from tkinter import messagebox, ttk

from app.database import execute, fetch_all
from app.utils import export_bill_text


class BillingView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=12)
        self.preview_text = ""
        self._build_form()
        self._build_table()
        self._load_patients()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Advanced Billing", padding=10)
        form.pack(fill="x", pady=8)
        ttk.Label(form, text="Patient").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(form, text="Doctor Fee").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(form, text="Medicine Cost").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(form, text="Room Charge").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(form, text="GST (%)").grid(row=4, column=0, sticky="w", padx=6, pady=4)

        self.patient_combo = ttk.Combobox(form, width=35, state="readonly")
        self.doctor_fee = ttk.Entry(form, width=38)
        self.medicine_cost = ttk.Entry(form, width=38)
        self.room_charge = ttk.Entry(form, width=38)
        self.gst_rate = ttk.Entry(form, width=38)
        self.gst_rate.insert(0, "18")

        self.patient_combo.grid(row=0, column=1, padx=6, pady=4)
        self.doctor_fee.grid(row=1, column=1, padx=6, pady=4)
        self.medicine_cost.grid(row=2, column=1, padx=6, pady=4)
        self.room_charge.grid(row=3, column=1, padx=6, pady=4)
        self.gst_rate.grid(row=4, column=1, padx=6, pady=4)

        ttk.Button(form, text="Preview Bill", command=self.preview_bill).grid(row=1, column=2, padx=8)
        ttk.Button(form, text="Save Bill", command=self.save_bill).grid(row=2, column=2, padx=8)
        ttk.Button(form, text="Export Bill", command=self.export_bill).grid(row=3, column=2, padx=8)

        self.preview_label = ttk.Label(form, text="Preview will be shown here.")
        self.preview_label.grid(row=5, column=0, columnspan=3, sticky="w", padx=6, pady=8)

    def _build_table(self):
        cols = ("Bill ID", "Patient ID", "Date", "Doctor Fee", "Medicine", "Room", "GST", "Total")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        self.tree.pack(fill="both", expand=True, pady=6)

    def _load_patients(self):
        rows = fetch_all("SELECT patient_id, name FROM patients ORDER BY name")
        self.patient_combo["values"] = [f"{r[0]} - {r[1]}" for r in rows]

    def _calculate(self):
        patient = self.patient_combo.get()
        if " - " not in patient:
            raise ValueError("Please select a patient.")
        patient_id = int(patient.split(" - ")[0])
        d_fee = float(self.doctor_fee.get().strip())
        m_fee = float(self.medicine_cost.get().strip())
        r_fee = float(self.room_charge.get().strip())
        gst_rate = float(self.gst_rate.get().strip())
        subtotal = d_fee + m_fee + r_fee
        gst_amount = round(subtotal * (gst_rate / 100), 2)
        total = round(subtotal + gst_amount, 2)
        return patient_id, d_fee, m_fee, r_fee, gst_rate, gst_amount, total

    def preview_bill(self):
        try:
            patient_id, d_fee, m_fee, r_fee, gst_rate, gst_amount, total = self._calculate()
        except Exception as exc:
            messagebox.showerror("Validation Error", str(exc))
            return
        bill_date = datetime.now().strftime("%Y-%m-%d")
        self.preview_text = (
            f"Bill Date: {bill_date}\n"
            f"Patient ID: {patient_id}\n"
            f"Doctor Fee: {d_fee:.2f}\nMedicine Cost: {m_fee:.2f}\nRoom Charge: {r_fee:.2f}\n"
            f"GST ({gst_rate:.2f}%): {gst_amount:.2f}\nTotal: {total:.2f}"
        )
        self.preview_label.config(text=self.preview_text)

    def save_bill(self):
        if not self.preview_text:
            self.preview_bill()
            if not self.preview_text:
                return
        patient_id, d_fee, m_fee, r_fee, gst_rate, gst_amount, total = self._calculate()
        bill_date = datetime.now().strftime("%Y-%m-%d")
        execute(
            """
            INSERT INTO billing(patient_id, bill_date, doctor_fee, medicine_cost, room_charge, gst_rate, gst_amount, total_amount)
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (patient_id, bill_date, d_fee, m_fee, r_fee, gst_rate, gst_amount, total),
        )
        messagebox.showinfo("Billing", "Bill saved successfully.")
        self.refresh()

    def export_bill(self):
        if not self.preview_text:
            self.preview_bill()
            if not self.preview_text:
                return
        saved = export_bill_text(self.preview_text)
        if saved:
            messagebox.showinfo("Export", f"Bill exported to:\n{saved}")

    def refresh(self):
        self._load_patients()
        rows = fetch_all("SELECT * FROM billing ORDER BY bill_id DESC")
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)
