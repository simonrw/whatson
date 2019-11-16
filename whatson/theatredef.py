from typing import NamedTuple, Optional, TextIO, List
import configparser
# from .parsers import Parser, custom as CustomParsers

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
    custom_class: Optional[str]

    # Whether to treat any links found as relative or not. Defaults to False.
    link_relative: bool

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
            link_relative=defn.getboolean("link-relative", fallback=False),
            fetcher=defn["fetcher"],
            custom_class=defn.get("custom-class", None),
            container_selector=defn["container-selector"],
            link_selector=defn["link-selector"],
            image_selector=defn["image-selector"],
            title_selector=defn["title-selector"],
            date_selector=defn["date-selector"],
            next_selector=defn.get("next-selector"),
        )
