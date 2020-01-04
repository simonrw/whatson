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
