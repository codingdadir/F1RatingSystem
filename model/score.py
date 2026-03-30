import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))

conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def get_races_in_range(start, end=None):
    if start < 2006:
        print("Invalid range")
        return []
    if end is not None and (end > 2025 or end < start):
        print("Invalid range")
        return []

    if end is None:
        cursor.execute("""SELECT race_id, season, round, name, circuit, date FROM races WHERE season = ?
                       ORDER BY round ASC""", (start,))
    else:
        cursor.execute("""SELECT race_id, season, round, name, circuit, date FROM races WHERE season BETWEEN ? and ?
                       ORDER BY season ASC, round ASC""", (start, end))

    return cursor.fetchall()


def get_constructor_averages(season):

    if season < 2006 or season > 2025:
        print("Invalid Season")
        return

    cursor.execute("""SELECT r.constructor_id,
        AVG(r.finish_position) AS avg_finish,
        AVG(q.position)        AS avg_quali
        FROM results r
        JOIN races rc ON r.race_id = rc.race_id
        LEFT JOIN qualifying q
               ON r.race_id = q.race_id AND r.driver_id = q.driver_id
        WHERE rc.season = ?
          AND r.finish_position IS NOT NULL
        GROUP BY r.constructor_id""", (season,))

    rows = cursor.fetchall()

    return {row["constructor_id"]: {"avg_finish": row["avg_finish"], "avg_quali": row["avg_quali"]} for row in rows}


def get_race_data(race_id):
    if race_id < 200601 or race_id > 202599:
        print("Invalid Race ID")
        return []

    cursor.execute("""SELECT r.driver_id, r.constructor_id,
        r.grid_position, r.finish_position,
        r.status, q.position AS quali_position
        FROM results r
        LEFT JOIN qualifying q
        ON r.race_id = q.race_id AND r.driver_id = q.driver_id
        WHERE r.race_id = ?""",(race_id,))

    rows = cursor.fetchall()

    drivers = {row["driver_id"]: {
        "constructor_id": row["constructor_id"],
        "quali_position": row["quali_position"],
        "grid_position": row["grid_position"],
        "finish_position": row["finish_position"],
        "status": row["status"]
    } for row in rows}

    teammates = {}
    for row in rows:
        cid = row["constructor_id"]
        if cid not in teammates:
            teammates[cid] = []
        teammates[cid].append(row["driver_id"])

    return drivers, teammates





