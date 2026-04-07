import sqlite3
import os
import math


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
        return None

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


def compute_finish_score(drivers, teammates, constructor_avgs, k=1):
    did_not_start = {
        driver_id: data for driver_id, data in drivers.items()
        if data["grid_position"] is None or data["status"] == "Did not start"
    } # Drivers who did not start
    started = {
        driver_id: data for driver_id, data in drivers.items()
        if driver_id not in did_not_start
    } # Drivers who started
    DNF_STATUSES = {"Accident", "Collision", "Spun off", "Collision damage"} # DNF Statuses

    n = len(started) # Number of drivers who started the race

    scores = {}

    for driver, data in started.items():
        finish = data["finish_position"]
        raw = (n - 2 * finish + 1) / (n-1)

        constructor = data["constructor_id"]
        teammate = None
        context = None
        teammate_delta = 0

        for t in teammates[constructor]: # finds a drivers teamamte
            if t != driver:
                teammate = t

        if teammate in started and drivers[teammate]["status"] not in DNF_STATUSES and data["status"] not in DNF_STATUSES: # checks if drivers teamate finishes race
            teammate_delta = started[teammate]["finish_position"] - finish

        if constructor not in constructor_avgs:
            context = 1
        else:
            expected = constructor_avgs[constructor]["avg_finish"]
            overperf = expected - finish
            context = 1 + (overperf / n)

        scores[driver] = context * (k * raw + teammate_delta)

    return scores


def compute_positions_score(drivers, k=5):
    did_not_start = {
        driver_id: data for driver_id, data in drivers.items()
        if data["grid_position"] is None or data["status"] == "Did not start"
    }  # Drivers who did not start
    started = {
        driver_id: data for driver_id, data in drivers.items()
        if driver_id not in did_not_start
    }  # Drivers who started

    scores = {}

    for driver, data in started.items():
        start = data["grid_position"]
        finish = data["finish_position"]

        if finish is None or start is None:
            scores[driver] = 0
            continue

        if start == 0:
            start = len(started) + 1

        if finish < start:
            score = sum(math.exp(-p / k) for p in range(finish, start))
        elif finish > start:
            score = -sum(math.exp(-p / k) for p in range(start, finish))
        else:
            if finish <= 10:
                score = math.exp(-finish / k)
            else:
                score = 0

        scores[driver] = score


    return scores


def compute_quali_score(drivers, teammates, constructor_avgs, k=10):
    n = len(drivers) # Number of drivers who started the race
    scores = {}

    for driver, data in drivers.items():
        finish = data["quali_position"]

        if finish is None:
            scores[driver] = 0
            continue

        raw = (n - 2 * finish + 1) / (n-1)

        constructor = data["constructor_id"]
        teammate = None
        context = None
        teammate_delta = 0

        for t in teammates[constructor]: # finds a drivers teamamte
            if t != driver:
                teammate = t

        if teammate and teammate in drivers and drivers[teammate]["quali_position"] is not None and data["quali_position"] is not None:
            teammate_delta = drivers[teammate]["quali_position"] - finish

        if constructor not in constructor_avgs:
            context = 1
        else:
            expected = constructor_avgs[constructor]["avg_quali"]
            if expected is None:
                context = 1
            else:
                overperf = expected - finish
                context = 1 + (overperf / n)

        scores[driver] = context * (k * raw + teammate_delta)

        if finish <= 10:
            scores[driver] += math.exp(-finish / k)

    return scores


def compute_dnf_penalty(drivers, X=0.5):
    DRIVER_FAULT_STATUSES = {"Accident", "Collision", "Spun off", "Collision damage"}
    scores = {}
    for driver, data in drivers.items():
        if data["status"] in DRIVER_FAULT_STATUSES:
            scores[driver] = -X
        else:
            scores[driver] = 0

    return scores


def compute_composite(drivers, finish_scores, positions_scores, quali_scores, dnf_scores, weights=(0.35, 0.25, 0.25, 0.15)):
    w1, w2, w3, w4 = weights  # (0.35, 0.25, 0.25, 0.15)
    final_scores = {}
    for driver in drivers:
        finish_score = finish_scores.get(driver, 0)
        positions_score = positions_scores.get(driver, 0)
        quali_score = quali_scores.get(driver, 0)
        dnf_score = dnf_scores.get(driver, 0)

        final_scores[driver] = (
            w1 * finish_score +
            w2 * positions_score +
            w3 * quali_score +
            w4 * dnf_score
        )

    return final_scores


def get_all_drivers(start_year, end_year):
    cursor.execute("""
        SELECT DISTINCT r.driver_id 
        FROM results r
        JOIN races rc ON r.race_id = rc.race_id
        WHERE rc.season BETWEEN ? AND ?
    """, (start_year, end_year))
    return [row["driver_id"] for row in cursor.fetchall()]
