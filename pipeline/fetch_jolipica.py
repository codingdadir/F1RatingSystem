import time
import requests

def safe_get(url):
    while True:
        response = requests.get(url)
        if response.status_code == 429:
            for i in range(120, 0, -1):
                print(f"Rate limited, retrying in {i}s...", end="\r")
                time.sleep(1)
        else:
            return response

def fetch_drivers(year):
    all_drivers = []
    offset = 0

    while True:
        url = f"https://api.jolpi.ca/ergast/f1/{year}/drivers/?limit=100&offset={offset}"
        response = safe_get(url)
        data = response.json()

        total = int(data["MRData"]["total"])
        drivers = data["MRData"]["DriverTable"]["Drivers"]

        if not drivers:
            break

        all_drivers.extend(drivers)
        time.sleep(0.3)

        if len(all_drivers) >= total:
            break

        offset += 100

    return all_drivers

def fetch_results(year):
    all_races = []
    offset = 0

    while True:
        print(f"Fetching {year} offset {offset}...")
        url = f"https://api.jolpi.ca/ergast/f1/{year}/results/?limit=100&offset={offset}"
        response = safe_get(url)

        data = response.json()

        total = int(data["MRData"]["total"])
        races = data["MRData"]["RaceTable"]["Races"]
        if not races:
            break

        all_races.extend(races)
        time.sleep(0.3)

        if len(all_races) >= total:
            break

        offset += 100

    return all_races

def fetch_qualifying(year):
    all_qualifying = []
    offset = 0

    while True:
        print(f"Fetching {year} offset {offset}...")
        url = f"https://api.jolpi.ca/ergast/f1/{year}/qualifying/?limit=100&offset={offset}"
        response = safe_get(url)
        data = response.json()
        total = int(data["MRData"]["total"])
        qualies = data["MRData"]["RaceTable"]["Races"]

        if not qualies:
            break

        all_qualifying.extend(qualies)
        time.sleep(0.3)

        if len(all_qualifying) >= total:
            break

        offset += 100

    return all_qualifying

def fetch_pitstops(year, races):
    all_pits = []

    for race in races:
        round_number = race["round"]
        print(f"Fetching {year} round {round_number} pit stops...")
        url = f"https://api.jolpi.ca/ergast/f1/{year}/{round_number}/pitstops/?limit=100&offset=0"
        response = safe_get(url)
        data = response.json()

        races_data = data["MRData"]["RaceTable"]["Races"]
        if not races_data:
            continue


        race_obj = data["MRData"]["RaceTable"]["Races"][0]
        all_pits.append(race_obj)

        time.sleep(0.3)
    return all_pits

def fetch_constructor_standing(year):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/constructorstandings/"
    print(f"Fetching {year} standings")
    response = safe_get(url)
    data = response.json()

    standings_lists = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings_lists:
        return []

    return standings_lists[0]["ConstructorStandings"]

def fetch_driver_standings(year):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/driverstandings/"
    response = safe_get(url)

    data = response.json()

    standings_list = data["MRData"]["StandingsTable"]["StandingsLists"]

    if not standings_list:
        return []

    return standings_list[0]["DriverStandings"]

