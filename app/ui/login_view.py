import tkinter as tk
from tkinter import messagebox, ttk

from app.auth import authenticate


class LoginView(ttk.Frame):
    def __init__(self, parent, on_login):
        super().__init__(parent, padding=20)
        self.on_login = on_login
        self.pack(fill="both", expand=True)

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="Hospital Management Login", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 16)
        )
        ttk.Label(card, text="Username").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Label(card, text="Password").grid(row=2, column=0, sticky="w", pady=6)

        self.username_entry = ttk.Entry(card, width=28)
        self.password_entry = ttk.Entry(card, width=28, show="*")
        self.username_entry.grid(row=1, column=1, pady=6)
        self.password_entry.grid(row=2, column=1, pady=6)

        ttk.Button(card, text="Login", style="Accent.TButton", command=self.try_login).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(12, 2)
        )
        ttk.Label(card, text="Default admin: admin / admin123").grid(
            row=4, column=0, columnspan=2, pady=(8, 0)
        )

    def try_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Validation Error", "Username and password are required.")
            return
        if not authenticate(username, password):
            messagebox.showerror("Login Failed", "Invalid credentials.")
            return
        self.on_login(username)
