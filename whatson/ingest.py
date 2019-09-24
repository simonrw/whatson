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


class ParseBelgrade(SoupParser):
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

                    date = self.date_text_to_date(date_text, year)

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


class ParseAlbany(SoupParser):
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

                    date = self.date_text_to_date(date_str)
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


class ParseHippodrome(SoupParser):
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
                date = self.date_text_to_date(
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

    def date_text_to_date(self, date_text, year=None):
        date_text = date_text.strip().lower()
        if "-" in date_text or "&" in date_text:
            if "-" in date_text:
                parts = date_text.split("-")
            elif "&" in date_text:
                parts = date_text.split("&")

            start_year_match = YEAR_RE.search(parts[0])
            end_year_match = YEAR_RE.search(parts[1])

            if start_year_match:
                start_year = int(start_year_match.group(0))
                start = self.date_text_to_date(parts[0], year=start_year)

                if end_year_match:
                    end = self.date_text_to_date(
                        parts[1], year=int(end_year_match.group(0))
                    )

                else:
                    end = self.date_text_to_date(parts[1], year=start_year)
            else:

                if end_year_match:
                    start_year = int(end_year_match.group(0))
                else:
                    start_year = CURRENT_YEAR
                start = self.date_text_to_date(parts[0], year=start_year)

                if end_year_match:
                    end = self.date_text_to_date(
                        parts[1], year=int(end_year_match.group(0))
                    )
                else:
                    end = self.date_text_to_date(parts[1], year=start_year)

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


class ParseResortsWorldArena(SeleniumParser):
    SINGLE_DATE_RE = re.compile(r"(?P<day>\d+)\s+(?P<month>\w+)\s+(?P<year>20\d{2})")
    JOINT_DATE_RE = re.compile(
        r"(?P<start_day>\d+)\s*-\s*(?P<end_day>\d+)\s+(?P<month>\w+)\s+(?P<year>20\d{2})"
    )

    def scrape(self):
        container = self.soup.find("div", id="home-results")
        if not container:
            raise ValueError("cannot find container element in HTML")

        events = container.find_all("div", class_="event-card")
        if not events:
            raise ValueError("cannot find event items")

        for event in events:
            link_tag = event.find("a", class_="eventhref")
            name = link_tag.find("span", class_="title").text
            link_url = "".join([self.root_url, link_tag.attrs["href"]])
            image_url = event.find("img", class_="lazy").attrs["src"]
            date_text = event.find("span", class_="date").text

            date = self.date_text_to_date(date_text)

            if isinstance(date, DateRange):
                yield Show(
                    name=name,
                    image_url=image_url,
                    link_url=link_url,
                    start_date=date.start,
                    end_date=date.end,
                )
            else:
                yield Show(
                    name=name,
                    image_url=image_url,
                    link_url=link_url,
                    start_date=date,
                    end_date=date,
                )

    def date_text_to_date(self, date_text):
        date_text = date_text.strip()
        single_match = self.SINGLE_DATE_RE.match(date_text)
        if single_match is not None:
            day = int(single_match.group("day"))
            year = int(single_match.group("year"))
            month = self.month_text_to_int(single_match.group("month"))
            return date(year, month, day)

        joint_match = self.JOINT_DATE_RE.match(date_text)
        if joint_match is not None:
            start_day = int(joint_match.group("start_day"))
            end_day = int(joint_match.group("end_day"))
            year = int(joint_match.group("year"))
            month = self.month_text_to_int(joint_match.group("month"))

            start = date(year, month, start_day)
            end = date(year, month, end_day)

            return DateRange(start=start, end=end)

        raise ValueError(f"Cannot parse {date_text}")

    def month_text_to_int(self, textvalue):
        return [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ].index(textvalue) + 1


def upload_theatre(theatre, parsers):
    print(theatre)
    name = theatre["name"]
    url = theatre["url"]
    root_url = theatre["root_url"]

    parser = parsers.get(name)
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


@click.command()
@click.argument("filename")
@click.option("--reset/--no-reset")
def main(filename, reset):
    if reset:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    parsers = {
        "belgrade": ParseBelgrade,
        "albany": ParseAlbany,
        "hippodrome": ParseHippodrome,
        "symphony-hall": ParseSymphonyHall,
        "resortsworld-arena": ParseResortsWorldArena,
    }

    with open(filename) as infile:
        config = json.load(infile)

    for theatre in config["theatres"]:
        upload_theatre(theatre, parsers=parsers)
