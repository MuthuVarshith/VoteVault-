from rate_calculator import calculate_rate


def test_rate_divides_amount_by_period():
    assert calculate_rate(100, 4) == 25.0


def test_rate_keeps_fractions():
    assert calculate_rate(10, 4) == 2.5
