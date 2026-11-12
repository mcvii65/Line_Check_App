"""Odds, expected-value, and Kelly-criterion calculations."""


def _validate_american_odds(odds: int) -> None:
    if -100 < odds < 100:
        raise ValueError("American odds must be at least +100 or at most -100.")
    if odds == 0:
        raise ValueError("American odds cannot be zero.")


def _validate_probability(probability: float) -> None:
    if not 0 < probability < 1:
        raise ValueError("Probability must be greater than 0% and less than 100%.")


def american_to_decimal(odds: int) -> float:
    """Convert valid American odds to decimal odds."""
    _validate_american_odds(odds)
    if odds > 0:
        return 1 + odds / 100
    return 1 + 100 / abs(odds)


def implied_probability(odds: int) -> float:
    """Return the raw implied probability for valid American odds."""
    _validate_american_odds(odds)
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)


def expected_value(stake: float, probability: float, odds: int) -> float:
    """Calculate expected net profit for a stake, win probability, and odds."""
    _validate_american_odds(odds)
    _validate_probability(probability)
    if stake < 0:
        raise ValueError("Stake cannot be negative.")
    profit_if_won = stake * (american_to_decimal(odds) - 1)
    return probability * profit_if_won - (1 - probability) * stake


def kelly_fraction(probability: float, odds: int) -> float:
    """Return the non-negative full-Kelly bankroll fraction for the wager."""
    _validate_american_odds(odds)
    _validate_probability(probability)
    decimal_odds = american_to_decimal(odds)
    net_odds = decimal_odds - 1
    loss_probability = 1 - probability
    return max(0.0, (net_odds * probability - loss_probability) / net_odds)


def kelly_stakes(
    bankroll: float, probability: float, odds: int
) -> tuple[float, float]:
    """Return full- and half-Kelly suggested stakes for the available bankroll."""
    if bankroll < 0:
        raise ValueError("Bankroll cannot be negative.")
    fraction = kelly_fraction(probability, odds)
    full_stake = bankroll * fraction
    return full_stake, full_stake / 2
