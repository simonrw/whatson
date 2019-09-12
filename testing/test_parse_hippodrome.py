import pytest
import vcr
from whatson.ingest import ParseHippodrome
from datetime import date


class TestParseHippodrome:
    @vcr.use_cassette("fixtures/test_parse_hippodrome.yaml")
    def setup(self):
        url = "https://www.birminghamhippodrome.com/whats-on/"
        root_url = "https://www.birminghamhippodrome.com/"

        self.results = list(ParseHippodrome(url, root_url).parse())

    def test_number_of_results(self):
        assert len(self.results) == 73

    @pytest.mark.parametrize(
        "idx,start,end",
        [
            (0, date(2019, 9, 13), date(2019, 12, 13)),
            (16, date(2019, 9, 28), date(2019, 9, 28)),
            (51, date(2019, 12, 21), date(2020, 2, 2)),
            (-1, date(2020, 9, 15), date(2020, 9, 26)),
        ],
    )
    def test_parse_dates(self, idx, start, end):
        assert self.results[idx].start_date == start
        assert self.results[idx].end_date == end

