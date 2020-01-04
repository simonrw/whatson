from dotenv import load_dotenv
import logging
import psycopg2
from psycopg2.errors import UniqueViolation
import argparse
import datetime
import configparser
import re
import os
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

log = logging.getLogger("whatson")
log.setLevel(logging.DEBUG)

# Database management

load_dotenv()

DB = psycopg2.connect(os.environ["DATABASE_URL"])


def reset_database():
    with DB as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS shows")
        cursor.execute(
            """CREATE TABLE shows (
                id SERIAL PRIMARY KEY,
                theatre VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                image_url VARCHAR(1024) NOT NULL,
                link_url VARCHAR(1024) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
        )
        cursor.execute(
            """CREATE UNIQUE INDEX _idx_shows_theatre_title
                ON shows (theatre, title)
                """
        )


def upload(theatre, show):
    """Given a show extracted from the theatre page, upload the show to the database"""
    log.info("uploading %s", show)
    with DB as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO shows (theatre, title, image_url, link_url, start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    theatre,
                    show["title"],
                    show["image_url"],
                    show["link_url"],
                    show["start_date"],
                    show["end_date"],
                ),
            )
        except UniqueViolation:
            # We have added this show already
            log.debug("duplicate show %s found, skipping", show)
            return
        except:
            raise


# Show fetching
CLIENT = requests.Session()
CLIENT.headers["User-Agent"] = "whatson/0.1.0"


def _fetch_html(url):
    r = CLIENT.get(url)
    r.raise_for_status()

    return r.text


def fetch_shows(theatre_config):
    """Given a theatre config, fetch the shows and yield each show"""
    log.info("fetching %s", theatre_config["url"])

    if theatre_config["name"] == "albany":
        return fetch_shows_albany(theatre_config)
    else:
        raise NotImplementedError(theatre_config["name"])


def fetch_shows_albany(theatre_config):
    html = _fetch_html(theatre_config["url"])
    soup = BeautifulSoup(html, "lxml")

    container = soup.find("div", class_="query_block_content")
    for elem in container.children:
        if not isinstance(elem, Tag):
            continue

        try:
            date_str = elem.find(class_="show-date").text.lower()
        except AttributeError:
            continue

        title = elem.find("h4").find("a").text
        image_url = elem.find("img").attrs["src"]
        image_url = "".join([theatre_config["root_url"], image_url])

        link_url = elem.find("h4").find("a").attrs["href"]
        link_url = "".join([theatre_config["root_url"], link_url])

        # Parse date string
        if "-" in date_str:
            # Two separate dates
            parts = [part.strip() for part in date_str.split("-")]
            end_date = datetime.datetime.strptime(parts[1], "%d %B %Y").date()

            dm = datetime.datetime.strptime(parts[0], "%d %B").date()
            start_date = datetime.date(end_date.year, dm.month, dm.day)
        else:
            # One date therefore start_date = end_date
            start_date = datetime.datetime.strptime(date_str, "%d %B %Y").date()
            end_date = start_date

        yield {
            "title": title,
            "image_url": image_url,
            "link_url": link_url,
            "start_date": start_date,
            "end_date": end_date,
        }


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
    logging.basicConfig(level=logging.WARNING)

    # Set up the command line parser

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        default="config.ini",
        type=argparse.FileType(mode="r"),
    )
    parser.add_argument(
        "-r",
        "--reset",
        action="store_true",
        default=False,
        help="Clear database contents before ingesting",
    )
    args = parser.parse_args()

    if args.reset:
        reset_database()

    # Run the ingestion

    config = load_config(args.config)
    for theatre_config in config:
        shows = fetch_shows(theatre_config)
        for show in shows:
            upload(theatre_config["name"], show)
