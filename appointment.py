import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def appointment_window(root):
    win = tk.Toplevel(root)
    win.title("Appointment Booking")
    win.geometry("700x450")

    tk.Label(win, text="Select Patient").grid(row=0, column=0, pady=5)
    tk.Label(win, text="Select Doctor").grid(row=1, column=0, pady=5)
    tk.Label(win, text="Date").grid(row=2, column=0, pady=5)
    tk.Label(win, text="Time").grid(row=3, column=0, pady=5)

    # Dropdowns
    patient_combo = ttk.Combobox(win, width=30)
    patient_combo.grid(row=0, column=1)

    doctor_combo = ttk.Combobox(win, width=30)
    doctor_combo.grid(row=1, column=1)

    date_entry = tk.Entry(win)
    date_entry.grid(row=2, column=1)

    time_entry = tk.Entry(win)
    time_entry.grid(row=3, column=1)

    
    def load_patients():
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT patient_id, name FROM patients")
        data = cursor.fetchall()
        conn.close()

        patient_combo['values'] = [
            f"{row[0]} - {row[1]}" for row in data
        ]

    
    def load_doctors():
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT doctor_id, name FROM doctors")
        data = cursor.fetchall()
        conn.close()

        doctor_combo['values'] = [
            f"{row[0]} - {row[1]}" for row in data
        ]

    
    def book():
        try:
            patient = patient_combo.get().split(" - ")[0]
            doctor = doctor_combo.get().split(" - ")[0]
            date = date_entry.get()
            time = time_entry.get()

            conn = sqlite3.connect("hospital.db")
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO appointments(patient_id, doctor_id, date, time)
            VALUES(?,?,?,?)
            """, (patient, doctor, date, time))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Appointment Booked Successfully")

            date_entry.delete(0, tk.END)
            time_entry.delete(0, tk.END)

            view_appointments()

        except:
            messagebox.showerror("Error", "Please select valid data")

    tk.Button(win, text="Book Appointment", command=book)\
        .grid(row=4, column=1, pady=10)

    
    columns = ("ID", "Patient ID", "Doctor ID", "Date", "Time")

    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.grid(row=6, column=0, columnspan=3, pady=15)

    for col in columns:
        tree.heading(col, text=col)

    
    def view_appointments():
        for row in tree.get_children():
            tree.delete(row)

        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    
    def delete_appointment():
        selected = tree.selection()

        if not selected:
            messagebox.showerror("Error", "Select appointment first")
            return

        appointment_id = tree.item(selected[0])['values'][0]

        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE appointment_id=?", (appointment_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Appointment Deleted")

        view_appointments()

    tk.Button(win, text="Delete Appointment", command=delete_appointment)\
        .grid(row=7, column=0, columnspan=3, pady=5)

    load_patients()
    load_doctors()
    view_appointments()
