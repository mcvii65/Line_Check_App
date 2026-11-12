import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from utils.calculations import expected_value, implied_probability
from utils.data import (
    estimate_matchup_probability,
    get_game_moneyline_bookmakers,
    get_nba_moneyline_odds,
    get_recent_form,
    get_upcoming_games,
    probability_to_american,
)
from utils.styles import matchup_card_html

st.title("Edge Finder")
st.markdown(
    '<p class="lc-kicker">Pick a game. Check the price. Understand the context.</p>',
    unsafe_allow_html=True,
)
st.write(
    "Browse the next 48 hours of NBA games, choose a matchup, and compare a "
    "sportsbook moneyline with Line Check's early form-based estimate."
)
with st.spinner("Loading the next 48 hours of NBA games..."):
    games, schedule_error = get_upcoming_games()

if schedule_error:
    st.error(f"Could not load the NBA schedule. {schedule_error}")
elif not games:
    st.info("There are no scheduled NBA games in the next 48 hours.")
else:
    try:
        odds_api_key = str(st.secrets["ODDS_API_KEY"])
    except (KeyError, StreamlitSecretNotFoundError):
        odds_api_key = ""
    with st.spinner("Checking available sportsbook moneylines..."):
        odds_events, odds_remaining, odds_error = get_nba_moneyline_odds(
            odds_api_key
        )
    if odds_error:
        st.info(
            f"{odds_error} You can still enter a sportsbook price manually "
            "when you analyze a game."
        )
    elif odds_remaining is not None:
        st.caption(f"The Odds API requests remaining until reset: {odds_remaining}")

    st.subheader(f"Upcoming slate · {len(games)} games")
    st.caption("NBA schedule data · times shown in Eastern Time")

    odds_by_game = {
        game["id"]: get_game_moneyline_bookmakers(odds_events, game)
        for game in games
    }
    for row_start in range(0, len(games), 2):
        columns = st.columns(2)
        for column, game in zip(columns, games[row_start : row_start + 2]):
            with column:
                st.markdown(matchup_card_html(game), unsafe_allow_html=True)
                books = odds_by_game[game["id"]]
                if books:
                    best_home = max(
                        books,
                        key=lambda book: (
                            1 + book["odds"][game["home_team"]] / 100
                            if book["odds"][game["home_team"]] > 0
                            else 1 + 100 / abs(book["odds"][game["home_team"]])
                        ),
                    )
                    best_away = max(
                        books,
                        key=lambda book: (
                            1 + book["odds"][game["away_team"]] / 100
                            if book["odds"][game["away_team"]] > 0
                            else 1 + 100 / abs(book["odds"][game["away_team"]])
                        ),
                    )
                    st.caption(
                        f"Best listed: {game['away_abbreviation']} "
                        f"{best_away['odds'][game['away_team']]:+d} · "
                        f"{game['home_abbreviation']} "
                        f"{best_home['odds'][game['home_team']]:+d}"
                    )
                else:
                    st.caption("Moneyline not currently listed")
                if st.button(
                    "Analyze matchup",
                    key=f"analyze_{game['id']}",
                    width="stretch",
                ):
                    st.session_state["selected_game_id"] = game["id"]

    selected_game_id = st.session_state.get("selected_game_id")
    selected_game = next(
        (game for game in games if game["id"] == selected_game_id), None
    )
    if selected_game is None and games:
        selected_game = games[0]
        st.session_state["selected_game_id"] = selected_game["id"]

    if selected_game is not None:
        st.divider()
        st.subheader(
            f"{selected_game['away_team']} at {selected_game['home_team']}"
        )
        st.write(
            f"{selected_game['date']} · {selected_game['time']} · "
            "Moneyline analysis"
        )

        model_error = None
        try:
            with st.spinner("Reviewing recent team form and rest..."):
                home_form = get_recent_form(selected_game["home_team"], 10)
                away_form = get_recent_form(selected_game["away_team"], 10)
                (
                    home_probability,
                    estimated_margin,
                    home_rest,
                    away_rest,
                ) = estimate_matchup_probability(
                    home_form, away_form, selected_game["date"]
                )
        except (RuntimeError, ValueError, KeyError, TypeError) as exc:
            model_error = str(exc)
            home_form = away_form = None
            home_probability = None

        side_options = [
            selected_game["away_team"],
            selected_game["home_team"],
        ]
        selected_side = st.radio(
            "Which side's moneyline are you checking?",
            side_options,
            horizontal=True,
            key=f"side_{selected_game['id']}",
        )

        selected_bookmakers = odds_by_game[selected_game["id"]]
        if selected_bookmakers:
            selected_book_name = st.selectbox(
                "Sportsbook",
                options=[book["name"] for book in selected_bookmakers],
                help="Moneylines are retrieved from The Odds API and cached for five minutes.",
                key=f"book_{selected_game['id']}",
            )
            selected_book = next(
                book
                for book in selected_bookmakers
                if book["name"] == selected_book_name
            )
            market_odds = selected_book["odds"][selected_side]
            opposite_side = (
                selected_game["home_team"]
                if selected_side == selected_game["away_team"]
                else selected_game["away_team"]
            )
            book_col, other_col, stake_col = st.columns(3)
            book_col.metric("Selected side moneyline", f"{market_odds:+d}")
            other_col.metric(
                f"{opposite_side} moneyline",
                f"{selected_book['odds'][opposite_side]:+d}",
            )
            with stake_col:
                stake = st.number_input(
                    "Example stake ($)",
                    min_value=0.0,
                    value=25.0,
                    step=5.0,
                    key=f"stake_{selected_game['id']}",
                )
            book_updated = selected_book.get("last_update")
            if book_updated:
                st.caption(f"Bookmaker prices last updated: {book_updated}")
        else:
            st.warning(
                "No bookmaker prices are currently available for this matchup. "
                "Enter the price you see at your sportsbook."
            )
            odds_column, stake_column = st.columns(2)
            with odds_column:
                market_odds = st.number_input(
                    "Sportsbook American odds",
                    min_value=-1000,
                    max_value=1000,
                    value=-110,
                    step=5,
                    help="Enter the selected team's moneyline from your sportsbook.",
                    key=f"odds_{selected_game['id']}_{selected_side}",
                )
            with stake_column:
                stake = st.number_input(
                    "Example stake ($)",
                    min_value=0.0,
                    value=25.0,
                    step=5.0,
                    key=f"stake_{selected_game['id']}",
                )

        if model_error:
            st.warning(
                "Recent form is unavailable, so Line Check will not invent a fair "
                f"price. {model_error}"
            )
        elif -100 < int(market_odds) < 100:
            st.error("American odds must be at least +100 or at most -100.")
        elif home_form is not None and away_form is not None:
            selected_probability = (
                home_probability
                if selected_side == selected_game["home_team"]
                else 1 - home_probability
            )
            raw_market_probability = implied_probability(int(market_odds))
            if selected_bookmakers:
                opposite_probability = implied_probability(
                    selected_book["odds"][opposite_side]
                )
                market_probability = raw_market_probability / (
                    raw_market_probability + opposite_probability
                )
            else:
                market_probability = raw_market_probability
            fair_odds = probability_to_american(selected_probability)
            try:
                ev = expected_value(stake, selected_probability, int(market_odds))
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.markdown(
                    '<div class="lc-model-note"><strong>Experimental form estimate</strong> '
                    "This simple, uncalibrated prototype uses the teams' last 10 "
                    "games, home-court advantage, and days of rest. It does not yet "
                    "include injuries, player matchups, or a trained prediction model.</div>",
                    unsafe_allow_html=True,
                )
                metric_columns = st.columns(4)
                metric_columns[0].metric(
                    "Line Check estimate", f"{selected_probability:.1%}"
                )
                metric_columns[1].metric(
                    "Sportsbook implied", f"{market_probability:.1%}"
                )
                metric_columns[2].metric("Fair moneyline", f"{fair_odds:+d}")
                metric_columns[3].metric("Example EV", f"${ev:+.2f}")

                if ev > 0:
                    st.success(
                        "The entered price is above break-even under this early "
                        "form estimate. This is a model comparison, not a pick or "
                        "a claim that the wager is safe."
                    )
                elif ev < 0:
                    st.warning(
                        "The entered price is below break-even under this early "
                        "form estimate. The estimate itself is experimental."
                    )
                else:
                    st.info(
                        "This price is approximately break-even under the current "
                        "form estimate."
                    )

                form_columns = st.columns(2)
                form_columns[0].markdown(
                    f"**{selected_game['away_team']}** · last 10: "
                    f"{away_form['Record']} · net points: "
                    f"{away_form['Net rating']:+.1f} · rest: {away_rest} day(s)"
                )
                form_columns[1].markdown(
                    f"**{selected_game['home_team']}** · last 10: "
                    f"{home_form['Record']} · net points: "
                    f"{home_form['Net rating']:+.1f} · rest: {home_rest} day(s)"
                )
                st.caption(
                    f"Prototype estimated margin: home team by {estimated_margin:+.1f} "
                    "points. Raw implied probability does not remove sportsbook margin."
                )
