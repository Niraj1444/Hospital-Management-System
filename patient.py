import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def patient_window(root):
    win = tk.Toplevel(root)
    win.title("Patient Management")
    win.geometry("800x400")

    labels = ["Name", "Age", "Gender", "Contact", "Disease", "Admission Date"]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(win, text=label).grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(win)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    def add_patient():
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO patients(name, age, gender, contact, disease, admission_date)
        VALUES(?,?,?,?,?,?)
        """, [e.get() for e in entries])
        conn.commit()
        conn.close()
        view_patients()

    tk.Button(win, text="Add Patient", command=add_patient)\
        .grid(row=7, column=1)

    columns = ("ID", "Name", "Age", "Gender", "Contact", "Disease", "Date")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.grid(row=0, column=3, rowspan=10, padx=20)

    for col in columns:
        tree.heading(col, text=col)

    def view_patients():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
        conn.close()

    def delete_patient():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a patient first")
            return
        patient_id = tree.item(selected[0])['values'][0]

        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))
        conn.commit()
        conn.close()

        view_patients()
        messagebox.showinfo("Success", "Patient Deleted")

    tk.Button(win, text="Delete Patient", command=delete_patient)\
        .grid(row=8, column=1)

    view_patients()
