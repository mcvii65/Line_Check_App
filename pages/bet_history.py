from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.database import fetch_bets, settle_bet

st.title("Bet History & Performance")
st.write(
    "Review records saved under your sidebar username, filter the table, and "
    "settle pending wagers. Supabase credentials and the `bets` table are required."
)

username = str(st.session_state.get("username", "guest")).strip() or "guest"
try:
    records = fetch_bets(username)
except Exception as exc:
    st.error(
        "Could not load bet history. Check your Supabase credentials, run "
        f"supabase_setup.sql, and confirm your network connection. Details: {exc}"
    )
    records = []

if records:
    bets = pd.DataFrame(records)
    bets["bet_date"] = pd.to_datetime(bets["bet_date"]).dt.date

    filters_left, filters_right = st.columns(2)
    with filters_left:
        selected_results = st.multiselect(
            "Filter by result",
            options=["pending", "won", "lost", "push"],
            default=["pending", "won", "lost", "push"],
            format_func=str.title,
        )
    with filters_right:
        date_range = st.date_input(
            "Filter by bet date",
            value=(date.today() - timedelta(days=365), date.today()),
            help="Choose a start and end date.",
        )

    filtered = bets.loc[bets["result"].isin(selected_results)].copy()
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered.loc[
            filtered["bet_date"].between(start_date, end_date)
        ]

    settled = filtered.loc[filtered["result"].isin(["won", "lost", "push"])].copy()
    decided = settled.loc[settled["result"].isin(["won", "lost"])]
    total_profit = pd.to_numeric(settled["profit"], errors="coerce").fillna(0).sum()
    total_staked = pd.to_numeric(settled["stake"], errors="coerce").fillna(0).sum()
    win_rate = (
        (decided["result"] == "won").mean() if not decided.empty else 0.0
    )
    roi = total_profit / total_staked if total_staked else 0.0

    total_col, win_col, profit_col, roi_col = st.columns(4)
    total_col.metric("Total bets", len(filtered))
    win_col.metric(
        "Win rate",
        f"{win_rate:.1%}" if not decided.empty else "—",
        help="Wins divided by won and lost bets; pushes and pending bets are excluded.",
    )
    profit_col.metric("Settled profit/loss", f"${total_profit:+.2f}")
    roi_col.metric(
        "ROI",
        f"{roi:.1%}" if total_staked else "—",
        help="Settled profit/loss divided by stake on settled bets.",
    )

    if not filtered.empty:
        display = filtered.copy()
        if "user_probability" in display:
            display["user_probability"] = (
                pd.to_numeric(display["user_probability"], errors="coerce") * 100
            ).map(lambda value: f"{value:.0f}%" if pd.notna(value) else "—")
        st.dataframe(
            display[
                [
                    "bet_date",
                    "matchup",
                    "bet_type",
                    "odds",
                    "stake",
                    "user_probability",
                    "result",
                    "profit",
                    "notes",
                ]
            ],
            hide_index=True,
            width="stretch",
            column_config={
                "bet_date": st.column_config.DateColumn("Date"),
                "stake": st.column_config.NumberColumn("Stake", format="$%.2f"),
                "profit": st.column_config.NumberColumn("Profit/Loss", format="$%.2f"),
                "user_probability": st.column_config.TextColumn("Your estimate"),
                "result": st.column_config.TextColumn("Result"),
            },
        )
    else:
        st.info("No bets match these filters.")

    pending = bets.loc[bets["result"] == "pending"].to_dict(orient="records")
    if pending:
        st.subheader("Settle a pending bet")
        labels = {
            str(bet["id"]): (
                f'{bet["bet_date"]} · {bet["matchup"]} · ${float(bet["stake"]):.2f}'
            )
            for bet in pending
        }
        selected_id = st.selectbox(
            "Pending bet",
            options=list(labels),
            format_func=lambda bet_id: labels[bet_id],
        )
        result = st.radio(
            "Outcome",
            ["Won", "Lost", "Push"],
            horizontal=True,
        )
        if st.button("Update result", type="primary"):
            selected_bet = next(bet for bet in pending if str(bet["id"]) == selected_id)
            try:
                settle_bet(selected_bet, result)
            except Exception as exc:
                st.error(f"Could not update this bet. Details: {exc}")
            else:
                st.success("Bet result updated.")
                st.rerun()

    st.subheader("Bankroll over time")
    starting_bankroll = st.number_input(
        "Starting bankroll ($)",
        min_value=0.0,
        value=1000.0,
        step=100.0,
        help="This starting amount is used for this chart and is not saved to Supabase.",
    )
    if not settled.empty:
        chart_data = settled.sort_values(["bet_date", "created_at"]).copy()
        chart_data["profit"] = (
            pd.to_numeric(chart_data["profit"], errors="coerce").fillna(0)
        )
        chart_data["Bankroll"] = starting_bankroll + chart_data["profit"].cumsum()
        chart = px.line(
            chart_data,
            x="bet_date",
            y="Bankroll",
            markers=True,
            title="Estimated balance after each settled bet",
        )
        chart.update_traces(line_color="#e87524")
        chart.update_layout(yaxis_title="Bankroll ($)", xaxis_title="Bet date")
        st.plotly_chart(chart, width="stretch")
    else:
        st.info("Settle a bet to see your bankroll-over-time chart.")
else:
    st.info(
        "No saved bets found for this username yet. Add Supabase credentials, "
        "run the setup SQL, then record a bet to get started."
    )
