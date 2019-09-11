import vcr
from whatson.ingest import ParseBelgrade, ParseAlbany


@vcr.use_cassette("fixtures/test_parse_belgrade.yaml")
def test_parse_belgrade():
    root_url = "http://www.belgrade.co.uk/"
    url = "http://www.belgrade.co.uk/whats-on/"

    results = list(ParseBelgrade(url, root_url).parse())

    assert len(results) == 66


@vcr.use_cassette("fixtures/test_parse_albany.yaml")
def test_parse_albany():
    root_url = "https://albanytheatre.co.uk/"
    url = "https://albanytheatre.co.uk/whats-on/"

    results = list(ParseAlbany(url, root_url).parse())

    assert len(results) == 49
