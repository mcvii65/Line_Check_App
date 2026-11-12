"""NBA recent-form data with a cached API request and a sample-data fallback."""

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st
from nba_api.stats.endpoints import leaguegamelog

from utils.teams import TEAM_NAMES, TEAM_ABBREVIATIONS


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


def _current_season() -> str:
    today = datetime.now()
    start_year = today.year if today.month >= 10 else today.year - 1
    return f"{start_year}-{str(start_year + 1)[-2:]}"


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

    points_by_game = game_log.groupby("GAME_ID")["PTS"].apply(list).to_dict()
    opponent_points: list[float] = []
    for row in team_games.itertuples():
        scores = points_by_game.get(row.GAME_ID, [])
        other_scores = [score for score in scores if score != row.PTS]
        if not other_scores:
            raise ValueError("Opponent scores were missing from the game log.")
        opponent_points.append(float(other_scores[0]))

    wins = int((team_games["WL"] == "W").sum())
    losses = int((team_games["WL"] == "L").sum())
    points_scored = float(team_games["PTS"].mean())
    points_allowed = sum(opponent_points) / len(opponent_points)
    return {
        "Team": dict((abbreviation_, name) for name, abbreviation_ in TEAM_ABBREVIATIONS.items())[
            abbreviation
        ],
        "Record": f"{wins}-{losses}",
        "Games": len(team_games),
        "Points scored": round(points_scored, 1),
        "Points allowed": round(points_allowed, 1),
        "Net rating": round(points_scored - points_allowed, 1),
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
