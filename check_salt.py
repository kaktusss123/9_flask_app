"""
Тут видно, что хеши для одинаковых паролей, но разных юзеров разные.
Значит, соль в виде username работает.
"""
import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()

cur.execute("SELECT * FROM users")
for i in cur.fetchall():
    print(i)

