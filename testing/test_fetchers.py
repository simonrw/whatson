from whatson.fetchers import RequestsFetcher, SeleniumFetcher, Fetcher


def test_can_create_requests_fetcher():
    assert isinstance(Fetcher.create("requests"), RequestsFetcher)


def test_can_create_selenium_fetcher():
    assert isinstance(Fetcher.create("selenium"), SeleniumFetcher)
