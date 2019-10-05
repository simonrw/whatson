from typing import Dict
import requests
import abc


class Fetcher(abc.ABC):
    @classmethod
    def create(cls, name: str) -> "Fetcher":
        try:
            return {"requests": RequestsFetcher, "selenium": SeleniumFetcher}[name]()
        except KeyError:
            raise ValueError("no fetcher configured: {}".format(name))

    @abc.abstractmethod
    def fetch(self, url: str) -> str:
        pass


class SeleniumFetcher(Fetcher):
    def fetch(self, url: str) -> str:
        raise NotImplementedError()


SESSION = requests.Session()
SESSION.headers[
    "User-Agent"
] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0"


class RequestsFetcher(Fetcher):
    def fetch(self, url: str) -> str:
        r = SESSION.get(url)
        r.raise_for_status()
        return r.text
