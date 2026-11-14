import os
import sqlite3
import tempfile
import unittest

from database import initialize_database, validate_booking_slot


class DesktopAppDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_initialize_database_creates_required_tables(self):
        initialize_database(self.db_path)
        conn = sqlite3.connect(self.db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {row[0] for row in tables}
        expected = {
            "Users",
            "Customers",
            "Tables",
            "Bookings",
            "MenuCategories",
            "MenuItems",
            "Reviews",
        }
        self.assertTrue(expected.issubset(table_names))
        conn.close()

    def test_validate_booking_slot_rejects_duplicate_booking(self):
        initialize_database(self.db_path)
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO Tables (name, capacity, status) VALUES (?, ?, ?)",
            ("A1", 4, "Available"),
        )
        conn.execute(
            "INSERT INTO Bookings (customer_name, table_id, booking_date, booking_time, guests, status) VALUES (?, ?, ?, ?, ?, ?)",
            ("Alice", 1, "2026-07-10", "19:00", 4, "Confirmed"),
        )
        conn.commit()
        self.assertFalse(validate_booking_slot(conn, 1, "2026-07-10", "19:00"))
        self.assertTrue(validate_booking_slot(conn, 1, "2026-07-10", "20:00"))
        conn.close()


if __name__ == "__main__":
    unittest.main()
