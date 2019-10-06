import pytest  # type: ignore
from whatson.theatredef import TheatreDefinition


@pytest.fixture(scope="session")
def get_theatre():
    def _inner(name):
        with open("config.ini") as infile:
            theatres = TheatreDefinition.parse_config(infile)

        for theatre in theatres:
            if theatre.name == name:
                return theatre

        raise KeyError("cannot find theatre")

    return _inner
