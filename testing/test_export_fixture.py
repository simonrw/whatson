from pathlib import Path
import yaml
from whatson.exportfixture import fixture_to_html


def test_to_html():
    fixture = Path(".").joinpath("fixtures", "test_parse_belgrade.yaml")
    assert fixture.is_file()

    with fixture.open() as infile:
        fixture_data = yaml.safe_load(infile)

    html = fixture_to_html(fixture_data)

    assert "Belgrade" in html
