import streamlit as st
import os
import sqlite3
import pandas as pd
from model.runner import get_final_leaderboard


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@st.cache_data
def get_max_races(start, end):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))
    table = f"ratings_{start}_{end}"
    cursor = conn.cursor()
    cursor.execute(f"SELECT MAX(cnt) FROM (SELECT COUNT(*) as cnt FROM {table} GROUP BY driver_id)")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 100

@st.cache_data
def get_driver_info():
    conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))
    df = pd.read_sql_query("SELECT driver_id, name, nationality FROM drivers", conn)
    conn.close()
    return df

@st.cache_data
def get_leaderboard(start_year, end_year, min_races):
    rows = get_final_leaderboard(start_year, end_year, min_races)
    return pd.DataFrame(rows, columns=["driver_id", "elo"])

NATIONALITY_CODES = {
    "American": "us", "Argentine": "ar", "Australian": "au",
    "Austrian": "at", "Belgian": "be", "Brazilian": "br",
    "British": "gb", "Canadian": "ca", "Chinese": "cn",
    "Colombian": "co", "Danish": "dk", "Dutch": "nl",
    "Finnish": "fi", "French": "fr", "German": "de",
    "Indian": "in", "Indonesian": "id", "Italian": "it",
    "Japanese": "jp", "Mexican": "mx", "Monegasque": "mc",
    "New Zealander": "nz", "Polish": "pl", "Portuguese": "pt",
    "Russian": "ru", "Spanish": "es", "Swedish": "se",
    "Swiss": "ch", "Thai": "th", "Venezuelan": "ve",
}

def flag_url(nationality):
    code = NATIONALITY_CODES.get(nationality, "un")
    return f"https://flagsapi.com/{code.upper()}/flat/32.png"


@st.cache_data
def get_elo_history(driver_ids, start, end):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))
    table = f"ratings_{start}_{end}"
    placeholders = ",".join("?" * len(driver_ids))
    query = f"""
        SELECT t.driver_id, t.elo, rc.season, rc.round, rc.name
        FROM {table} t
        JOIN races rc ON t.race_id = rc.race_id
        WHERE t.driver_id IN ({placeholders})
        ORDER BY rc.season, rc.round
    """
    df = pd.read_sql_query(query, conn, params=driver_ids)
    conn.close()
    return df

@st.cache_data
def get_comparison_info(drivers):
    driver_stats = {d: {} for d in drivers}

    conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))
    placeholders = ",".join("?" * len(drivers))
    query = f"""
                SELECT driver_id,
                       COUNT(*) as race_starts,
                       SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) as wins,
                       SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) as podiums,
                       ROUND(AVG(finish_position), 1) as avg_finish,
                       SUM(CASE WHEN status != 'Finished' AND status NOT LIKE '+%' THEN 1 ELSE 0 END) as dnfs
                FROM results
                WHERE driver_id IN ({placeholders})
                GROUP BY driver_id
                """
    cursor = conn.cursor()
    cursor.execute(query, drivers)
    results = cursor.fetchall()

    # Poles
    pole_query = f"""
        SELECT driver_id, COUNT(*) as poles
        FROM qualifying
        WHERE position = 1 AND driver_id IN ({placeholders})
        GROUP BY driver_id
    """
    cursor.execute(pole_query, drivers)
    pole_results = cursor.fetchall()

    # Peak and current ELO (from full range table)
    elo_query = f"""
        SELECT driver_id, 
               ROUND(MAX(elo), 0) as peak_elo,
               ROUND((SELECT t2.elo FROM ratings_2006_2025 t2 
                      JOIN races r2 ON t2.race_id = r2.race_id
                      WHERE t2.driver_id = t.driver_id 
                      ORDER BY r2.season DESC, r2.round DESC LIMIT 1), 0) as current_elo
        FROM ratings_2006_2025 t
        WHERE driver_id IN ({placeholders})
        GROUP BY driver_id
    """
    cursor.execute(elo_query, drivers)
    elo_results = cursor.fetchall()

    # Championships
    champ_query = f"""
        SELECT driver_id, championships
        FROM drivers
        WHERE driver_id IN ({placeholders})
    """
    cursor.execute(champ_query, drivers)
    champ_results = cursor.fetchall()

    conn.close()

    for row in results:
        driver_stats[row[0]] = {"race_starts": row[1], "wins": row[2], "podiums": row[3], "avg_finish": row[4],
                                "dnfs": row[5]}

    for row in pole_results:
        driver_stats[row[0]]["poles"] = row[1]

    for row in elo_results:
        driver_stats[row[0]]["peak_elo"] = row[1]
        driver_stats[row[0]]["current_elo"] = row[2]

    for row in champ_results:
        driver_stats[row[0]]["championships"] = row[1]

    # Fill in zeros for drivers with no poles/championships
    for d in drivers:
        driver_stats[d].setdefault("poles", 0)
        driver_stats[d].setdefault("championships", 0)

    return driver_stats

lower_is_better = ["Avg Finish", "DNFs"]

def highlight_best(row):
    if row.name in lower_is_better:
        best = row.min()
    else:
        best = row.max()
    return ["background-color: #1a472a" if v == best else "" for v in row]

