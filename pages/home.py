import streamlit as st

from utils.styles import render_logo

render_logo()
st.markdown('<p class="lc-kicker">Research the price. Understand the risk.</p>', unsafe_allow_html=True)
st.title("A clearer look at the line.")
st.write(
    "Line Check helps you compare sportsbook odds with your own research-based "
    "estimate of an NBA outcome. It highlights where your estimate and the market "
    "differ; it does not generate picks or guarantee results."
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
        "Start in **Edge Finder** to enter odds, your probability estimate, and a "
        "stake. Use **Team Comparison** for recent form. Log bets to review your "
        "history and performance."
    )

st.info(
    "Your probability estimate is an input, not a prediction from Line Check. "
    "Compare assumptions carefully and treat every calculation as uncertain."
)
