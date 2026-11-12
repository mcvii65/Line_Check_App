import streamlit as st

from utils.styles import render_logo

render_logo()
st.markdown(
    '<p class="lc-kicker">Research the price. Understand the risk.</p>',
    unsafe_allow_html=True,
)
st.title("Find the story behind the line.")
st.write(
    "Line Check brings upcoming NBA matchups, sportsbook prices, and recent-game "
    "context together so you can examine how the market price compares with a "
    "transparent, early research estimate. It is decision support—not a pick "
    "generator—and it never guarantees outcomes."
)

left, right = st.columns(2)
with left:
    st.subheader("Who it's for")
    st.write(
        "NBA fans and casual-to-serious bettors looking for data-driven reasoning, "
        "plus students and analysts interested in sports analytics."
    )
with right:
    st.subheader("How to use Line Check")
    st.write(
        "Open **Edge Finder**, select a game from the upcoming slate, choose a "
        "moneyline side, and enter the sportsbook price you see. Review the early "
        "form estimate before deciding what the comparison means to you."
    )

st.info(
    "The current form estimate is experimental and uncalibrated. Live sportsbook "
    "moneylines are available when an Odds API key is configured; otherwise, you "
    "can enter a price manually. Factors such as injuries are not included yet."
)
