from whatson import ingest
from unittest import mock
import datetime


@mock.patch("whatson.ingest._fetch_html")
def test_albany(client):
    with open("testing/responses/albany.html") as infile:
        client.return_value = infile.read()

    config = {
        "name": "albany",
        "root_url": "https://albanytheatre.co.uk/",
        "url": "https://albanytheatre.co.uk/whats-on/",
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
        "root_url": "http://www.belgrade.co.uk/",
        "url": "http://www.belgrade.co.uk/whats-on/",
    }

    shows = list(ingest.fetch_shows(config))

    assert len(shows) == 66
    assert shows[0]["start_date"] == datetime.date(2019, 11, 27)
    assert shows[0]["end_date"] == datetime.date(2020, 1, 11)
    assert shows[0]["title"] == "Puss In Boots"

    assert shows[-1]["start_date"] == datetime.date(2020, 11, 25)
    assert shows[-1]["end_date"] == datetime.date(2021, 1, 9)
    assert shows[-1]["title"] == "Beauty and the Beast"
