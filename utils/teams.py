"""NBA team names and abbreviations used by the app."""

NBA_TEAMS: tuple[tuple[str, str], ...] = (
    ("Atlanta Hawks", "ATL"),
    ("Boston Celtics", "BOS"),
    ("Brooklyn Nets", "BKN"),
    ("Charlotte Hornets", "CHA"),
    ("Chicago Bulls", "CHI"),
    ("Cleveland Cavaliers", "CLE"),
    ("Dallas Mavericks", "DAL"),
    ("Denver Nuggets", "DEN"),
    ("Detroit Pistons", "DET"),
    ("Golden State Warriors", "GSW"),
    ("Houston Rockets", "HOU"),
    ("Indiana Pacers", "IND"),
    ("Los Angeles Clippers", "LAC"),
    ("Los Angeles Lakers", "LAL"),
    ("Memphis Grizzlies", "MEM"),
    ("Miami Heat", "MIA"),
    ("Milwaukee Bucks", "MIL"),
    ("Minnesota Timberwolves", "MIN"),
    ("New Orleans Pelicans", "NOP"),
    ("New York Knicks", "NYK"),
    ("Oklahoma City Thunder", "OKC"),
    ("Orlando Magic", "ORL"),
    ("Philadelphia 76ers", "PHI"),
    ("Phoenix Suns", "PHX"),
    ("Portland Trail Blazers", "POR"),
    ("Sacramento Kings", "SAC"),
    ("San Antonio Spurs", "SAS"),
    ("Toronto Raptors", "TOR"),
    ("Utah Jazz", "UTA"),
    ("Washington Wizards", "WAS"),
)

TEAM_NAMES = tuple(team[0] for team in NBA_TEAMS)
TEAM_ABBREVIATIONS = {name: abbreviation for name, abbreviation in NBA_TEAMS}
