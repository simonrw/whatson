import abc
from .fetchers import RequestsFetcher, SeleniumFetcher, RequestsHTMLFetcher
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
from .models import Show
from .date_parsers import (
    HippodromeDateParser,
    DefaultDateParser,
    ResortsworldDateParser,
    DateRange,
)


class Parser(abc.ABC):

    FETCHER = None
    DATE_PARSER = None

    def __init__(self, url, root_url):
        # Validate the class setup
        if self.FETCHER is None:
            raise ValueError("Parser `FETCHER` parameter is not set")

        if self.DATE_PARSER is None:
            raise ValueError("Parser `DATE_PARSER` parameter is not set")

        self.url = url
        self.root_url = root_url
        self.fetcher = self.FETCHER()
        self.soup = None

    @classmethod
    def from_config(cls, config_dict):
        return cls(url=config_dict["url"], root_url=config_dict["root-url"])

    def parse(self):
        html = self.fetcher.fetch(self.url)
        self.soup = BeautifulSoup(html, "lxml")

        return self.scrape()

    def next_page(self, url):
        html = self.fetcher.fetch(url)
        self.soup = BeautifulSoup(html, "lxml")

    @abc.abstractmethod
    def scrape(self):
        pass


## Custom parser


class ParseAlbany(Parser):

    FETCHER = RequestsFetcher
    DATE_PARSER = DefaultDateParser

    def scrape(self):
        container = self.soup.find("div", class_="query_block_content")
        for elem in container.children:
            if isinstance(elem, Tag):
                try:
                    date_str = elem.find(class_="show-date").text.lower()
                except AttributeError:
                    continue

                title = elem.find("h4").find("a").text
                image_url = elem.find("img").attrs["src"]
                image_url = "".join([self.root_url, image_url])

                link_url = elem.find("h4").find("a").attrs["href"]
                link_url = "".join([self.root_url, link_url])

                date = self.DATE_PARSER.date_text_to_date(date_str)
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


class ParseBelgrade(Parser):

    FETCHER = RequestsFetcher
    DATE_PARSER = DefaultDateParser

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

                    date = self.DATE_PARSER.date_text_to_date(date_text, year)

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


class ParseHippodrome(Parser):

    FETCHER = RequestsFetcher
    DATE_PARSER = HippodromeDateParser

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
                date = self.DATE_PARSER.date_text_to_date(
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


class ParseResortsWorldArena(Parser):

    FETCHER = SeleniumFetcher
    DATE_PARSER = ResortsworldDateParser

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

            date = self.DATE_PARSER.date_text_to_date(date_text)

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


class ParseArenaBirmingham(Parser):

    FETCHER = SeleniumFetcher
    # Use the same date parser as resortsworld
    DATE_PARSER = ResortsworldDateParser

    def scrape(self):
        supercontainer = self.soup.find("div", class_="content-area")
        if supercontainer is None:
            raise ValueError("cannot find supercontainer in HTML content")
        container = supercontainer.find("div", class_="events-wrap")

        events = container.find_all("div", class_="event-card")
        if not events:
            raise ValueError("cannot find events")

        for event in events:
            link_tag = event.find("a", class_="eventhref")
            link_url = "".join([self.root_url, link_tag.attrs["href"]])

            name = event.find("span", class_="title").text

            image_url = event.find("div", class_="image").find("img", class_="lazy").attrs["src"]

            date_text = event.find("div", class_="information").find("span", class_="date").text

            date = self.DATE_PARSER.date_text_to_date(date_text)

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
