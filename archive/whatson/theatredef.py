from typing import NamedTuple, Optional, TextIO, List
import configparser
# from .parsers import Parser, custom as CustomParsers

URL = str


class TheatreDefinition(NamedTuple):
    """Configuration for a theatre.

    This is typically created from a config file, rather than created manually.
    """

    name: str
    active: bool
    root_url: URL
    url: URL

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
        )
