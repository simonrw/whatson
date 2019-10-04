from typing import NamedTuple, Optional, TextIO, List, Dict, Any
import configparser

URL = str
CSSSelector = str
Fetcher = str


class TheatreDefinition(NamedTuple):
    """Configuration for a theatre.

    This is typically created from a config file, rather than created manually.
    """

    name: str
    active: bool
    root_url: URL
    url: URL
    fetcher: Fetcher

    # Selectors
    container_selector: CSSSelector
    link_selector: CSSSelector
    image_selector: CSSSelector
    title_selector: CSSSelector
    date_selector: CSSSelector
    next_selector: Optional[CSSSelector]

    @classmethod
    def parse_config(cls, fptr: TextIO) -> List["TheatreDefinition"]:
        config = configparser.ConfigParser()
        config.read_file(fptr)
        theatres = []
        for cfg in config.sections():
            theatre = TheatreDefinition.from_definition(config[cfg])
            theatres.append(theatre)
        return theatres

    @classmethod
    def from_definition(cls, defn: Dict[str, Any]) -> "TheatreDefinition":
        return TheatreDefinition(
            name=defn.name,
            active=True,
            root_url="",
            url="",
            fetcher=None,
            container_selector="",
            link_selector="",
            image_selector="",
            title_selector="",
            date_selector="",
            next_selector=None,
        )
