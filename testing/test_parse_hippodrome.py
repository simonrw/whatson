import pytest
import vcr
from whatson.ingest import ParseHippodrome
from datetime import date


@pytest.fixture(scope="session")
def parser():
    url = "https://www.birminghamhippodrome.com/whats-on/"
    root_url = "https://www.birminghamhippodrome.com/"
    return ParseHippodrome(url, root_url)


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/test_parse_hippodrome.yaml")
def results(parser):
    return list(parser.parse())


def test_number_of_results(results):
    assert len(results) == 73


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
def test_parse_dates(results, idx, start, end):
    assert results[idx].start_date == start
    assert results[idx].end_date == end


def test_parse_specific_date(results, parser):
    result = parser.date_text_to_date("Wed 8 Apr - Sat 11 Apr 2020")
    assert result.start == date(2020, 4, 8)
    assert result.end == date(2020, 4, 11)
