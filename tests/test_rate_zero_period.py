from rate_calculator import calculate_rate


def test_zero_period_returns_zero_instead_of_crashing():
    assert calculate_rate(100, 0) == 0.0
