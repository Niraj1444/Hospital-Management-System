import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def doctor_window(root):
    win = tk.Toplevel(root)
    win.title("Doctor Management")
    win.geometry("750x450")

    labels = ["Name", "Specialization", "Phone", "Fees"]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(win, text=label).grid(row=i, column=0, padx=10, pady=5)
        entry = tk.Entry(win)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    
    def add_doctor():
        try:
            conn = sqlite3.connect("hospital.db")
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO doctors(name, specialization, phone, fees)
            VALUES(?,?,?,?)
            """, (
                entries[0].get(),
                entries[1].get(),
                entries[2].get(),
                float(entries[3].get())
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Doctor Added Successfully")
            view_doctors()

            for e in entries:
                e.delete(0, tk.END)

        except:
            messagebox.showerror("Error", "Please enter valid data")

    tk.Button(win, text="Add Doctor", command=add_doctor)\
        .grid(row=5, column=1, pady=10)

    
    columns = ("ID", "Name", "Specialization", "Phone", "Fees")

    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.grid(row=0, column=3, rowspan=12, padx=20)

    for col in columns:
        tree.heading(col, text=col)

   
    def view_doctors():
        for row in tree.get_children():
            tree.delete(row)

        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    tk.Button(win, text="View Doctors", command=view_doctors)\
        .grid(row=6, column=1, pady=5)

    
    def delete_doctor():
        selected = tree.selection()

        if not selected:
            messagebox.showerror("Error", "Select a doctor first")
            return

        doctor_id = tree.item(selected[0])['values'][0]

        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM doctors WHERE doctor_id=?", (doctor_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Doctor Deleted")
        view_doctors()

    tk.Button(win, text="Delete Doctor", command=delete_doctor)\
        .grid(row=7, column=1, pady=5)

    view_doctors()
