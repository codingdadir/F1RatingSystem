import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))
cursor = conn.cursor()

all_status = cursor.execute("SELECT status FROM results")
statuses = []
for status in all_status:
    if status[0][0] == "+" and status[0] not in statuses:
        statuses.append(status[0])

print(statuses)