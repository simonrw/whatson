from typing import Any, Iterable, NamedTuple
from ..models import Show
from ..fetchers import Fetcher
from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import date
import re


CURRENT_YEAR = date.today().year
YEAR_RE = re.compile(r"20\d{2}")


class DateRange(NamedTuple):
    start: date
    end: date


class Parser(object):
    def __init__(self, definition: "TheatreDefinition") -> None:
        self._defn = definition

    def parse(self, html: str, fetcher: Fetcher) -> Iterable[Show]:
        while True:
            soup = BeautifulSoup(html, "lxml")
            container = soup.select_one(self._defn.container_selector)
            print(container)
            for elem in container.children:
                if not isinstance(elem, Tag):
                    continue

                try:
                    title = elem.select_one(self._defn.title_selector).text

                    image_url = self._relative_or_absolute_link(
                        elem.select_one(self._defn.image_selector).attrs["src"]
                    )

                    link_url = self._relative_or_absolute_link(
                        elem.select_one(self._defn.link_selector).attrs["href"]
                    )

                    date_str = elem.select_one(self._defn.date_selector).text.lower()
                    date = self._date_text_to_date(date_str)

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

            if self._defn.next_selector is None:
                # no pagination so just quit
                return
            else:
                next_link = soup.select_one(self._defn.next_selector)
                if not next_link:
                    return
                next_url = next_link.attrs["href"]
                html = fetcher.fetch(next_url)


    def _relative_or_absolute_link(self, link: str) -> str:
        if self._defn.link_relative:
            return self._defn.root_url + link
        else:
            return link

    def _date_text_to_date(self, date_text, year=None):
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
                start = self._date_text_to_date(parts[0], year=start_year)

                if end_year_match:
                    end = self._date_text_to_date(
                        parts[1], year=int(end_year_match.group(0))
                    )

                else:
                    end = self._date_text_to_date(parts[1], year=start_year)
            else:

                if end_year_match:
                    start_year = int(end_year_match.group(0))
                else:
                    try:
                        start_year = year if year is not None else start_year
                    except UnboundLocalError:
                        start_year = CURRENT_YEAR
                start = self._date_text_to_date(parts[0], year=start_year)

                if end_year_match:
                    end = self._date_text_to_date(
                        parts[1], year=int(end_year_match.group(0))
                    )
                else:
                    end = self._date_text_to_date(parts[1], year=start_year)

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
