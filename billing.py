import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def billing_window(root):
    win = tk.Toplevel(root)
    win.title("Billing System")
    win.geometry("750x450")

    tk.Label(win, text="Select Patient").grid(row=0, column=0, pady=5)
    tk.Label(win, text="Doctor Fee").grid(row=1, column=0, pady=5)
    tk.Label(win, text="Medicine Cost").grid(row=2, column=0, pady=5)
    tk.Label(win, text="Room Charge").grid(row=3, column=0, pady=5)

    patient_combo = ttk.Combobox(win, width=30)
    patient_combo.grid(row=0, column=1)

    doctor_fee = tk.Entry(win)
    doctor_fee.grid(row=1, column=1)

    medicine_cost = tk.Entry(win)
    medicine_cost.grid(row=2, column=1)

    room_charge = tk.Entry(win)
    room_charge.grid(row=3, column=1)

    total_label = tk.Label(win, text="Total: 0")
    total_label.grid(row=5, column=1)

    
    def load_patients():
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT patient_id, name FROM patients")
        data = cursor.fetchall()
        conn.close()

        patient_combo['values'] = [
            f"{row[0]} - {row[1]}" for row in data
        ]

    
    def generate_bill():
        try:
            patient_id = patient_combo.get().split(" - ")[0]
            d_fee = float(doctor_fee.get())
            m_cost = float(medicine_cost.get())
            r_charge = float(room_charge.get())

            total = d_fee + m_cost + r_charge

            conn = sqlite3.connect("hospital.db")
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO billing(patient_id, doctor_fee, medicine_cost, room_charge, total_amount)
            VALUES(?,?,?,?,?)
            """, (patient_id, d_fee, m_cost, r_charge, total))

            conn.commit()
            conn.close()

            total_label.config(text=f"Total: {total}")
            messagebox.showinfo("Success", "Bill Generated Successfully")

            doctor_fee.delete(0, tk.END)
            medicine_cost.delete(0, tk.END)
            room_charge.delete(0, tk.END)

            view_bills()

        except:
            messagebox.showerror("Error", "Please enter valid data")

    tk.Button(win, text="Generate Bill", command=generate_bill)\
        .grid(row=4, column=1, pady=10)

    
    columns = ("Bill ID", "Patient ID", "Doctor Fee", "Medicine Cost", "Room Charge", "Total")

    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.grid(row=6, column=0, columnspan=3, pady=15)

    for col in columns:
        tree.heading(col, text=col)

    
    def view_bills():
        for row in tree.get_children():
            tree.delete(row)

        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM billing")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    
    def delete_bill():
        selected = tree.selection()

        if not selected:
            messagebox.showerror("Error", "Select bill first")
            return

        bill_id = tree.item(selected[0])['values'][0]

        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM billing WHERE bill_id=?", (bill_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Bill Deleted")

        view_bills()

    tk.Button(win, text="Delete Bill", command=delete_bill)\
        .grid(row=7, column=0, columnspan=3, pady=5)

    load_patients()
    view_bills()
