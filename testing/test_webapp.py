# pylint: disable=missing-module-docstring,missing-function-docstring
from whatson.webapp import interpolate_months


def test_something():
    start = {"year": 2019, "month": 11}
    end = {"year": 2020, "month": 8}

    dates = list(interpolate_months([start, end]))

    assert dates == [
        {"year": 2019, "month": 11},
        {"year": 2019, "month": 12},
        {"year": 2020, "month": 1},
        {"year": 2020, "month": 2},
        {"year": 2020, "month": 3},
        {"year": 2020, "month": 4},
        {"year": 2020, "month": 5},
        {"year": 2020, "month": 6},
        {"year": 2020, "month": 7},
        {"year": 2020, "month": 8},
    ]
