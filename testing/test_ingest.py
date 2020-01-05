from whatson import ingest
from unittest import mock
import datetime


@mock.patch("whatson.ingest._fetch_html")
def test_albany(client):
    with open("testing/responses/albany.html") as infile:
        client.return_value = infile.read()

    config = {
        "name": "albany",
        "root_url": "",
        "url": "",
    }

    shows = list(ingest.fetch_shows(config))

    assert len(shows) == 29
    assert shows[0]["start_date"] == datetime.date(2020, 1, 1)
    assert shows[-1]["title"] == "The Mersey Beatles 2020"


@mock.patch("whatson.ingest._fetch_html")
def test_belgrade(client):
    with open("testing/responses/belgrade.html") as infile:
        client.return_value = infile.read()

    config = {
        "name": "belgrade",
        "root_url": "",
        "url": "",
    }

    shows = list(ingest.fetch_shows(config))

    assert len(shows) == 66
    assert shows[0]["start_date"] == datetime.date(2019, 11, 27)
    assert shows[0]["end_date"] == datetime.date(2020, 1, 11)
    assert shows[0]["title"] == "Puss In Boots"

    assert shows[-1]["start_date"] == datetime.date(2020, 11, 25)
    assert shows[-1]["end_date"] == datetime.date(2021, 1, 9)
    assert shows[-1]["title"] == "Beauty and the Beast"


@mock.patch("whatson.ingest._fetch_html")
def test_symphony_hall(client):
    with open("testing/responses/symphony_hall_1.html") as infile:
        resp1 = infile.read()

    with open("testing/responses/symphony_hall_2.html") as infile:
        resp2 = infile.read()

    client.side_effect = [resp1, resp2]

    config = {
        "name": "symphony-hall",
        "root_url": "",
        "url": "",
    }

    shows = list(ingest.fetch_shows(config))

    assert len(shows) == 24
    assert shows[0]["start_date"] == datetime.date(2020, 1, 5)
    assert shows[0]["end_date"] == datetime.date(2020, 1, 12)
    assert shows[0]["title"] == "We're Going On A Bear Hunt"

    assert shows[-1]["start_date"] == datetime.date(2020, 1, 28)
    assert shows[-1]["end_date"] == datetime.date(2020, 1, 28)
    assert shows[-1]["title"] == "Echo Eternal Youth Arts Festival 2020: Horizons"


@mock.patch("whatson.ingest._fetch_html")
def test_hippodrome(client):
    with open("testing/responses/hippodrome_1.html") as infile:
        resp1 = infile.read()

    with open("testing/responses/hippodrome_2.html") as infile:
        resp2 = infile.read()

    client.side_effect = [resp1, resp2]

    config = {
        "name": "hippodrome",
        "root_url": "",
        "url": "",
    }

    shows = list(ingest.fetch_shows(config))

    assert len(shows) == 32
    assert shows[0]["start_date"] == datetime.date(2020, 1, 5)
    assert shows[0]["end_date"] == datetime.date(2020, 2, 2)
    assert shows[0]["title"] == "Snow White & the Seven Dwarfs"

    assert shows[-1]["start_date"] == datetime.date(2020, 3, 27)
    assert shows[-1]["end_date"] == datetime.date(2020, 3, 28)
    assert shows[-1]["title"] == "DX - Mariposa"


@mock.patch("whatson.ingest._fetch_html")
def test_resortsworld(client):
    with open("testing/responses/resortsworld.html") as infile:
        client.return_value = infile.read()

    config = {
        "name": "resortsworld-arena",
        "root_url": "",
        "url": "",
    }

    shows = list(ingest.fetch_shows(config))

    assert len(shows) == 28
    assert shows[0]["start_date"] == datetime.date(2020, 1, 31)
    assert shows[0]["end_date"] == datetime.date(2020, 2, 1)
    assert shows[0]["title"] == "The Arenacross Tour 2020"

    assert shows[-1]["start_date"] == datetime.date(2020, 11, 21)
    assert shows[-1]["end_date"] == datetime.date(2020, 11, 21)
    assert shows[-1]["title"] == "Free Radio Hits Live 2020"


@mock.patch("whatson.ingest._fetch_html")
def test_arena_bham(client):
    with open("testing/responses/arena_birmingham.html") as infile:
        client.return_value = infile.read()

    config = {
        "name": "arena-birmingham",
        "root_url": "",
        "url": "",
    }

    shows = list(ingest.fetch_shows(config))

    assert len(shows) == 61
    assert shows[0]["start_date"] == datetime.date(2020, 1, 16)
    assert shows[0]["end_date"] == datetime.date(2020, 1, 19)
    assert shows[0]["title"] == "Strictly Come Dancing The Live Tour 2020"

    assert shows[-1]["start_date"] == datetime.date(2020, 12, 11)
    assert shows[-1]["end_date"] == datetime.date(2020, 12, 11)
    assert shows[-1]["title"] == "Il Divo"


@mock.patch("whatson.ingest._fetch_html")
def test_artrix(client):
    with open("testing/responses/artrix_1.html") as infile:
        resp1 = infile.read()

    with open("testing/responses/artrix_2.html") as infile:
        resp2 = infile.read()

    with open("testing/responses/artrix_3.html") as infile:
        resp3 = infile.read()

    client.side_effect = [resp1, resp2, resp3]

    config = {
        "name": "artrix",
        "root_url": "",
        "url": "",
    }

    shows = list(ingest.fetch_shows(config))

    assert len(shows) == 32
    assert shows[0]["start_date"] == datetime.date(2019, 11, 5)
    assert shows[0]["end_date"] == datetime.date(2020, 1, 5)
    assert shows[0]["title"] == "KATHLEEN WATSON AND LYNNE SAWYER  - INSPIRE BY NATURE"

    assert shows[-1]["start_date"] == datetime.date(2020, 1, 18)
    assert shows[-1]["end_date"] == datetime.date(2020, 1, 18)
    assert shows[-1]["title"] == "Polar Squad"
