import pytest
import vcr
from whatson.ingest import ParseBelgrade, ParseAlbany
from datetime import date


class TestParseBelgrade:
    @vcr.use_cassette("fixtures/test_parse_belgrade.yaml")
    def setup(self):
        root_url = "http://www.belgrade.co.uk/"
        url = "http://www.belgrade.co.uk/whats-on/"

        self.results = list(ParseBelgrade(url, root_url).parse())

    def test_parse_belgrade(self):
        assert len(self.results) == 66
