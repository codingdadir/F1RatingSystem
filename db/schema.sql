CREATE TABLE drivers (
driver_id TEXT PRIMARY KEY,
name TEXT NOT NULL,
nationality TEXT NOT NULL
);

CREATE TABLE races (
race_id INTEGER PRIMARY KEY,
season INTEGER NOT NULL,
round INTEGER NOT NULL,
name TEXT NOT NULL,
circuit TEXT,
date TEXT
);

CREATE TABLE results (
result_id INTEGER PRIMARY KEY,
race_id INTEGER NOT NULL,
driver_id TEXT NOT NULL,
constructor_id TEXT,
grid_position INTEGER,
finish_position INTEGER,
points REAL,
status TEXT,

UNIQUE(race_id, driver_id),
FOREIGN KEY (race_id)   REFERENCES races(race_id),
FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

CREATE TABLE qualifying (
qual_id INTEGER PRIMARY KEY,
race_id INTEGER NOT NULL,
driver_id TEXT NOT NULL,
constructor_id TEXT,
position INTEGER,
q1_time TEXT,
q2_time TEXT,
q3_time TEXT,

UNIQUE(race_id, driver_id),
FOREIGN KEY (race_id)   REFERENCES races(race_id),
FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

CREATE TABLE pit_stops(
pit_id INTEGER PRIMARY KEY,
race_id INTEGER NOT NULL,
driver_id TEXT NOT NULL,
stop INTEGER,
duration REAL,

UNIQUE(race_id, driver_id, stop),
FOREIGN KEY (race_id)   REFERENCES races(race_id),
FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

CREATE TABLE ratings(
rating_id INTEGER PRIMARY KEY,
race_id INTEGER NOT NULL,
driver_id TEXT NOT NULL,
score REAL,
elo_delta REAL,
elo REAL,

UNIQUE(race_id, driver_id),
FOREIGN KEY (race_id)   REFERENCES races(race_id),
FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

CREATE TABLE constructor_standings (
    season          INTEGER NOT NULL,
    constructor_id  TEXT    NOT NULL,
    final_position  INTEGER,
    total_points    REAL,
    PRIMARY KEY (season, constructor_id)
);
