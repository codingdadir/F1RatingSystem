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
