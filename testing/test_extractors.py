import vcr
from whatson.ingest import parse_belgrade, parse_albany


@vcr.use_cassette("fixtures/test_parse_belgrade.yaml")
def test_parse_belgrade():
    url = "http://www.belgrade.co.uk/whats-on/"

    results = list(parse_belgrade(url))

    assert len(results) == 66


@vcr.use_cassette("fixtures/test_parse_albany.yaml")
def test_parse_albany():
    url = "https://albanytheatre.co.uk/whats-on/"

    results = list(parse_albany(url))

    assert len(results) == 49
