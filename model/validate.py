from pipeline.fetch_jolipica import fetch_driver_standings
import sqlite3
import os
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))

conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def create_standings_dict(start, end):
    standings_dict = {}
    for i in range(start, end+1):
        standings = fetch_driver_standings(i)
        for standing in standings:
            pos_text = standing.get("positionText", None)
            if pos_text and pos_text.isdigit():
                position = int(pos_text)
            else:
                continue
            driver_id = standing["Driver"]["driverId"]
            standings_dict[(driver_id, i)] = position

    return standings_dict

def get_avg_scores(start, end):
    table = f"ratings_{start}_{end}"
    cursor.execute(f"""
        SELECT t.driver_id, rc.season, AVG(t.score) AS avg_score
        FROM {table} t
        JOIN races rc ON t.race_id = rc.race_id
        GROUP BY t.driver_id, rc.season
    """)
    rows = cursor.fetchall()
    return {(row["driver_id"], row["season"]): row["avg_score"] for row in rows}

def align_data(avg_scores, standings):
    x = []
    y = []
    for key in avg_scores:
        if key in standings:
            x.append(avg_scores[key])
            y.append(standings[key])

    return x, y

def run_regression(x, y):
    X = np.array(x).reshape(-1, 1)
    y = np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    r2_train = model.score(X_train, y_train)
    r2_test  = model.score(X_test, y_test)

    print(f"R² train: {r2_train:.3f}")
    print(f"R² test:  {r2_test:.3f}")

    return model


if __name__ == "__main__":
    start, end = 2006, 2025

    print("Fetching standings...")
    standings = create_standings_dict(start, end)

    print("Getting average scores...")
    avg_scores = get_avg_scores(start, end)

    print("Aligning data...")
    x, y = align_data(avg_scores, standings)

    print(f"Aligned {len(x)} driver-season pairs")

    print("Running regression...")
    model = run_regression(x, y)