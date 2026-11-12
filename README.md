# Line Check

## Student Name
Michael Vaccaro II

## App Description
Line Check is an NBA analytics and decision-support app. It helps users compare
a sportsbook's American odds with their own research-based estimate of a game's
outcome, explore recent team form, and track their bets. Line Check does not
generate picks or guarantee results; its calculations depend on the assumptions
and estimates entered by the user.

## Intended Users
NBA fans and casual-to-serious bettors looking for data-driven reasoning, along
with students and analysts interested in sports analytics.

## Current Features
- Home/About page explaining the app and how to use it.
- Edge Finder converts American odds to raw implied probability, compares that
  probability with a user's estimate, calculates expected value, and displays
  full- and half-Kelly reference stakes.
- Team Comparison shows recent records, points scored/allowed, and a simple net
  rating for two selected teams. It uses NBA.com Stats data when available and
  clearly labels its illustrative sample-data fallback.
- Log a Bet saves a user's matchup, bet details, probability estimate, and notes
  to Supabase.
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
   ```

   The actual `secrets.toml` is ignored by Git. Never commit real credentials.
   The username field is only a record filter, not authentication or security.

### 3. Run Line Check

```bash
streamlit run app.py
```

The NBA.com Stats API may be temporarily unavailable; Team Comparison then
displays clearly labeled sample data. Bet logging and history require valid
Supabase credentials and the SQL table setup.

## Responsible Use

Line Check is for education and analysis only, not betting advice. It does not
guarantee outcomes. Please bet responsibly, only where betting is legal, and
only if you are of legal betting age.
