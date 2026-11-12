# Line Check

## Student Name
Michael Vaccaro II

## App Description
Line Check is an NBA analytics and decision-support app. It puts upcoming
matchups, a sportsbook's moneyline, and recent-game context together so users
can examine how a market price compares with a transparent, early form estimate.
Line Check does not generate guaranteed picks; its current estimate is an
experimental heuristic, not a calibrated prediction model.

## Intended Users
NBA fans and casual-to-serious bettors looking for data-driven reasoning, along
with students and analysts interested in sports analytics.

## Current Features
- Home/About page explaining the app and how to use it.
- Edge Finder lists NBA games scheduled in the next 48 hours, lets users select
  a matchup and view The Odds API's US sportsbook moneylines when configured.
  Without an API key or listed price, users can enter odds manually. It compares
  the price with an experimental estimate based on each team's last 10 games,
  home-court advantage, and rest days, then shows fair odds and example expected
  value.
- Team-color cards use custom abbreviation badges. They are not official team
  logo artwork.
- Team Comparison shows recent records, points scored/allowed, and a simple net
  rating for two selected teams. It uses NBA.com Stats data when available and
  clearly labels its illustrative sample-data fallback.
- Log a Bet saves an upcoming matchup, entered sportsbook price, experimental
  model estimate, and notes to Supabase.
- Bet History filters records by result and date, allows pending bets to be
  settled, and reports win rate, profit/loss, ROI, and bankroll over time.
- Dark hardwood-inspired theme, shared navigation, inline logo, and responsible
  use reminders.

## Planned Features
- Injury impact summaries.
- Rest, travel, and schedule factors.
- Opponent-adjusted win-streak quality.
- Player-vs-defender matchup analysis.
- User login and authentication with secure per-user records.
- A calibrated, tested game probability model with richer player and schedule
  context.

## Setup

### 1. Install dependencies

From the project directory, create and activate a virtual environment, then
install the packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate`.

### 2. Configure Supabase

1. Create a project at [supabase.com](https://supabase.com/).
2. In the Supabase SQL Editor, open and run [`supabase_setup.sql`](./supabase_setup.sql)
   to create the `public.bets` table.
3. In the Supabase project settings, copy the Project URL and an API key
   (anon/publishable key for this prototype).
4. Copy [`.streamlit/secrets.toml.example`](./.streamlit/secrets.toml.example)
   to `.streamlit/secrets.toml` and replace the placeholders:

   ```toml
   SUPABASE_URL = "https://your-project-id.supabase.co"
   SUPABASE_KEY = "your-supabase-anon-or-publishable-key"
   ODDS_API_KEY = "your-the-odds-api-key"
   ```

   The actual `secrets.toml` is ignored by Git. Never commit real credentials.
   The username field is only a record filter, not authentication or security.
5. Create an account with [The Odds API](https://the-odds-api.com/) and add its
   API key as `ODDS_API_KEY` in the same local secrets file. The app requests
   US NBA head-to-head moneylines, caches them for five minutes, and displays
   the provider's remaining request quota when available. API plans and quotas
   can change; check the provider's current pricing before relying on a plan.
   Without a valid key, you can still enter odds manually.

### 3. Run Line Check

```bash
streamlit run app.py
```

The NBA.com Stats API may be temporarily unavailable; Team Comparison then
displays clearly labeled sample data, while Edge Finder and bet logging report
that a live form estimate is unavailable. The Odds API key is optional; without
it, enter sportsbook odds manually. The early form estimate is experimental and
should not be treated as betting advice. Bet logging and history require valid
Supabase credentials and the SQL table setup.

## Responsible Use

Line Check is for education and analysis only, not betting advice. It does not
guarantee outcomes. Please bet responsibly, only where betting is legal, and
only if you are of legal betting age.
