import tkinter as tk

from app.auth import ensure_default_admin
from app.database import init_db
from app.ui.dashboard_view import DashboardView
from app.ui.login_view import LoginView
from app.ui.theme import apply_theme


class HospitalApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hospital Management System - Phase 2")
        self.root.geometry("1200x720")
        self.dark_mode = False
        self.current_view = None

    def start(self):
        init_db()
        ensure_default_admin()
        apply_theme(self.root, self.dark_mode)
        self.show_login()
        self.root.mainloop()

    def clear_view(self):
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None

    def show_login(self):
        self.clear_view()
        self.current_view = LoginView(self.root, on_login=self.show_dashboard)

    def show_dashboard(self, username):
        self.clear_view()
        self.current_view = DashboardView(
            self.root,
            username=username,
            on_logout=self.show_login,
            on_toggle_dark=self.toggle_dark_mode,
        )

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        apply_theme(self.root, self.dark_mode)
        if self.current_view:
            self.current_view.destroy()
        self.show_login()


def run_app():
    app = HospitalApp()
    app.start()
