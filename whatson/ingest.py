#!/usr/bin/env python


import abc
from functools import partial
import click
import json
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
import requests
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from typing import NamedTuple
from .models import Base, Show, session, engine
from .theatredef import TheatreDefinition
from .parsers import PARSERS
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


def upload_theatre(theatre, parsers):
    name = theatre.name
    print(name)
    if name not in parsers:
        raise ValueError("cannot find parser for theatre {}".format(name))

    url = theatre.url
    root_url = theatre.root_url

    parser = parsers[name]
    try:
        parsed = parser(url, root_url).parse()
        for item in parsed:
            try:
                with session() as sess:
                    item.theatre = name
                    sess.add(item)
            except IntegrityError:
                continue
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        print(e)


@click.command()
@click.argument("filename")
@click.option("--reset/--no-reset")
def main(filename, reset):
    if reset:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    with open(filename) as infile:
        theatres = TheatreDefinition.parse_config(infile)

    fn = partial(upload_theatre, parsers=PARSERS)

    with ThreadPoolExecutor() as pool:
        pool.map(fn, theatres)
