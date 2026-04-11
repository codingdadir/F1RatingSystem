import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from model.runner import get_final_leaderboard
import sqlite3, pandas as pd, plotly.express as px
st.set_page_config(page_title="Leaderboard", layout="wide")


# ── Leaderboard selectors ──────────────────────────────────────────────
options = range(2006, 2026)
col1, col2 = st.columns(2)

start_year = col1.selectbox("Select Start Year", options)
valid_end = range(start_year, 2026)
default_end = st.session_state.get("end_year", 2025)

if default_end < start_year:
    default_end = start_year

end_year = col2.selectbox("Select End Year", valid_end, index=list(valid_end).index(default_end))
st.session_state["end_year"] = end_year

min_races = st.slider("Minimum Races", 1, 100, 40)

@st.cache_data
def get_leaderboard(start_year, end_year, min_races):
    rows = get_final_leaderboard(start_year, end_year, min_races)
    return pd.DataFrame(rows, columns=["driver_id", "elo"])


_, centre, _ = st.columns([2, 1, 2])
with centre:
    run_leaderboard = st.button("Run Leaderboard", type="primary", width="stretch")


if run_leaderboard:
    leaderboard = get_leaderboard(start_year, end_year, min_races)
    leaderboard["Rank"] = range(1, len(leaderboard) + 1)
    st.dataframe(leaderboard, hide_index=True)
