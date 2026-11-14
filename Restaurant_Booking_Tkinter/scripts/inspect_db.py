import sqlite3
import os
p = os.path.join(os.path.dirname(__file__), '..', 'database', 'restaurant_booking.db')
conn = sqlite3.connect(p)
conn.row_factory = sqlite3.Row
print('Users:')
for r in conn.execute('SELECT id, username, full_name FROM Users'):
    print(dict(r))
print('\nMenu Categories:')
for r in conn.execute('SELECT id, name FROM MenuCategories'):
    print(dict(r))
print('\nMenu Items:')
for r in conn.execute('SELECT id, name, price, description FROM MenuItems'):
    print(dict(r))
conn.close()
