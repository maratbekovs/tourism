import sqlite3

def print_users():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()

print_users()