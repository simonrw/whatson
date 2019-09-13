import pytest
import vcr
from whatson.ingest import ParseSymphonyHall
from datetime import date


class TestParseSymphonyHall(object):
    @vcr.use_cassette("fixtures/test_parse_symphony_hall.yaml")
    def setup(self):
        root_url = "https://www.thsh.co.uk/"
        url = "https://www.thsh.co.uk/whats-on/"

        self.results = list(ParseSymphonyHall(url, root_url).parse())

    def test_number_of_results(self):
        assert len(self.results) == 348

    @pytest.mark.parametrize(
        "idx,start,end",
        [
            (0, date(2019, 9, 14), date(2019, 9, 14)),
            (10, date(2019, 9, 21), date(2019, 12, 7)),
            (198, date(2019, 12, 31), date(2020, 1, 2)),
        ],
    )
    def test_parse_dates(self, idx, start, end):
        assert self.results[idx].start_date == start
        assert self.results[idx].end_date == end
