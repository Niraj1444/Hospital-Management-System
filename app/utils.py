import csv
import shutil
from pathlib import Path
from tkinter import filedialog

from app.database import DB_PATH


def export_rows_to_csv(headers, rows):
    file_path = filedialog.asksaveasfilename(
        title="Export CSV",
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
    )
    if not file_path:
        return None
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)
    return file_path


def export_bill_text(content):
    file_path = filedialog.asksaveasfilename(
        title="Export Bill",
        defaultextension=".pdf",
        filetypes=[("PDF/Text Compatible", "*.pdf"), ("Text Files", "*.txt")],
    )
    if not file_path:
        return None
    Path(file_path).write_text(content, encoding="utf-8")
    return file_path


def backup_database():
    file_path = filedialog.asksaveasfilename(
        title="Backup Database",
        defaultextension=".db",
        filetypes=[("SQLite DB", "*.db")],
    )
    if not file_path:
        return None
    shutil.copy2(DB_PATH, file_path)
    return file_path


def restore_database():
    file_path = filedialog.askopenfilename(
        title="Restore Database",
        filetypes=[("SQLite DB", "*.db")],
    )
    if not file_path:
        return None
    shutil.copy2(file_path, DB_PATH)
    return file_path
