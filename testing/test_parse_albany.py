import pytest  # type: ignore
import vcr  # type: ignore
from whatson.fetchers import Fetcher
from datetime import date


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/test_parse_albany.yaml")
def results(get_theatre):
    theatre = get_theatre("albany")
    fetcher = Fetcher.create(theatre.fetcher)
    html = fetcher.fetch(theatre.url)
    parser = theatre.to_parser()

    shows = []
    for item in parser.parse(html):
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
