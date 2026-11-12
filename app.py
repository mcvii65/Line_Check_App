import streamlit as st

from utils.styles import apply_global_styles, render_page_footer, render_sidebar

st.set_page_config(
    page_title="Line Check",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()
render_sidebar()

navigation = st.navigation(
    {
        "Home": [
            st.Page("pages/home.py", title="Home / About", icon="🏠", default=True),
        ],
        "Analyze": [
            st.Page("pages/edge_finder.py", title="Edge Finder", icon="📈"),
            st.Page("pages/team_comparison.py", title="Team Comparison", icon="🏀"),
        ],
        "My Bets": [
            st.Page("pages/log_bet.py", title="Log a Bet", icon="✍️"),
            st.Page(
                "pages/bet_history.py",
                title="Bet History & Performance",
                icon="📋",
            ),
        ],
    }
)

navigation.run()
render_page_footer()
