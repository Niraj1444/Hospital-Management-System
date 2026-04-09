import sqlite3

def connect():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        contact TEXT,
        disease TEXT,
        admission_date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors(
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialization TEXT,
        phone TEXT,
        fees REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        date TEXT,
        time TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS billing(
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_fee REAL,
        medicine_cost REAL,
        room_charge REAL,
        total_amount REAL
    )
    """)

    conn.commit()
    conn.close()
