import logging
import argparse
import configparser

log = logging.getLogger("whatson")


def upload(show):
    """Given a show extracted from the theatre page, upload the show to the database"""
    log.info("uploading %s", show)
    pass


def fetch_shows(theatre_config):
    """Given a theatre config, fetch the shows and yield each show"""
    log.info("fetching %s", theatre_config)

    yield None


def load_config(fptr):
    """Load the list of theatres from the config file"""
    parser = configparser.ConfigParser()
    fptr.seek(0)
    parser.read_file(fptr)

    for section in parser.sections():
        config = parser[section]
        yield {
            "name": section,
            "active": config.getboolean("active"),
            "root_url": config["root-url"],
            "url": config["url"],
        }


def main():
    logging.basicConfig(level=logging.DEBUG)

    # Set up the command line parser

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        default="config.ini",
        type=argparse.FileType(mode="r"),
    )
    args = parser.parse_args()

    # Run the ingestion

    config = load_config(args.config)
    for theatre_config in config:
        shows = fetch_shows(theatre_config)
        for show in shows:
            upload(show)
