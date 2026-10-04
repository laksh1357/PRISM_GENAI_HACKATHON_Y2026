from calculator import add, average


def test_add():
    assert add(2, 3) == 5


def test_average_preserves_fractional_values():
    assert average([2, 3]) == 2.5

