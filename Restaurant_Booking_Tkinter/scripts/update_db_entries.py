import sqlite3, os
p = os.path.join(os.path.dirname(__file__), '..', 'database', 'restaurant_booking.db')
conn = sqlite3.connect(p)
cur = conn.cursor()
# Update admin full name
cur.execute("UPDATE Users SET full_name = ? WHERE username = ?", ("Prakash Mehra", 'admin'))
# Update menu items by id
updates = [
    ("Samosa (2 pcs)", 120.0, "Crispy potato-filled pastry served with chutney", 1),
    ("Butter Chicken", 420.0, "Classic Punjabi butter chicken with naan or rice", 2),
    ("Gulab Jamun (3 pcs)", 150.0, "Soft milk dumplings soaked in rose syrup", 3),
    ("Masala Chai", 60.0, "Spiced Indian tea brewed with milk", 4),
]
for name, price, desc, item_id in updates:
    cur.execute("UPDATE MenuItems SET name = ?, price = ?, description = ? WHERE id = ?", (name, price, desc, item_id))
conn.commit()
print('DB updates applied')
conn.close()
