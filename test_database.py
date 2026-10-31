
from database.db import get_connection

connection = get_connection()

cursor = connection.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

tables = cursor.fetchall()

print("\nDATABASE TABLES")
print("--------------------")

for table in tables:
    print(table["name"])

connection.close()
