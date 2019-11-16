import pytest
import vcr
from whatson.parsers import ParseBelgrade
from datetime import date


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/test_parse_belgrade.yaml")
def results():
    root_url = "http://www.belgrade.co.uk/"
    url = "http://www.belgrade.co.uk/whats-on/"

    return list(ParseBelgrade(url, root_url).parse())


def test_number_of_results(results):
    assert len(results) == 64


@pytest.mark.parametrize(
    "idx,start,end",
    [
        (0, date(2019, 9, 13), date(2019, 9, 13)),
        (9, date(2019, 10, 2), date(2019, 10, 2)),
        (28, date(2019, 10, 29), date(2019, 11, 2)),
        (42, date(2020, 1, 15), date(2020, 1, 15)),
        (-1, date(2020, 7, 27), date(2020, 7, 27)),
    ],
)
def test_parse_dates(results, idx, start, end):
    assert results[idx].start_date == start
    assert results[idx].end_date == end
