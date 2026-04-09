import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "hospital.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _create_schema():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS doctors(
                doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                fees REAL NOT NULL CHECK (fees >= 0)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patients(
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK (age > 0),
                gender TEXT NOT NULL,
                contact TEXT NOT NULL UNIQUE,
                disease TEXT NOT NULL,
                admission_date TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments(
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Booked',
                FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS billing(
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                bill_date TEXT NOT NULL,
                doctor_fee REAL NOT NULL CHECK (doctor_fee >= 0),
                medicine_cost REAL NOT NULL CHECK (medicine_cost >= 0),
                room_charge REAL NOT NULL CHECK (room_charge >= 0),
                gst_rate REAL NOT NULL CHECK (gst_rate >= 0),
                gst_amount REAL NOT NULL CHECK (gst_amount >= 0),
                total_amount REAL NOT NULL CHECK (total_amount >= 0),
                FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
            )
            """
        )


def _quarantine_invalid_db():
    if not DB_PATH.exists():
        return True
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bad_path = DB_PATH.with_name(f"hospital_invalid_{stamp}.db")
    try:
        DB_PATH.rename(bad_path)
        return True
    except PermissionError:
        return False


def init_db():
    global DB_PATH
    try:
        _create_schema()
    except sqlite3.DatabaseError:
        # Existing file is not a valid SQLite database.
        quarantined = _quarantine_invalid_db()
        if not quarantined:
            # If file is locked by another process, switch to a new DB file.
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            DB_PATH = DB_PATH.with_name(f"hospital_recovered_{stamp}.db")
        _create_schema()


def fetch_all(query, params=()):
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def execute(query, params=()):
    with get_connection() as conn:
        conn.execute(query, params)
        conn.commit()
