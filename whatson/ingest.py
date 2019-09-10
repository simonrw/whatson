#!/usr/bin/env python


import sys
import abc
import click
import json
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
import requests
import re
from datetime import date
from typing import NamedTuple
from .models import Base, Show, session, engine
from sqlalchemy.exc import IntegrityError  # type: ignore


CURRENT_YEAR = date.today().year

rsess = requests.Session()
rsess.headers[
    "User-Agent"
] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0"


class DateRange(NamedTuple):
    start: date
    end: date


def date_text_to_date(date_text, year=None):
    date_text = date_text.strip().lower()
    if "-" in date_text:
        parts = date_text.split("-")
        if year is None:
            match = re.search(r"20\d{2}", date_text)
            if not match:
                year = CURRENT_YEAR
            else:
                year = int(match.group(0))

        return DateRange(
            start=date_text_to_date(parts[0], year),
            end=date_text_to_date(parts[1], year),
        )
    else:
        match = re.search(
            r"(?P<day_str>\d+)\w*\s*(?P<month_str>\w+)\s*(?P<year_str>\d+)?", date_text
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


class Parser(abc.ABC):
    def __init__(self, url, root_url):
        self.url = url
        self.root_url = root_url

    def parse(self):
        r = rsess.get(self.url)
        r.raise_for_status()

        html = r.text
        self.soup = BeautifulSoup(html, "html.parser")

        return self.scrape()

    def next_page(self, url):
        r = rsess.get(url)
        r.raise_for_status()

        html = r.text
        self.soup = BeautifulSoup(html, "html.parser")

    @abc.abstractmethod
    def scrape(self):
        pass


class ParseBelgrade(Parser):
    def scrape(self):
        container = self.soup.find("div", class_="list-productions")
        year = -1
        for elem in container.contents:
            if isinstance(elem, Tag):
                if elem.attrs.get("id") == "production-navigation":
                    continue

                if elem.name == "h2":
                    text = elem.text.lower()
                    _, year_text = text.split()
                    year = int(year_text)
                else:
                    if "production-list-item" not in elem.attrs["class"]:
                        continue

                    title = elem.find("h3").text.strip()
                    date_text = elem.find("p", class_="date").text.strip().lower()

                    link_url = elem.find("a", class_="production-link").attrs["href"]
                    link_url = "".join([self.root_url, link_url])

                    image_url = (
                        elem.find("a", class_="production-link")
                        .find("img")
                        .attrs["src"]
                    )
                    image_url = "".join([self.root_url, image_url])

                    date = date_text_to_date(date_text, year)

                    if isinstance(date, DateRange):
                        yield Show(
                            name=title,
                            image_url=image_url,
                            link_url=link_url,
                            start_date=date.start,
                            end_date=date.end,
                        )
                    else:
                        yield Show(
                            name=title,
                            image_url=image_url,
                            link_url=link_url,
                            start_date=date,
                            end_date=date,
                        )


class ParseAlbany(Parser):
    def scrape(self):
        container = self.soup.find("div", class_="query_block_content")
        for elem in container.children:
            if isinstance(elem, Tag):
                try:
                    date_str = elem.find(class_="show-date").text.lower()
                    title = elem.find("h4").find("a").text
                    image_url = elem.find("img").attrs["src"]
                    image_url = "".join([self.root_url, image_url])

                    link_url = elem.find("h4").find("a").attrs["href"]
                    link_url = "".join([self.root_url, link_url])

                    date = date_text_to_date(date_str)
                    if isinstance(date, DateRange):
                        yield Show(
                            name=title,
                            image_url=image_url,
                            link_url=link_url,
                            start_date=date.start,
                            end_date=date.end,
                        )
                    else:
                        yield Show(
                            name=title,
                            image_url=image_url,
                            link_url=link_url,
                            start_date=date,
                            end_date=date,
                        )
                except AttributeError:
                    continue


class ParseHippodrome(Parser):
    def scrape(self):
        while True:
            container = self.soup.find("ul", class_="main-events-list")
            for elem in container.find_all("li", class_="events-list-item"):
                item = elem.find("div", class_="performance-listing")

                try:
                    image_url = elem.find("a", class_="block").find("img").attrs["src"]
                except AttributeError:
                    image_url = ""

                link_url = item.find("a", class_="block").attrs["href"]

                details = item.find("div", class_="event-details")
                title = details.find("h5", class_="performance-listing-title").text
                date = date_text_to_date(
                    details.find("p", class_="performance-listing-date").text
                )

                if isinstance(date, DateRange):
                    yield Show(
                        name=title,
                        image_url=image_url,
                        link_url=link_url,
                        start_date=date.start,
                        end_date=date.end,
                    )
                else:
                    yield Show(
                        name=title,
                        image_url=image_url,
                        link_url=link_url,
                        start_date=date,
                        end_date=date,
                    )

            next_link = self.soup.find("a", class_="next")
            if next_link:
                next_url = next_link.attrs["href"]
                self.next_page(next_url)
            else:
                break


@click.command()
@click.argument("filename")
@click.option("--reset/--no-reset")
def main(filename, reset):
    if reset:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    parsers = {
        # "belgrade": ParseBelgrade,
        # "albany": ParseAlbany,
        "hippodrome": ParseHippodrome,
    }

    with open(filename) as infile:
        config = json.load(infile)

    for theatre in config["theatres"]:
        print(theatre)
        name = theatre["name"]
        url = theatre["url"]
        root_url = theatre["root_url"]

        parser = parsers.get(name)
        if not parser:
            continue
            raise NotImplementedError(name)
        parsed = parser(url, root_url).parse()

        for item in parsed:
            try:
                with session() as sess:
                    item.theatre = name
                    sess.add(item)
            except IntegrityError:
                continue
