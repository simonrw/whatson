import pytest  # type: ignore
from whatson.parsers import ParseResortsWorldArena  # type: ignore
from datetime import date
from unittest import mock


@pytest.fixture(scope="session")
def results():
    root_url = "https://www.resortsworldarena.co.uk/"
    url = "https://www.resortsworldarena.co.uk/whats-on/"

    parser = ParseResortsWorldArena(url, root_url)
    with open("fixtures/test_parse_resortsworld_arena.html") as infile:
        html = infile.read()

    with mock.patch.object(parser, "fetcher") as mock_fetcher:
        mock_fetcher.fetch.return_value = html

        return list(parser.parse())


def test_number_of_results(results):
    assert len(results) == 31


@pytest.mark.parametrize(
    "idx,start,end",
    [
        (0, date(2019, 10, 2), date(2019, 10, 6)),
        (4, date(2019, 10, 19), date(2019, 10, 19)),
        (16, date(2020, 1, 31), date(2020, 2, 1)),
    ],
)
def test_parse_dates(results, idx, start, end):
    assert results[idx].start_date == start
    assert results[idx].end_date == end
