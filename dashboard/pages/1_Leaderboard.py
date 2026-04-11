import sys
import os
import plotly.express as px


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from dashboard.utils import get_max_races, get_leaderboard, flag_url, get_driver_info, get_elo_history

st.set_page_config(page_title="Leaderboard", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.markdown("<h1 style='text-align: center;'>Leaderboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Select a year range and minimum race threshold, then click <b>Run Leaderboard</b> to generate ELO rankings.</p>", unsafe_allow_html=True)
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

max_races = get_max_races(start_year, end_year)
min_races = st.slider("Minimum Races", 1, max_races, min(40, max_races))

# ── Leaderboard ──────────────────────────────────────────────

_, centre, _ = st.columns([1.75, 1, 1.75])
with centre:
    run_leaderboard = st.button("Run Leaderboard", type="primary", width="stretch")


_, centre1, _ = st.columns([1,  2, 1])
with centre1:
    if run_leaderboard:
        st.session_state["lb_start"] = start_year
        st.session_state["lb_end"] = end_year
        st.session_state["lb_min_races"] = min_races
        st.session_state["leaderboard_data"] = True

if "leaderboard_data" in st.session_state:
    s = st.session_state["lb_start"]
    e = st.session_state["lb_end"]
    m = st.session_state["lb_min_races"]

    driver_info = get_driver_info()
    leaderboard = get_leaderboard(s, e, m)

    leaderboard["Rank"] = range(1, len(leaderboard) + 1)
    leaderboard = leaderboard.merge(driver_info, on="driver_id", how="left")
    leaderboard["elo"] = leaderboard["elo"].round(0)
    driver_ids = leaderboard["driver_id"].tolist()
    leaderboard = leaderboard.rename(columns={"name": "Driver", "nationality": "Nationality", "elo": "ELO"})
    leaderboard["Flag"] = leaderboard["Nationality"].apply(flag_url)
    leaderboard = leaderboard[["Rank", "Flag", "Driver", "ELO"]]
    leaderboard["Rank"] = range(1, len(leaderboard) + 1)

    # ── Centered table + slider ──
    _, centre2, _ = st.columns([1, 2, 1])
    with centre2:
        st.dataframe(leaderboard, hide_index=True,
                     column_config={
                        "Rank": st.column_config.NumberColumn(width="small"),
                        "Flag": st.column_config.ImageColumn("Nation", width=0.25),
                        "Driver": st.column_config.TextColumn(width="medium"),
                        "ELO": st.column_config.NumberColumn(width="small"),
                        },
                     width="stretch",
                     )

        if len(driver_ids) > 1:
            top_xids = st.slider("Show Top 'X' Drivers", 1, len(driver_ids), min(10, len(driver_ids)))
        else:
            top_xids = 1

    # ── Full-width chart ──
    top_10_ids = tuple(driver_ids[:top_xids])
    history = get_elo_history(top_10_ids, s, e)
    history = history.sort_values(["season", "round"])
    history = history.merge(driver_info[["driver_id", "name"]].rename(columns={"name": "Driver Name"}),
                            on="driver_id", how="left")
    history["Race"] = history["season"].astype(str) + " R" + history["round"].astype(str)

    season_starts = history.drop_duplicates(subset="season", keep="first")["Race"].tolist()

    fig = px.line(history, x="Race", y="elo", color="Driver Name",
                  line_shape="spline")
    fig.update_layout(
        height=850,
        title=dict(text="ELO Over Time", font=dict(size=40), xanchor="center", x=0.5),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),

    )
    fig.update_traces(line=dict(width=1.5), hovertemplate="%{y:.0f}<extra>%{fullData.name}</extra>")
    fig.update_xaxes(
        categoryorder="array",
        categoryarray=history["Race"].unique().tolist(),
        tickvals=season_starts,
        ticktext=[r.split(" ")[0] for r in season_starts],
        tickangle=45,
    )
    st.plotly_chart(fig, width="stretch")

    st.session_state["leaderboard_data"] = True
    st.session_state["driver_ids"] = driver_ids