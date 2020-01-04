import pytest
from whatson import webapp
from whatson.models import init_test_db, Show, session


@pytest.fixture
def client():
    client = webapp.app.test_client()
    webapp.app.config["TESTING"] = True

    with webapp.app.app_context():
        init_test_db()
        yield client


def test_fetch_months(client):
    with session() as sess:
        pass
