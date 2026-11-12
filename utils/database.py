"""Supabase connection and bet-record operations."""

from typing import Any

import streamlit as st
from supabase import Client, create_client

from utils.calculations import american_to_decimal


def get_supabase_client() -> Client:
    """Create a Supabase client from Streamlit secrets."""
    if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
        raise ValueError(
            "Supabase is not configured. Add SUPABASE_URL and SUPABASE_KEY "
            "to .streamlit/secrets.toml."
        )
    url = str(st.secrets["SUPABASE_URL"]).strip()
    key = str(st.secrets["SUPABASE_KEY"]).strip()
    if not url or not key or "your-" in url.lower() or "your-" in key.lower():
        raise ValueError(
            "Supabase credentials are placeholders. Add your project URL and key "
            "to .streamlit/secrets.toml."
        )
    return create_client(url, key)


def save_bet(bet: dict[str, Any]) -> None:
    """Insert a bet record into Supabase."""
    client = get_supabase_client()
    client.table("bets").insert(bet).execute()


def fetch_bets(username: str) -> list[dict[str, Any]]:
    """Read the current user's records from Supabase."""
    client = get_supabase_client()
    response = (
        client.table("bets")
        .select("*")
        .eq("username", username)
        .order("bet_date", desc=True)
        .execute()
    )
    return response.data


def settle_bet(bet: dict[str, Any], result: str) -> None:
    """Update a pending bet result and its net profit."""
    if result not in {"Won", "Lost", "Push"}:
        raise ValueError("Result must be Won, Lost, or Push.")
    stake = float(bet["stake"])
    if result == "Won":
        profit = stake * (american_to_decimal(int(bet["odds"])) - 1)
    elif result == "Lost":
        profit = -stake
    else:
        profit = 0.0
    client = get_supabase_client()
    (
        client.table("bets")
        .update({"result": result.lower(), "profit": profit})
        .eq("id", bet["id"])
        .eq("username", bet["username"])
        .execute()
    )
