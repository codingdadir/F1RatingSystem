import time
from http.client import responses

import requests
from PIL.ImageChops import offset


def fetch_driver(year):
    all_drivers = []
    offset = 0

    while True:
        url = f"https://api.jolpi.ca/ergast/f1/{year}/drivers/?limit=100&offset={offset}"
        response = requests.get(url)
        data = response.json()

        total = int(data["MRData"]["total"])
        drivers = data["MRData"]["DriverTable"]["Drivers"]

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
        url = f"https://api.jolpi.ca/ergast/f1/{year}/results/?limit=100&offset={offset}"
        response = requests.get(url)
        data = response.json()

        total = int(data["MRData"]["total"])
        races = data["MRData"]["RaceTable"]["Races"]

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
        url = f"https://api.jolpi.ca/ergast/f1/{year}/qualifying/?limit=100&offset={offset}"
        response = requests.get(url)
        data = response.json()

        total = int(data["MRData"]["total"])
        qualies = data["MRData"]["RaceTable"]["Races"]

        all_qualifying.extend(qualies)
        time.sleep(0.3)

        if len(all_qualifying) >= total:
            break

        offset += 100

    return all_qualifying

def fetch_pitstops(year):
    all_pits = []
    races = fetch_results(year)

    for race in races:
        round_number = race["round"]
        url = f"https://api.jolpi.ca/ergast/f1/{year}/{round_number}/pitstops/?limit=100&offset=0"
        response = requests.get(url)
        data = response.json()

        pits = data["MRData"]["RaceTable"]["Races"][0]["PitStops"]
        all_pits.extend(pits)

        time.sleep(0.3)
    return all_pits