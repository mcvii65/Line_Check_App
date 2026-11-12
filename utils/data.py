"""NBA recent-form data with a cached API request and a sample-data fallback."""

import math
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st
from nba_api.stats.endpoints import leaguegamelog, scheduleleaguev2

from utils.teams import TEAM_ABBREVIATIONS, TEAM_NAME_BY_ABBREVIATION, TEAM_NAMES


@st.cache_data(ttl=3600, show_spinner=False)
def _load_league_game_log(season: str) -> tuple[pd.DataFrame, str | None]:
    """Fetch a league-wide game log, returning API errors for the caller to show."""
    try:
        endpoint = leaguegamelog.LeagueGameLog(
            season=season,
            season_type_all_star="Regular Season",
            player_or_team_abbreviation="T",
            timeout=20,
        )
        return endpoint.get_data_frames()[0], None
    except Exception as exc:
        return pd.DataFrame(), f"NBA.com data is temporarily unavailable ({exc})."


@st.cache_data(ttl=3600, show_spinner=False)
def _load_season_schedule(season: str) -> tuple[pd.DataFrame, str | None]:
    """Fetch the NBA season schedule and return any connection error."""
    try:
        endpoint = scheduleleaguev2.ScheduleLeagueV2(season=season, timeout=20)
        return endpoint.get_data_frames()[0], None
    except Exception as exc:
        return pd.DataFrame(), f"NBA.com schedule is temporarily unavailable ({exc})."


def _current_season() -> str:
    today = datetime.now()
    start_year = today.year if today.month >= 10 else today.year - 1
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def get_upcoming_games(
    window_hours: int = 48,
) -> tuple[list[dict[str, Any]], str | None]:
    """Return scheduled games in the next 48 hours in the user's local NBA time."""
    schedule, error = _load_season_schedule(_current_season())
    if error is not None:
        return [], error
    if schedule.empty or "gameDateTimeUTC" not in schedule:
        return [], "NBA.com did not return a usable game schedule."

    now_utc = datetime.now(timezone.utc)
    end_utc = now_utc + timedelta(hours=window_hours)
    game_times = pd.to_datetime(schedule["gameDateTimeUTC"], utc=True, errors="coerce")
    upcoming = schedule.loc[
        game_times.between(pd.Timestamp(now_utc), pd.Timestamp(end_utc))
    ].copy()
    upcoming["game_time_utc"] = game_times.loc[upcoming.index]
    upcoming = upcoming.sort_values("game_time_utc")
    local_zone = ZoneInfo("America/New_York")

    games: list[dict[str, Any]] = []
    for row in upcoming.to_dict(orient="records"):
        game_time = row["game_time_utc"].to_pydatetime().astimezone(local_zone)
        home_abbreviation = str(row.get("homeTeam_teamTricode", ""))
        away_abbreviation = str(row.get("awayTeam_teamTricode", ""))
        home_name = TEAM_NAME_BY_ABBREVIATION.get(home_abbreviation)
        away_name = TEAM_NAME_BY_ABBREVIATION.get(away_abbreviation)
        if not home_name or not away_name:
            continue
        games.append(
            {
                "id": str(row.get("gameId", "")),
                "date": game_time.date().isoformat(),
                "time": game_time.strftime("%-I:%M %p ET"),
                "datetime": game_time.isoformat(),
                "home_team": home_name,
                "home_abbreviation": home_abbreviation,
                "away_team": away_name,
                "away_abbreviation": away_abbreviation,
                "status": str(row.get("gameStatusText", "Scheduled")),
            }
        )
    return games, None


@st.cache_data(ttl=300, show_spinner=False)
def get_nba_moneyline_odds(
    api_key: str,
) -> tuple[list[dict[str, Any]], int | None, str | None]:
    """Fetch current US NBA moneyline odds and return the remaining API quota."""
    if not api_key.strip():
        return [], None, "Add ODDS_API_KEY to .streamlit/secrets.toml to load odds."

    try:
        response = requests.get(
            "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/",
            params={
                "apiKey": api_key.strip(),
                "regions": "us",
                "markets": "h2h",
                "oddsFormat": "american",
            },
            headers={"User-Agent": "LineCheck/1.0"},
            timeout=20,
        )
    except requests.Timeout:
        return [], None, "The Odds API request timed out. Try again later."
    except requests.RequestException:
        return [], None, "The Odds API could not be reached. Try again later."

    if response.status_code in (401, 403):
        return [], None, "The Odds API rejected the key. Check ODDS_API_KEY."
    if response.status_code == 429:
        return [], None, "The Odds API request limit has been reached."
    if response.status_code >= 400:
        return [], None, f"The Odds API returned HTTP {response.status_code}."
    try:
        events = response.json()
    except ValueError:
        return [], None, "The Odds API returned an unreadable response."
    remaining = response.headers.get("x-requests-remaining")

    if not isinstance(events, list):
        return [], None, "The Odds API response was not a list of games."
    try:
        requests_remaining = int(remaining) if remaining is not None else None
    except ValueError:
        requests_remaining = None
    return events, requests_remaining, None


def _canonical_team_name(name: str) -> str:
    """Normalize common city-name variants returned by odds feeds."""
    normalized = " ".join(name.lower().replace(".", "").split())
    aliases = {
        "la clippers": "los angeles clippers",
        "la lakers": "los angeles lakers",
        "ny knicks": "new york knicks",
    }
    return aliases.get(normalized, normalized)


def get_game_moneyline_bookmakers(
    events: list[dict[str, Any]], game: dict[str, Any]
) -> list[dict[str, Any]]:
    """Find bookmaker moneylines matching a scheduled game."""
    home_name = _canonical_team_name(game["home_team"])
    away_name = _canonical_team_name(game["away_team"])
    matching_event = next(
        (
            event
            for event in events
            if _canonical_team_name(str(event.get("home_team", ""))) == home_name
            and _canonical_team_name(str(event.get("away_team", ""))) == away_name
        ),
        None,
    )
    if matching_event is None:
        return []

    bookmakers: list[dict[str, Any]] = []
    for bookmaker in matching_event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market.get("key") != "h2h":
                continue
            outcomes: dict[str, int] = {}
            for outcome in market.get("outcomes", []):
                if "price" not in outcome:
                    continue
                outcome_name = _canonical_team_name(str(outcome.get("name", "")))
                if outcome_name == home_name:
                    team_name = game["home_team"]
                elif outcome_name == away_name:
                    team_name = game["away_team"]
                else:
                    continue
                outcomes[team_name] = int(round(float(outcome["price"])))
            if game["home_team"] in outcomes and game["away_team"] in outcomes:
                bookmakers.append(
                    {
                        "key": str(bookmaker.get("key", "")),
                        "name": str(bookmaker.get("title", "Sportsbook")),
                        "last_update": bookmaker.get("last_update"),
                        "odds": outcomes,
                    }
                )
    return bookmakers


def _summarize_team(
    game_log: pd.DataFrame, abbreviation: str, game_count: int
) -> dict[str, Any]:
    """Summarize the latest games for one team from a league-wide game log."""
    team_games = game_log.loc[
        game_log["TEAM_ABBREVIATION"] == abbreviation
    ].copy()
    team_games["GAME_DATE"] = pd.to_datetime(team_games["GAME_DATE"])
    team_games = team_games.sort_values("GAME_DATE", ascending=False).head(game_count)
    if team_games.empty:
        raise ValueError(f"No recent games were found for {abbreviation}.")

    opponent_points: list[float] = []
    for row in team_games.itertuples():
        opponent_rows = game_log.loc[
            (game_log["GAME_ID"] == row.GAME_ID)
            & (game_log["TEAM_ABBREVIATION"] != abbreviation),
            "PTS",
        ]
        if opponent_rows.empty:
            raise ValueError("Opponent scores were missing from the game log.")
        opponent_points.append(float(opponent_rows.iloc[0]))

    wins = int((team_games["WL"] == "W").sum())
    losses = int((team_games["WL"] == "L").sum())
    points_scored = float(team_games["PTS"].mean())
    points_allowed = sum(opponent_points) / len(opponent_points)
    return {
        "Team": TEAM_NAME_BY_ABBREVIATION[abbreviation],
        "Record": f"{wins}-{losses}",
        "Games": len(team_games),
        "Points scored": round(points_scored, 1),
        "Points allowed": round(points_allowed, 1),
        "Net rating": round(points_scored - points_allowed, 1),
        "Last played": team_games["GAME_DATE"].max().date().isoformat(),
    }


def _sample_team_summary(team_name: str, game_count: int) -> dict[str, Any]:
    """Return deterministic, explicitly illustrative stats for an NBA team."""
    team_index = TEAM_NAMES.index(team_name)
    wins = max(0, min(game_count, (game_count // 2) + ((team_index % 5) - 2)))
    points_scored = 106.0 + (team_index % 11) * 1.7
    points_allowed = 105.0 + (team_index % 7) * 1.5
    return {
        "Team": team_name,
        "Record": f"{wins}-{game_count - wins}",
        "Games": game_count,
        "Points scored": round(points_scored, 1),
        "Points allowed": round(points_allowed, 1),
        "Net rating": round(points_scored - points_allowed, 1),
    }


def get_team_comparison(
    first_team: str, second_team: str, game_count: int
) -> tuple[pd.DataFrame, bool, str | None]:
    """Return recent team form, whether it is sample data, and an optional warning."""
    raw_log, api_error = _load_league_game_log(_current_season())
    if api_error is None and not raw_log.empty:
        try:
            summaries = [
                _summarize_team(
                    raw_log, TEAM_ABBREVIATIONS[team_name], game_count
                )
                for team_name in (first_team, second_team)
            ]
            return pd.DataFrame(summaries), False, None
        except (KeyError, ValueError, TypeError) as exc:
            api_error = f"NBA.com returned incomplete recent-game data ({exc})."

    sample_data = pd.DataFrame(
        [
            _sample_team_summary(first_team, game_count),
            _sample_team_summary(second_team, game_count),
        ]
    )
    return sample_data, True, api_error or "No recent NBA.com game data was available."


def get_recent_form(team_name: str, game_count: int = 10) -> dict[str, Any]:
    """Return recent real team form or raise an informative data error."""
    if team_name not in TEAM_ABBREVIATIONS:
        raise ValueError(f"Unknown NBA team: {team_name}")
    game_log, error = _load_league_game_log(_current_season())
    if error:
        raise RuntimeError(error)
    return _summarize_team(
        game_log, TEAM_ABBREVIATIONS[team_name], game_count
    )


def estimate_matchup_probability(
    home_form: dict[str, Any],
    away_form: dict[str, Any],
    game_date: str,
) -> tuple[float, float, int, int]:
    """Estimate a preliminary home-win probability from form, rest, and home court.

    This transparent prototype heuristic is not trained or calibrated for betting.
    """
    scheduled_date = datetime.fromisoformat(game_date).date()
    home_last_game = datetime.fromisoformat(str(home_form["Last played"])).date()
    away_last_game = datetime.fromisoformat(str(away_form["Last played"])).date()
    home_rest = max(0, (scheduled_date - home_last_game).days - 1)
    away_rest = max(0, (scheduled_date - away_last_game).days - 1)
    form_difference = float(home_form["Net rating"]) - float(away_form["Net rating"])
    estimated_margin = form_difference * 0.5 + 2.0 + (home_rest - away_rest) * 0.4
    home_probability = 1 / (1 + math.exp(-estimated_margin / 12))
    home_probability = min(0.9, max(0.1, home_probability))
    return home_probability, estimated_margin, home_rest, away_rest


def probability_to_american(probability: float) -> int:
    """Convert a win probability strictly between zero and one to fair odds."""
    if not 0 < probability < 1:
        raise ValueError("Probability must be greater than 0% and less than 100%.")
    if probability >= 0.5:
        return round(-100 * probability / (1 - probability))
    return round(100 * (1 - probability) / probability)
