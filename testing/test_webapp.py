# pylint: disable=missing-module-docstring,missing-function-docstring
import pytest
from whatson.webapp import create_app, interpolate_months
import datetime
from unittest import mock


@pytest.fixture(scope="module")
def client(connection):
    app = create_app(connection)
    with app.test_client() as client:
        yield client


def test_getting_months(client, cursor):
    start_date = datetime.date(2019, 1, 2)
    end_date = datetime.date(2019, 2, 3)
    cursor.execute(
        """INSERT INTO shows (theatre, title, image_url, link_url, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s)""",
        ("test", "show", "", "", start_date, end_date),
    )

    rv = client.get("/api/months")
    data = rv.get_json()

    expected = [{"year": 2019, "month": 1}, {"year": 2019, "month": 2}]
    assert data["dates"] == expected


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
