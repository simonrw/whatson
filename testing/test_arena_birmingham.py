import pytest  # type: ignore
from unittest import mock
import vcr  # type: ignore
from whatson.fetchers import Fetcher
from datetime import date


@pytest.fixture(scope="session")
def results(get_theatre):
    theatre = get_theatre("arena-birmingham")
    fetcher = Fetcher.create(theatre.fetcher)
    with mock.patch.object(fetcher, "fetch") as mock_fetch:
        with open("fixtures/test_parse_arena_birmingham.html") as infile:
            mock_fetch.return_value = infile.read()
    html = fetcher.fetch(theatre.url)
    parser = theatre.to_parser()

    shows = []
    for item in parser.parse(html, fetcher):
        item.theatre = theatre.name
        shows.append(item)
    return shows


def test_number_of_results(results):
    assert len(results) == 49


@pytest.mark.parametrize(
    "idx,start,end",
    [
        (0, date(2019, 9, 13), date(2019, 9, 13)),
        (1, date(2019, 9, 13), date(2019, 9, 22)),
        (37, date(2020, 1, 1), date(2020, 1, 5)),
        (48, date(2020, 6, 6), date(2020, 6, 6)),
    ],
)
def test_parse_dates(results, idx, start, end):
    assert results[idx].start_date == start
    assert results[idx].end_date == end

