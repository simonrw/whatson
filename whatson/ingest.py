#!/usr/bin/env python


import abc
import click
import json
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
import requests
import re
from datetime import date, datetime
from typing import NamedTuple
from .models import Base, Show, session, engine
from .theatredef import TheatreDefinition
from sqlalchemy.exc import IntegrityError  # type: ignore
from selenium import webdriver  # type: ignore

CURRENT_YEAR = date.today().year

rsess = requests.Session()
rsess.headers[
    "User-Agent"
] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0"

YEAR_RE = re.compile(r"20\d{2}")


class DateRange(NamedTuple):
    start: date
    end: date


class DateParseMixin(object):
    def date_text_to_date(self, date_text, year=None):
        date_text = date_text.strip().lower()
        if "-" in date_text:
            parts = date_text.split("-")
            if year is None:
                match = re.search(r"20\d{2}", date_text)
                if not match:
                    year = CURRENT_YEAR
                else:
                    year = int(match.group(0))

            start = self.date_text_to_date(parts[0], year)
            end = self.date_text_to_date(parts[1], year)

            if start > end:
                start = date(start.year - 1, start.month, start.day)

            return DateRange(start=start, end=end)
        else:
            match = re.search(
                r"(?P<day_str>\d+)\w*\s*(?P<month_str>\w+)\s*(?P<year_str>\d+)?",
                date_text,
            )
            if not match:
                raise ValueError("error parsing string {}".format(date_text))

            day = int(match.group("day_str"))
            month_str = match.group("month_str")
            month = [
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
            ].index(month_str) % 12

            if year is None and match.group("year_str") is None:
                year = CURRENT_YEAR

            if year is not None:
                return date(year, month + 1, day)
            else:
                year = int(match.group("year_str"))
                return date(year, month + 1, day)


class SoupParser(DateParseMixin, abc.ABC):
    def __init__(self, url, root_url):
        self.url = url
        self.root_url = root_url

    def parse(self):
        r = rsess.get(self.url)
        r.raise_for_status()

        html = r.text
        self.soup = BeautifulSoup(html, "lxml")

        return self.scrape()

    def next_page(self, url):
        r = rsess.get(url)
        r.raise_for_status()

        html = r.text
        self.soup = BeautifulSoup(html, "lxml")

    @abc.abstractmethod
    def scrape(self):
        pass


class ParseSymphonyHall(SoupParser):
    def scrape(self):
        page = 1
        while True:
            container = self.soup.find("ul", class_="grid cf")
            assert len(container.contents) <= 16
            for elem in container.contents:
                title = elem.find("h3").text

                link_url = elem.find("a", class_="event-block").attrs["href"]
                image_url = (
                    elem.find("img", class_="o-image__full")
                    .attrs["data-srcset"]
                    .split()[0]
                )

                date_container = elem.find("span", class_="event-block__time")
                times = date_container.find_all("time")
                if len(times) == 1:
                    # Simple case, only a single time available
                    start_time = datetime.fromisoformat(
                        times[0].attrs["datetime"]
                    ).date()
                    end_time = start_time
                elif len(times) == 2:
                    # We have start time and end time
                    assert times[0].attrs["itemprop"] == "startDate"
                    assert times[1].attrs["itemprop"] == "endDate"

                    start_time = datetime.fromisoformat(
                        times[0].attrs["datetime"]
                    ).date()
                    end_time = datetime.fromisoformat(times[1].attrs["datetime"]).date()

                yield Show(
                    name=title,
                    image_url=image_url,
                    link_url=link_url,
                    start_date=start_time,
                    end_date=end_time,
                )

            next_link = self.soup.find("a", class_="pagination__link--next")
            if next_link and "disabled" not in next_link.attrs["class"]:
                next_url = next_link.attrs["href"]
                self.next_page(next_url)
                page += 1
            else:
                break


class SeleniumParser(DateParseMixin, abc.ABC):
    def __init__(self, url, root_url):
        self.url = url
        self.root_url = root_url

        self.driver = webdriver.PhantomJS()

    @abc.abstractmethod
    def scrape(self):
        pass

    def parse(self):
        self.driver.get(self.url)
        html = self.driver.page_source
        self.soup = BeautifulSoup(html, "lxml")

        return self.scrape()


def upload_theatre(theatre, custom_parsers):
    name = theatre.name
    if theatre.name in custom_parsers:
        url = theatre.url
        root_url = theatre.root_url

        parser = custom_parsers.get(name)
        if not parser:
            raise ValueError("cannot find parser for {}".format(name))
        parsed = parser(url, root_url).parse()

        for item in parsed:
            try:
                with session() as sess:
                    item.theatre = name
                    sess.add(item)
            except IntegrityError:
                continue
    else:
        fetcher = Fetcher.create(theatre.fetcher)
        html = fetcher.fetch(theatre.url)
        parser = theatre.to_parser()
        for item in parser.parse(html):
            item.theatre = theatre.name
            try:
                with session() as sess:
                    sess.add(item)
            except IntegrityError:
                continue


@click.command()
@click.argument("filename")
@click.option("--reset/--no-reset")
def main(filename, reset):
    if reset:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    with open(filename) as infile:
        theatres = TheatreDefinition.parse_config(infile)

    custom_parsers = {
        "belgrade": ParseBelgrade,
        "albany": ParseAlbany,
        "hippodrome": ParseHippodrome,
        "symphony-hall": ParseSymphonyHall,
        "resortsworld-arena": ParseResortsWorldArena,
    }

    for theatre in theatres:
        print(theatre.name)
        if theatre.active:
            try:
                upload_theatre(theatre, custom_parsers=custom_parsers)
            except Exception as e:
                print(e)
                continue
