from whatson.ingest import Parser
from datetime import date


class DummyParser(Parser):
    def scrape(self):
        pass


def test_parse_text():
    text = "14 September 2019"

    result = DummyParser(None, None).date_text_to_date(text)

    assert result == date(2019, 9, 14)
