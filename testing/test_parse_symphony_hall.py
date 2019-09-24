import pytest
import vcr
from whatson.ingest import ParseSymphonyHall
from datetime import date


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/test_parse_symphony_hall.yaml")
def results():
    root_url = "https://www.thsh.co.uk/"
    url = "https://www.thsh.co.uk/whats-on/"

    return list(ParseSymphonyHall(url, root_url).parse())


def test_number_of_results(results):
    assert len(results) == 348


@pytest.mark.parametrize(
    "idx,start,end",
    [
        (0, date(2019, 9, 14), date(2019, 9, 14)),
        (10, date(2019, 9, 21), date(2019, 12, 7)),
        (198, date(2019, 12, 31), date(2020, 1, 2)),
    ],
)
def test_parse_dates(results, idx, start, end):
    assert results[idx].start_date == start
    assert results[idx].end_date == end


def test_no_duplicate_show_names(results):
    """
    Regression test. A bug in the code caused repeated finding of the
    same title throughout the page. This test ensures this does not happen
    again.
    """
    names = [show.name for show in results]

    # Check that they are basically unique (some show names may be
    # repeated, but certainly not too many
    assert len(set(names)) == 316
