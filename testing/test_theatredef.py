import pytest
from whatson.theatredef import TheatreDefinition
from io import StringIO


@pytest.fixture(scope="session")
def config():
    return StringIO(
        r"""[belgrade]
active = true
root_url = http://www.belgrade.co.uk/
url = http://www.belgrade.co.uk/whats-on/
fetcher = requests
container_selector = div.list-productions
link_selector = a.production-link
image_selector = a.production-link > img
title_selector = h2,h3
date_selector = p.date
    """
    )


def test_parse_config(config):
    defns = TheatreDefinition.parse_config(config)
    assert len(defns) == 1
