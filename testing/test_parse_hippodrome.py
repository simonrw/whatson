import pytest
import vcr
from whatson.ingest import ParseHippodrome
from datetime import date


class TestParseHippodrome:
    @vcr.use_cassette("fixtures/test_parse_hippodrome.yaml")
    def setup(self):
        url = "https://www.birminghamhippodrome.com/whats-on/"
        root_url = "https://www.birminghamhippodrome.com/"

        self.cls = ParseHippodrome(url, root_url)
        self.results = list(self.cls.parse())

    def test_number_of_results(self):
        assert len(self.results) == 73

    @pytest.mark.parametrize(
        "idx,start,end",
        [
            (0, date(2019, 9, 13), date(2019, 12, 13)),
            (16, date(2019, 9, 28), date(2019, 9, 28)),
            (51, date(2019, 12, 21), date(2020, 2, 2)),
            (52, date(2020, 1, 22), date(2020, 1, 23)),
            (-1, date(2020, 9, 15), date(2020, 9, 26)),
        ],
    )
    def test_parse_dates(self, idx, start, end):
        assert self.results[idx].start_date == start
        assert self.results[idx].end_date == end

    def test_parse_specific_date(self):
        result = self.cls.date_text_to_date("Wed 8 Apr - Sat 11 Apr 2020")
        assert result.start == date(2020, 4, 8)
        assert result.end == date(2020, 4, 11)
