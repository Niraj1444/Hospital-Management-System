import tkinter as tk
from tkinter import messagebox

def login_screen(root, success_callback):
    frame = tk.Frame(root)
    frame.pack()

    tk.Label(frame, text="Admin Login", font=("Arial", 16)).pack(pady=10)

    tk.Label(frame, text="Username").pack()
    username = tk.Entry(frame)
    username.pack()

    tk.Label(frame, text="Password").pack()
    password = tk.Entry(frame, show="*")
    password.pack()

    def check_login():
        if username.get() == "admin" and password.get() == "1234":
            frame.destroy()
            success_callback()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    tk.Button(frame, text="Login", command=check_login).pack(pady=10)
