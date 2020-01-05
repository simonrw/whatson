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
from .db import DB, reset_database

log = logging.getLogger("whatson")
log.setLevel(logging.DEBUG)

# Database management


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

    fetchers = {
        "albany": fetch_shows_albany,
        "belgrade": fetch_shows_belgrade,
        "symphony-hall": fetch_shows_symphony_hall,
    }

    try:
        fetcher = fetchers[theatre_config["name"]]
    except KeyError:
        raise NotImplementedError(theatre_config["name"])
    else:
        return fetcher(theatre_config)


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

        title = elem.find("h4").find("a").text.strip()
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


def fetch_shows_belgrade(theatre_config):
    html = _fetch_html(theatre_config["url"])
    soup = BeautifulSoup(html, "lxml")

    container = soup.find("div", class_="list-productions", id="secondary-content")

    # The month and year _should_ be set up by the first child container, which
    # will hopefully be a month/year panel. If this is not the case, then we
    # have to rethink the way this date/time parsing works.
    month = None
    year = None

    # Regex replacer to remove 1st/2nd/3rd/4th etc.
    date_replacer = re.compile(r"\b([0123]?[0-9])(st|th|nd|rd)\b")

    for elem in container.children:
        if not isinstance(elem, Tag):
            continue

        if elem.name == "h2":
            # Month/Year section
            date_text = elem.text.lower()
            tmp_date = datetime.datetime.strptime(date_text, "%B %Y").date()
            month = tmp_date.month
            year = tmp_date.year

            log.info("found month/year panel, month = %s, year = %s", month, year)
            continue

        if "class" not in elem.attrs:
            continue

        if "production-list-item" not in elem.attrs["class"]:
            continue

        # We should always have a month and year, as hopefully the first panel
        # is a month/day panel
        assert month is not None
        assert year is not None

        title = elem.find("h3").text.strip()
        date_text = elem.find("p", class_="date").text.strip().lower()

        link_url = elem.find("a", class_="production-link").attrs["href"]
        link_url = "".join([theatre_config["root_url"], link_url])

        image_url = elem.find("a", class_="production-link").find("img").attrs["src"]
        image_url = "".join([theatre_config["root_url"], image_url])

        # Parse the date from this panel. First we replace instances of e.g.
        # 1st -> 1 so that strptime can parse the day and month
        date_text = date_replacer.sub(r"\1", date_text)

        def parse_single_date(text):
            try:
                tmp_date = datetime.datetime.strptime(text, "%d %B").date()
            except ValueError as e:
                if "day is out of range for month" in str(e):
                    # Leap year? Try parsing with the current year
                    text = f"{text} {year}"
                    tmp_date = datetime.datetime.strptime(text, "%d %B %Y").date()
            return datetime.datetime(year, tmp_date.month, tmp_date.day).date()

        if "-" in date_text:
            # Separate start and end dates
            parts = [part.strip() for part in date_text.split("-")]
            start_date = parse_single_date(parts[0])
            end_date = parse_single_date(parts[1])
        else:
            # Single date
            start_date = parse_single_date(date_text)
            end_date = start_date

        log.debug("DATES: %s %s", start_date, end_date)

        # Check if the start date and end date make sense. The start date must
        # be the same as the date panel. If this is not the case, something is
        # up. Therefore if the end date is before the start date then we must
        # add one to the end date year.
        assert start_date.year == year
        if end_date < start_date:
            end_date = datetime.date(end_date.year + 1, end_date.month, end_date.day)

        yield {
            "title": title,
            "image_url": image_url,
            "link_url": link_url,
            "start_date": start_date,
            "end_date": end_date,
        }


def fetch_shows_symphony_hall(theatre_config):
    url = theatre_config["url"]

    # Loop over all pages
    while True:
        html = _fetch_html(url)
        soup = BeautifulSoup(html, "lxml")

        container = soup.find("ul", class_="grid cf")
        assert len(container.contents) <= 16
        for elem in container.contents:
            # The title is in capitals so we must turn this into a nicer
            # format. Note we should treat each word separately rather than
            # calling the `.title` method as this does not support embedded
            # apostrophes (https://stackoverflow.com/a/1549644)
            raw_title = elem.find("h3").text
            title = " ".join(w.capitalize() for w in raw_title.split())

            link_url = elem.find("a", class_="event-block").attrs["href"]
            image_url = (
                elem.find("img", class_="o-image__full").attrs["data-srcset"].split()[0]
            )

            date_container = elem.find("span", class_="event-block__time")
            times = date_container.find_all("time")
            if len(times) == 1:
                # Simple case, only a single time available
                start_date = datetime.datetime.fromisoformat(
                    times[0].attrs["datetime"]
                ).date()
                end_date = start_date
            elif len(times) == 2:
                # We have start time and end time
                assert times[0].attrs["itemprop"] == "startDate"
                assert times[1].attrs["itemprop"] == "endDate"

                start_date = datetime.datetime.fromisoformat(
                    times[0].attrs["datetime"]
                ).date()
                end_date = datetime.datetime.fromisoformat(
                    times[1].attrs["datetime"]
                ).date()
            else:
                raise NotImplementedError(f"cannot parse dates from {date_container}")

            yield {
                "title": title,
                "image_url": image_url,
                "link_url": link_url,
                "start_date": start_date,
                "end_date": end_date,
            }

        # Handle pagination
        next_link = soup.find("a", class_="pagination__link--next")
        if next_link and "disabled" not in next_link.attrs["class"]:
            url = next_link.attrs["href"]
        else:
            break


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
        if not theatre_config["active"]:
            log.info("Theatre %s is not active, skipping", theatre_config["name"])
            continue

        shows = fetch_shows(theatre_config)
        for show in shows:
            upload(theatre_config["name"], show)
