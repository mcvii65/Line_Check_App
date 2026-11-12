import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from utils.data import (
    estimate_matchup_probability,
    get_game_moneyline_bookmakers,
    get_nba_moneyline_odds,
    get_recent_form,
    get_upcoming_games,
)
from utils.database import save_bet

st.title("Log a Bet")
st.write(
    "Record a bet on an upcoming matchup. Line Check saves its experimental "
    "form estimate with the sportsbook price you enter."
)

games, schedule_error = get_upcoming_games()
if schedule_error:
    st.error(f"Could not load upcoming games. {schedule_error}")
    st.stop()
if not games:
    st.info("There are no games scheduled in the next 48 hours to log.")
    st.stop()

try:
    odds_api_key = str(st.secrets["ODDS_API_KEY"])
except (KeyError, StreamlitSecretNotFoundError):
    odds_api_key = ""
odds_events, _, _ = get_nba_moneyline_odds(odds_api_key)
odds_by_game = {
    game["id"]: get_game_moneyline_bookmakers(odds_events, game)
    for game in games
}

game_by_label = {
    f"{game['date']} · {game['time']} · {game['away_team']} at {game['home_team']}": game
    for game in games
}

with st.form("log_bet_form", clear_on_submit=True):
    selected_label = st.selectbox("Upcoming matchup", list(game_by_label))
    selected_game = game_by_label[selected_label]
    selected_side = st.radio(
        "Team selected",
        [selected_game["away_team"], selected_game["home_team"]],
        horizontal=True,
    )
    bet_type = st.selectbox("Bet type", ["Moneyline"])
    selected_bookmakers = odds_by_game[selected_game["id"]]
    if selected_bookmakers:
        selected_book_name = st.selectbox(
            "Sportsbook",
            options=[book["name"] for book in selected_bookmakers],
        )
        selected_book = next(
            book for book in selected_bookmakers if book["name"] == selected_book_name
        )
        odds = selected_book["odds"][selected_side]
        st.metric("Moneyline from selected sportsbook", f"{odds:+d}")
    else:
        st.info("No sportsbook prices available for this game; enter odds manually.")
        odds = None
    odds_column, stake_column = st.columns(2)
    if odds is None:
        with odds_column:
            odds = st.number_input(
                "Sportsbook American odds",
                min_value=-1000,
                max_value=1000,
                value=-110,
                step=5,
                help="Enter the selected team's moneyline price from your sportsbook.",
            )
    with stake_column:
        stake = st.number_input(
            "Stake ($)",
            min_value=0.01,
            value=25.0,
            step=5.0,
        )
    notes = st.text_area("Notes (optional)", max_chars=2000)
    submitted = st.form_submit_button("Save bet", type="primary")

if submitted:
    if -100 < int(odds) < 100:
        st.error("American odds must be at least +100 or at most -100.")
    else:
        try:
            home_form = get_recent_form(selected_game["home_team"], 10)
            away_form = get_recent_form(selected_game["away_team"], 10)
            home_probability, _, _, _ = estimate_matchup_probability(
                home_form, away_form, selected_game["date"]
            )
        except (RuntimeError, ValueError, KeyError, TypeError) as exc:
            st.error(f"Could not calculate the experimental form estimate. {exc}")
        else:
            user_probability = (
                home_probability
                if selected_side == selected_game["home_team"]
                else 1 - home_probability
            )
            opponent = (
                selected_game["away_team"]
                if selected_side == selected_game["home_team"]
                else selected_game["home_team"]
            )
            username = str(st.session_state.get("username", "guest")).strip() or "guest"
            bet_record = {
                "username": username,
                "bet_date": selected_game["date"],
                "matchup": f"{selected_side} vs {opponent}",
                "bet_type": bet_type,
                "odds": int(odds),
                "stake": float(stake),
                "user_probability": user_probability,
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
                st.success(
                    f"Bet saved with an experimental Line Check estimate of "
                    f"{user_probability:.1%}. This estimate is not calibrated."
                )

st.caption(
    "Bet logging stores a form-based model estimate. The current Supabase schema "
    "uses the legacy `user_probability` column for this value."
)
