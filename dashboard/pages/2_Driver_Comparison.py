import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dashboard.utils import get_driver_info, get_comparison_info, highlight_best

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Driver Comparison", layout="wide")

all_names = get_driver_info()["name"].tolist()

num_drivers = st.slider("Number of Drivers", 2, 5, 2)

selected_drivers = []
cols = st.columns(num_drivers)
for i, col in enumerate(cols):
    with col:
        current_val = st.session_state.get(f"driver_{i}", None)
        available = [n for n in all_names if n not in selected_drivers or n == current_val]
        driver = st.selectbox(f"Driver {i+1}", available,
                              key=f"driver_{i}",
                              index=None, placeholder="Search for a driver...")
        selected_drivers.append(driver)

driver_info = get_driver_info()
name_to_id = dict(zip(driver_info["name"], driver_info["driver_id"]))

valid_drivers = [name_to_id[d] for d in selected_drivers if d is not None]

# Deduplicate
seen = set()
unique_drivers = []
unique_names = []
for did, name in zip(valid_drivers, [d for d in selected_drivers if d is not None]):
    if did not in seen:
        seen.add(did)
        unique_drivers.append(did)
        unique_names.append(name)

if unique_drivers:
    stats = get_comparison_info(unique_drivers)

    stat_labels = [
        ("Race Starts", "race_starts"),
        ("Wins", "wins"),
        ("Podiums", "podiums"),
        ("Pole Positions", "poles"),
        ("Championships", "championships"),
        ("Avg Finish", "avg_finish"),
        ("DNFs", "dnfs"),
        ("Peak ELO", "peak_elo"),
        ("Current ELO", "current_elo"),
    ]

    table_data = {}
    for label, key in stat_labels:
        values = [stats[did].get(key, 0) for did in unique_drivers]
        if key == "avg_finish":
            table_data[label] = values
        else:
            table_data[label] = [int(v) for v in values]

    df = pd.DataFrame(table_data, index=unique_names).T
    styled_df = df.style.apply(highlight_best, axis=1).format(
        {col: lambda x: f"{x:.1f}" if isinstance(x, float) and x != int(x) else f"{int(x)}" for col in df.columns}
    )
    st.dataframe(styled_df, width="stretch")