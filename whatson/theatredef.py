from typing import NamedTuple, Optional, TextIO, List
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
    def from_definition(cls, defn: configparser.SectionProxy) -> "TheatreDefinition":
        return TheatreDefinition(
            name=defn.name,
            active=defn.getboolean("active"),
            root_url=defn["root-url"],
            url=defn["url"],
            fetcher=defn["fetcher"],
            container_selector=defn["container-selector"],
            link_selector=defn["link-selector"],
            image_selector=defn["image-selector"],
            title_selector=defn["title-selector"],
            date_selector=defn["date-selector"],
            next_selector=defn.get("next-selector"),
        )
