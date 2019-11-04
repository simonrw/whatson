import abc
from .base import Parser, DateRange
from ..fetchers import Fetcher
from ..models import Show
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Any, Iterable, NamedTuple


class ParseBelgrade(Parser):
    def parse(self, html: str, fetcher: Fetcher) -> Iterable[Show]:
        soup = BeautifulSoup(html, "lxml")
        container = soup.find("div", class_="list-productions")

        # Custom logic as the content of the page relies on storing state
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
                    link_url = "".join([self._defn.root_url, link_url])

                    image_url = (
                        elem.find("a", class_="production-link")
                        .find("img")
                        .attrs["src"]
                    )
                    image_url = "".join([self._defn.root_url, image_url])

                    date = self._date_text_to_date(date_text, year)

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
