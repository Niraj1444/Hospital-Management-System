from tkinter import ttk


def apply_theme(root, dark_mode=False):
    style = ttk.Style(root)
    style.theme_use("clam")
    bg = "#1e1e1e" if dark_mode else "#f4f6f8"
    fg = "#ffffff" if dark_mode else "#1f2937"
    card = "#2c2c2c" if dark_mode else "#ffffff"
    accent = "#2563eb"
    root.configure(bg=bg)

    style.configure("TFrame", background=bg)
    style.configure("Card.TFrame", background=card, relief="flat")
    style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
    style.configure("TButton", padding=8, font=("Segoe UI", 10))
    style.configure("Accent.TButton", background=accent, foreground="#ffffff")
    style.map("Accent.TButton", background=[("active", "#1e4fcc")])
    style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
