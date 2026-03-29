import sqlite3
from fetch_jolipica import fetch_results, fetch_drivers, fetch_qualifying, fetch_pitstops
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(BASE_DIR, "db", "database.db"))
cursor = conn.cursor()


years = [1997]

for year in years:
    drivers = fetch_drivers(year)
    races = fetch_results(year)
    qualis = fetch_qualifying(year)
    pits = fetch_pitstops(year, races)

    for driver in drivers:
        driver_id = driver["driverId"]
        name = driver["givenName"] + " " + driver["familyName"]
        nationality = driver.get("nationality", None)

        cursor.execute("INSERT OR IGNORE INTO drivers VALUES (?, ?, ?)", (driver_id, name, nationality))

    for race in races:
        season = int(str(race["season"]))
        race_round = int(str(race["round"]))
        race_id = int(str(race["season"]) + str(race["round"]).zfill(2))
        race_name = race["raceName"]
        circuit = race["Circuit"]["circuitName"]
        date = race["date"]

        cursor.execute("INSERT OR IGNORE INTO races VALUES (?, ?, ?, ?, ?, ?)", (race_id, season,
                                                                                 race_round, race_name, circuit,
                                                                                 date))

        for result in race["Results"]:
            result_id = None
            driver_id = result["Driver"]["driverId"]
            grid_position = int(result["grid"]) if result.get("grid") else None
            finish_position = int(result["position"])
            points = float(result["points"])
            status = result.get("status", None)

            cursor.execute("INSERT OR IGNORE INTO results VALUES (?, ?, ?, ?, ?, ?, ?)", (result_id,
                                                                                       race_id, driver_id,
                                                                                       grid_position,finish_position,
                                                                                       points, status))

    for race in qualis:
        race_id = int(str(race["season"]) + str(race["round"]).zfill(2))
        for quali in race["QualifyingResults"]:

            qual_id = None
            driver_id = quali["Driver"]["driverId"]
            quali_position = int(quali["position"]) if quali.get("position") else None
            q1 = quali["Q1"] if quali.get("Q1") else None
            q2 = quali["Q2"] if quali.get("Q2") else None
            q3 = quali["Q3"] if quali.get("Q3") else None

            cursor.execute("INSERT OR IGNORE INTO qualifying VALUES (?, ?, ?, ?, ?, ?, ?)", (qual_id, race_id,
                                                                                          driver_id, quali_position,
                                                                                          q1, q2, q3))

    for race in pits:
        race_id = int(str(race["season"]) + str(race["round"]).zfill(2))
        for pit in race["PitStops"]:
            pit_id = None
            driver_id = pit["driverId"]
            stop = pit["stop"]
            duration = pit["duration"]

            cursor.execute("INSERT OR IGNORE INTO pit_stops VALUES (?, ?, ?, ?, ?)", (pit_id, race_id, driver_id,
                                                                      stop, duration))

    conn.commit()
    print(f"{year} ✅")




conn.close()

