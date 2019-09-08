#!/usr/bin/env python


import click
import json
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
import requests
import re
from datetime import date
from typing import NamedTuple, Union


session = requests.Session()
session.headers[
    "User-Agent"
] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0"


class DateRange(NamedTuple):
    start: date
    end: date


class Show(NamedTuple):
    name: str
    date: Union[date, DateRange]


def date_text_to_date(date_text, year=None):
    date_text = date_text.strip()
    if "-" in date_text:
        parts = date_text.split("-")
        match = re.search(r"20\d{2}", date_text)
        if not match:
            raise ValueError("cannot find year in date string")

        year = int(match.group(0))
        return DateRange(
            start=date_text_to_date(parts[0], year),
            end=date_text_to_date(parts[1], year),
        )
    else:
        match = re.match(
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
        ].index(month_str)

        if year is None and match.group("year_str") is None:
            raise ValueError("cannot determine year")

        if year is not None:
            return date(year, month + 1, day)
        else:
            year = int(match.group("year_str"))
            return date(year, month + 1, day)


def parse_belgrade(url):
    r = session.get(url)
    r.raise_for_status()

    html = r.text
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find("div", class_="list-productions")
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

                date = date_text_to_date(date_text, year)

                yield Show(name=title, date=date)


def parse_albany(url):
    r = session.get(url)
    r.raise_for_status()

    html = r.text
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find("div", class_="query_block_content")
    for elem in container.children:
        if isinstance(elem, Tag):
            try:
                date_str = elem.find(class_="show-date").text.lower()
                title = elem.find("h4").find("a").text

                date = date_text_to_date(date_str)
                yield Show(name=title, date=date)
            except AttributeError:
                continue


@click.command()
@click.argument("filename")
def main(filename):
    # parsers = {"belgrade": parse_belgrade, "albany": parse_albany}
    parsers = {"albany": parse_albany}

    with open(filename) as infile:
        config = json.load(infile)

    for theatre in config["theatres"]:
        name = theatre["name"]
        url = theatre["url"]

        parser = parsers.get(name)
        if not parser:
            continue
            raise NotImplementedError(name)
        parsed = parser(url)

        for item in parsed:
            print(item)


if __name__ == "__main__":
    main()
