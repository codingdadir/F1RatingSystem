import sqlite3
import os
from model.elo import initialise_elo, compute_elo_delta, update_elo
from model.score import get_races_in_range, get_constructor_averages, get_race_data, compute_finish_score, compute_quali_score, compute_positions_score, compute_composite, compute_dnf_penalty, get_all_drivers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_ratings_table(start_year, end_year):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    table = f"ratings_{start_year}_{end_year}"

    cursor.execute(f"DROP TABLE IF EXISTS {table}")

    cursor.execute(f"""CREATE TABLE {table} 
    (
    race_id INTEGER NOT NULL,
    driver_id TEXT NOT NULL, 
    score REAL,
    elo_delta REAL,
    elo REAL,
    PRIMARY KEY (race_id, driver_id)
    )
    """)

    conn.commit()
    conn.close()


def save_ratings(table, race_id, composite, deltas, elo):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    for driver_id in composite:
        cursor.execute(
            f"INSERT INTO {table} VALUES (?, ?, ?, ?, ?)",
            (
                race_id,
                driver_id,
                composite.get(driver_id, 0),
                deltas.get(driver_id, 0),
                elo.get(driver_id, 1000)
            )
        )
    conn.commit()
    conn.close()


def calculate_ratings(start, end):
    races = get_races_in_range(start, end)
    elo = initialise_elo(get_all_drivers(start, end))

    current_season = None
    constructor_avgs = {}

    table = f"ratings_{start}_{end}"
    conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    if cursor.fetchone():
        print(f"Skipping {start}-{end}, already exists")
        conn.close()
        return
    conn.close()

    create_ratings_table(start, end)

    for race in races:
        print(f"Processing {race['season']} round {race['round']}...")

        if race["season"] != current_season:
            constructor_avgs = get_constructor_averages(race["season"])
            current_season = race["season"]

        drivers, teammates = get_race_data(race["race_id"])

        finish = compute_finish_score(drivers, teammates, constructor_avgs)
        positions = compute_positions_score(drivers)
        quali = compute_quali_score(drivers, teammates, constructor_avgs)
        dnf = compute_dnf_penalty(drivers)
        composite = compute_composite(drivers, finish, positions, quali, dnf)

        deltas = compute_elo_delta(composite)
        elo = update_elo(elo, deltas)

        save_ratings(table, race["race_id"], composite, deltas, elo)

    print(f"Ratings calculated for {start}-{end}")


def get_final_leaderboard(start, end, min_races):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    table = f"ratings_{start}_{end}"
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    if not cursor.fetchone():
        conn.close()
        return []
    table = f"ratings_{start}_{end}"
    cursor.execute(f"""
        SELECT driver_id, elo
        FROM {table} t1
        WHERE race_id = (
            SELECT MAX(race_id) FROM {table} t2
            WHERE t2.driver_id = t1.driver_id
        )
        AND driver_id IN (
            SELECT driver_id FROM {table}
            GROUP BY driver_id
            HAVING COUNT(*) >= ?
        )
        ORDER BY elo DESC
    """, (min_races,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# def precompute_all_ranges():
#     years = range(2006, 2026)
#     total = sum(1 for s in years for e in years if e >= s)
#     count = 0
#     for start in years:
#         for end in years:
#             if end >= start:
#                 count += 1
#                 print(f"Computing {start}-{end} ({count}/{total})...")
#                 calculate_ratings(start, end)
#     print("All ranges computed.")
