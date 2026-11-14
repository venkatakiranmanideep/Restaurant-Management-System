import os
import sqlite3
from datetime import datetime
from typing import Optional


DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "database", "restaurant_booking.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    target = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(target), exist_ok=True)
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(db_path: Optional[str] = None) -> str:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'Staff'
        );

        CREATE TABLE IF NOT EXISTS Customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS Tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            capacity INTEGER NOT NULL,
            status TEXT DEFAULT 'Available',
            location TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS Bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            table_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            guests INTEGER NOT NULL,
            status TEXT DEFAULT 'Confirmed',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(table_id) REFERENCES Tables(id)
        );

        CREATE TABLE IF NOT EXISTS MenuCategories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS MenuItems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            availability TEXT DEFAULT 'Available',
            image_path TEXT,
            FOREIGN KEY(category_id) REFERENCES MenuCategories(id)
        );

        CREATE TABLE IF NOT EXISTS Reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()

    seed_initial_data(conn)
    conn.commit()
    conn.close()
    return db_path or DEFAULT_DB_PATH


def seed_initial_data(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO Users (username, email, password, full_name, role) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin@restaurant.com", "admin123", "Prakash Mehra", "Admin"),
        )

    cursor.execute("SELECT COUNT(*) FROM Customers")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO Customers (full_name, email, phone, notes) VALUES (?, ?, ?, ?)",
            ("Asha Sharma", "asha@example.com", "+91-98765-43210", "VIP guest"),
        )

    cursor.execute("SELECT COUNT(*) FROM Tables")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO Tables (name, capacity, status, location) VALUES (?, ?, ?, ?)",
            [
                ("Table 01", 2, "Available", "Window"),
                ("Table 02", 4, "Available", "Center"),
                ("Table 03", 6, "Reserved", "Private"),
            ],
        )

    cursor.execute("SELECT COUNT(*) FROM MenuCategories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO MenuCategories (name, description) VALUES (?, ?)",
            [
                ("Starters", "Freshly prepared appetizers"),
                ("Main Course", "Signature mains"),
                ("Desserts", "Sweet finales"),
                ("Drinks", "Refreshing beverages"),
            ],
        )

    cursor.execute("SELECT COUNT(*) FROM MenuItems")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO MenuItems (category_id, name, price, description, availability) VALUES (?, ?, ?, ?, ?)",
            (1, "Samosa (2 pcs)", 120.0, "Crispy potato-filled pastry served with chutney", "Available"),
        )
        cursor.execute(
            "INSERT INTO MenuItems (category_id, name, price, description, availability) VALUES (?, ?, ?, ?, ?)",
            (2, "Butter Chicken", 420.0, "Classic Punjabi butter chicken with naan or rice", "Available"),
        )
        cursor.execute(
            "INSERT INTO MenuItems (category_id, name, price, description, availability) VALUES (?, ?, ?, ?, ?)",
            (3, "Gulab Jamun (3 pcs)", 150.0, "Soft milk dumplings soaked in rose syrup", "Available"),
        )
        cursor.execute(
            "INSERT INTO MenuItems (category_id, name, price, description, availability) VALUES (?, ?, ?, ?, ?)",
            (4, "Masala Chai", 60.0, "Spiced Indian tea brewed with milk", "Available"),
        )

    cursor.execute("SELECT COUNT(*) FROM Reviews")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO Reviews (customer_name, rating, comment) VALUES (?, ?, ?)",
            ("Asha Sharma", 5, "Warm hospitality and delicious food."),
        )


def validate_booking_slot(conn: sqlite3.Connection, table_id: int, booking_date: str, booking_time: str) -> bool:
    cursor = conn.execute(
        "SELECT id FROM Bookings WHERE table_id = ? AND booking_date = ? AND booking_time = ? AND status != 'Cancelled'",
        (table_id, booking_date, booking_time),
    )
    return cursor.fetchone() is None


def authenticate_user(conn: sqlite3.Connection, username: str, password: str) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM Users WHERE username = ? AND password = ?",
        (username, password),
    ).fetchone()


def get_dashboard_stats(conn: sqlite3.Connection) -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    booking_count = conn.execute("SELECT COUNT(*) FROM Bookings").fetchone()[0]
    available_tables = conn.execute("SELECT COUNT(*) FROM Tables WHERE status = 'Available'").fetchone()[0]
    todays_reservations = conn.execute(
        "SELECT COUNT(*) FROM Bookings WHERE booking_date = ?",
        (today,),
    ).fetchone()[0]
    revenue = conn.execute(
        "SELECT COALESCE(SUM(guests * 20), 0) FROM Bookings WHERE status != 'Cancelled'"
    ).fetchone()[0]
    recent = conn.execute(
        "SELECT customer_name, booking_date, booking_time, guests, status FROM Bookings ORDER BY id DESC LIMIT 5"
    ).fetchall()
    return {
        "total_bookings": booking_count,
        "available_tables": available_tables,
        "todays_reservations": todays_reservations,
        "revenue": revenue,
        "recent_bookings": recent,
    }
