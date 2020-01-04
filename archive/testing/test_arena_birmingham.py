import pytest  # type: ignore
from unittest import mock
import vcr  # type: ignore
from whatson.parsers import ParseArenaBirmingham
from datetime import date


@pytest.fixture(scope="session")
def results():
    root_url = "https://www.arenabham.co.uk/"
    url = "https://www.arenabham.co.uk/whats-on/"

    parser = ParseArenaBirmingham(url, root_url)
    with open("fixtures/test_parse_arena_birmingham.html") as infile:
        html = infile.read()

    with mock.patch.object(parser, "fetcher") as mock_fetcher:
        mock_fetcher.fetch.return_value = html

        return list(parser.parse())


def test_number_of_results(results):
    assert len(results) == 56


@pytest.mark.parametrize(
    "idx,start,end",
    [
        (0, date(2019, 11, 15), date(2019, 11, 17)),
        (13, date(2019, 12, 23), date(2019, 12, 24)),
    ],
)
def test_parse_dates(results, idx, start, end):
    assert results[idx].start_date == start
    assert results[idx].end_date == end
