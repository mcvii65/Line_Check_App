import plotly.graph_objects as go
import streamlit as st

from utils.data import get_team_comparison
from utils.teams import TEAM_NAMES

st.title("Team Comparison")
st.write(
    "Compare recent scoring and results for two teams. NBA.com data may be "
    "temporarily unavailable; any fallback figures are labeled sample data."
)

team_left, team_right = st.columns(2)
with team_left:
    first_team = st.selectbox("First team", TEAM_NAMES, index=1)
with team_right:
    second_team = st.selectbox("Second team", TEAM_NAMES, index=0)

game_count = st.radio(
    "Recent games",
    options=[5, 10, 20],
    format_func=lambda count: f"Last {count}",
    horizontal=True,
    help="Choose the number of the team's most recent regular-season games.",
)

if first_team == second_team:
    st.warning("Choose two different teams to compare.")
else:
    with st.spinner("Loading recent NBA team form..."):
        comparison, is_sample, data_message = get_team_comparison(
            first_team, second_team, game_count
        )

    if is_sample:
        st.warning(
            f"Showing **sample data, not live team statistics**. {data_message}"
        )
    else:
        st.caption("Source: NBA.com Stats team game log.")

    st.dataframe(comparison, hide_index=True, width="stretch")

    chart = go.Figure()
    chart.add_bar(
        name="Points scored",
        x=comparison["Team"],
        y=comparison["Points scored"],
        marker_color="#e87524",
    )
    chart.add_bar(
        name="Points allowed",
        x=comparison["Team"],
        y=comparison["Points allowed"],
        marker_color="#f6bd60",
    )
    chart.update_layout(
        title=f"Average points per game (last {game_count})",
        barmode="group",
        yaxis_title="Points",
        height=360,
        margin=dict(t=55, b=35, l=35, r=20),
    )
    st.plotly_chart(chart, width="stretch")

st.caption(
    "Net rating here is average points scored minus average points allowed; it "
    "is a simple recent-form measure, not a full possession-adjusted rating."
)
