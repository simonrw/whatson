import pytest
from whatson.theatredef import TheatreDefinition
from io import StringIO


@pytest.fixture(scope="session")
def config():
    return StringIO(
        r"""[belgrade]
active = yes
root-url = http://www.belgrade.co.uk/
url = http://www.belgrade.co.uk/whats-on/
fetcher = requests
container-selector = div.list-productions
link-selector = a.production-link
image-selector = a.production-link > img
title-selector = h2,h3
date-selector = p.date

[symphony-hall]
active = yes
root-url = https://www.thsh.co.uk/
url = https://www.thsh.co.uk/whats-on/
fetcher = selenium
container-selector = div.list-productions
link-selector = a.production-link
image-selector = a.production-link > img
title-selector = h2,h3
date-selector = p.date
next-selector = div#next
    """
    )


@pytest.fixture(scope="session")
def definitions(config):
    return TheatreDefinition.parse_config(config)


@pytest.fixture(scope="session")
def defn(definitions):
    def _inner(idx):
        return definitions[idx]

    return _inner


def test_length(definitions):
    assert len(definitions) == 2


@pytest.mark.parametrize(
    "attr,expected",
    [
        ("name", "belgrade"),
        ("active", True),
        ("root_url", "http://www.belgrade.co.uk/"),
        ("url", "http://www.belgrade.co.uk/whats-on/"),
        ("fetcher", "requests"),
        ("container_selector", "div.list-productions"),
        ("link_selector", "a.production-link"),
        ("image_selector", "a.production-link > img"),
        ("title_selector", "h2,h3"),
        ("date_selector", "p.date"),
    ],
)
def test_first_attribute(attr, expected, defn):
    assert getattr(defn(0), attr) == expected


@pytest.mark.parametrize(
    "attr,expected", [("name", "symphony-hall"), ("next_selector", "div#next")]
)
def test_second_attributes(attr, expected, defn):
    assert getattr(defn(1), attr) == expected
