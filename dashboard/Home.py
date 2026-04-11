import streamlit as st

st.set_page_config(page_title="F1 Rating System", page_icon="🏠", layout="wide")

st.markdown("<h1 style='text-align: center;'>F1 Driver Rating System</h1>", unsafe_allow_html=True)

st.markdown("""
<p style='text-align: center; font-size: 18px;'>
An ELO-based rating system that ranks Formula 1 drivers based on race performance from 2006 to 2025.
</p>
""", unsafe_allow_html=True)

st.divider()

st.markdown("""
<div style='text-align: center; max-width: 700px; margin: 0 auto;'>

<h3>How It Works</h3>

<p>Drivers start with a base ELO of 1000. After each race, their rating is updated based on
finish position, positions gained or lost, qualifying performance, and DNF penalties.
Ratings accumulate over time, producing a career-long measure of driver performance.</p>

<h3>Pages</h3>

</div>
""", unsafe_allow_html=True)

_, c1, c2, _ = st.columns([3, 1, 1, 3])
with c1:
    st.page_link("pages/1_Leaderboard.py", label="Leaderboard", icon="🏆", use_container_width=True)
with c2:
    st.page_link("pages/2_Driver_Comparison.py", label="Driver Comparison", icon="🏎️", use_container_width=True)

st.markdown("""
<div style='text-align: center; max-width: 700px; margin: 0 auto;'>

<h3>Data</h3>

<p>All race data is sourced from the <a href="https://github.com/jolpica/jolpica-f1" target="_blank">Jolpica API</a> covering the 2006–2025 seasons.</p>

<hr>

<p>Built by Abdul · <a href="https://github.com/codingdadir/F1RatingSystem" target="_blank">GitHub</a></p>

</div>
""", unsafe_allow_html=True)