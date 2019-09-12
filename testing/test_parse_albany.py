import pytest
import vcr
from whatson.ingest import ParseBelgrade, ParseAlbany
from datetime import date


class TestParseAlbany(object):
    @vcr.use_cassette("fixtures/test_parse_albany.yaml")
    def setup(self):
        root_url = "https://albanytheatre.co.uk/"
        url = "https://albanytheatre.co.uk/whats-on/"

        self.results = list(ParseAlbany(url, root_url).parse())

    def test_number_of_results(self):
        assert len(self.results) == 49

    @pytest.mark.parametrize(
        "idx,start,end",
        [
            (0, date(2019, 9, 13), date(2019, 9, 13)),
            (1, date(2019, 9, 13), date(2019, 9, 22)),
            (37, date(2020, 1, 1), date(2020, 1, 5)),
            (48, date(2020, 6, 6), date(2020, 6, 6)),
        ],
    )
    def test_parse_dates(self, idx, start, end):
        assert self.results[idx].start_date == start
        assert self.results[idx].end_date == end
