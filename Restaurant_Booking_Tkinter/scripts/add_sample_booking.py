import sqlite3, os
from datetime import datetime
p = os.path.join(os.path.dirname(__file__), '..', 'database', 'restaurant_booking.db')
conn = sqlite3.connect(p)
cur = conn.cursor()
# Create a sample booking (if none exists)
cur.execute("SELECT COUNT(*) FROM Bookings")
if cur.fetchone()[0] == 0:
    today = datetime.now().strftime('%Y-%m-%d')
    cur.execute("INSERT INTO Bookings (customer_name, table_id, booking_date, booking_time, guests, status) VALUES (?, ?, ?, ?, ?, ?)",
                ('Test Guest', 1, today, '19:00', 2, 'Confirmed'))
    conn.commit()
    print('Sample booking created')
else:
    print('Bookings already present')
conn.close()
