from typing import Dict


class Fetcher(object):
    @classmethod
    def create(cls, name):
        try:
            return {"requests": RequestsFetcher, "selenium": SeleniumFetcher}[name]()
        except KeyError:
            raise ValueError("no fetcher configured: {}".format(name))


class SeleniumFetcher(Fetcher):
    pass


class RequestsFetcher(Fetcher):
    pass
