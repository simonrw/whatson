import pytest
import vcr
from whatson.fetchers import Fetcher
from whatson.parsers import Parser
from datetime import date


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/test_parse_hippodrome.yaml")
def results(get_theatre):
    theatre = get_theatre("hippodrome")
    fetcher = Fetcher.create(theatre.fetcher)
    html = fetcher.fetch(theatre.url)
    parser = theatre.to_parser()

    shows = []
    for item in parser.parse(html, fetcher):
        item.theatre = theatre.name
        shows.append(item)
    return shows


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


def test_parse_specific_date(results):
    parser = Parser(None)
    result = parser._date_text_to_date("Wed 8 Apr - Sat 11 Apr 2020")
    assert result.start == date(2020, 4, 8)
    assert result.end == date(2020, 4, 11)
