# F1 Driver Rating System

A data science project by Abdulkadir Abdalla

## Project Summary

This project builds a custom driver rating system for Formula 1, designed to evaluate driver performance more fairly and accurately than championship points alone.

Championship points are heavily influenced by the car — a driver in a dominant car will score points almost regardless of their individual performance, while a driver in a backmarker car may drive brilliantly and score nothing. This system attempts to strip away the car's influence and rate drivers on what they actually control: how well they qualify relative to their teammate, how much they gain or lose positions in the race, and how often they make mistakes that end their race.

The rating is built on four components — qualifying performance vs teammate, race finish vs teammate, positions gained or lost, and a DNF penalty that distinguishes between driver errors and mechanical failures. Each component is normalised and weighted, then fed into an ELO-style system that tracks driver ratings across every race from 2006 to 2025. Constructor championship standings are used to provide season context, so a strong result in a backmarker car is valued more highly than the same result in a dominant car.

The project is end-to-end: a Python pipeline fetches data from the Jolpica F1 API, stores it in a structured SQLite database, runs the rating model, and presents the results in an interactive Streamlit dashboard.

---

## Tech Stack

- **Python** — data pipeline, scoring model, ELO system
- **SQLite** — local database storing race results, qualifying, pit stops, constructor standings, and ratings
- **Jolpica API** — successor to the Ergast F1 API, provides historical race data from 2006–2025
- **scikit-learn** — linear regression for model validation
- **Streamlit** — interactive dashboard (in progress)

---

## Scoring Model

Each driver receives a composite score per race made up of four components:

| Component | Weight | Description |
|---|---|---|
| Finish position | 0.35 | Normalised finish position with teammate comparison and season context multiplier |
| Positions gained/lost | 0.25 | Exponential decay weighting — front positions worth more than midfield |
| Qualifying performance | 0.25 | Same structure as finish score — normalised position vs teammate vs constructor average |
| DNF penalty | 0.15 | Flat penalty for driver-fault DNFs (Accident, Collision, Spun off, Collision damage) |

### Season context multiplier

To normalise for car quality, each finish and qualifying score is adjusted by a context multiplier based on how much the driver over or underperformed their constructor's average result for that season. A backmarker driver finishing P6 receives a larger boost than a top team driver finishing P6.

### ELO layer

After computing composite scores for all drivers in a race, drivers are ranked and assigned symmetric ELO deltas. Every driver starts at ELO = 1000 at the beginning of a chosen range. ELO accumulates race by race, producing a career rating trajectory for every driver.

---

## Validation

The model was validated by running linear regression of average per-season composite scores against actual championship standings across 466 driver-season pairs from 2006–2025.

**R² = 0.66 on held-out test data**

This means the model explains 66% of the variance in championship outcomes — well above the 0.6 threshold set as the target. The remaining variance is largely attributable to car performance, which the model deliberately attempts to normalise away. A perfect R² would indicate the model was simply predicting car quality rather than driver skill.

The train/test gap is small (0.683 train vs 0.662 test), confirming the model generalises well and is not overfitting.

---

## Leaderboard (2006–2025, minimum 40 races)

| Rank | Driver | ELO |
|---|---|---|
| 1 | Hamilton | 3677 |
| 2 | Verstappen | 3305 |
| 3 | Alonso | 3036 |
| 4 | Vettel | 2733 |
| 5 | Rosberg | 2246 |
| 6 | Leclerc | 2010 |
| 7 | Norris | 1877 |
| 8 | Raikkonen | 1821 |
| 9 | Bottas | 1721 |
| 10 | Webber | 1583 |

---

## Known Limitations

- Some mechanical DNFs may be caused by driver error (e.g. kerb strikes causing suspension failure). The model classifies strictly by reported retirement status.
- Drivers with fewer than 40 races are excluded from the leaderboard due to high ELO variance with limited data.
- The qualifying format changed in 2006 to the current Q1/Q2/Q3 system — data before 2006 is not used.

---

## Setup

```bash
git clone https://github.com/yourusername/f1-rating-system
cd f1-rating-system
pip install -r requirements.txt
python pipeline/load_db.py        # fetch and load data
python model/runner.py            # calculate ratings
python model/validate.py          # run validation
streamlit run dashboard/Home.py    # launch dashboard
```