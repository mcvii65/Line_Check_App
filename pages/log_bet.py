from datetime import date

import streamlit as st

from utils.teams import TEAM_NAMES
from utils.database import save_bet

st.title("Log a Bet")
st.write(
    "Save a wager to your Supabase bet history. Your sidebar username tags the "
    "record but is not a secure account."
)

with st.form("log_bet_form", clear_on_submit=True):
    bet_date = st.date_input("Bet date", value=date.today())
    team_col, opponent_col = st.columns(2)
    with team_col:
        selected_team = st.selectbox("Team you are betting on", TEAM_NAMES)
    with opponent_col:
        opponent = st.selectbox(
            "Opponent",
            TEAM_NAMES,
            index=1,
        )
    bet_type = st.selectbox(
        "Bet type",
        ["Moneyline", "Spread", "Over/Under", "Other"],
        help="For this first version, the saved record tracks the selected odds and outcome.",
    )
    odds_col, stake_col, probability_col = st.columns(3)
    with odds_col:
        odds = st.number_input(
            "American odds",
            min_value=-1000,
            max_value=1000,
            value=-110,
            step=5,
            help="Enter -110, +150, or another valid American price.",
        )
    with stake_col:
        stake = st.number_input(
            "Stake ($)",
            min_value=0.01,
            value=25.0,
            step=5.0,
        )
    with probability_col:
        user_probability = st.slider(
            "Your estimated win probability",
            min_value=1,
            max_value=99,
            value=55,
            format="%d%%",
        )
    notes = st.text_area("Notes (optional)", max_chars=2000)
    submitted = st.form_submit_button("Save bet", type="primary")

if submitted:
    if selected_team == opponent:
        st.error("Choose two different teams for the matchup.")
    elif -100 < int(odds) < 100:
        st.error("American odds must be at least +100 or at most -100.")
    else:
        username = str(st.session_state.get("username", "guest")).strip() or "guest"
        bet_record = {
            "username": username,
            "bet_date": bet_date.isoformat(),
            "matchup": f"{selected_team} vs {opponent}",
            "bet_type": bet_type,
            "odds": int(odds),
            "stake": float(stake),
            "user_probability": user_probability / 100,
            "result": "pending",
            "profit": None,
            "notes": notes.strip() or None,
        }
        try:
            save_bet(bet_record)
        except Exception as exc:
            st.error(
                "Could not save your bet. Check your Supabase credentials, table "
                f"setup, and network connection. Details: {exc}"
            )
        else:
            st.success("Bet saved. It will appear in Bet History & Performance.")

st.caption(
    "Saved user probabilities are stored as decimal values (for example, 55% as 0.55)."
)
