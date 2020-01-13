import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from whatson.db import reset_database
import dotenv

dotenv.load_dotenv()


@pytest.fixture(scope="module")
def dburl():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        raise ValueError("no TEST_DATABASE_URL specified in environment")


@pytest.fixture(scope="module")
def connection(dburl):
    conn = psycopg2.connect(
        os.getenv("TEST_DATABASE_URL"), cursor_factory=RealDictCursor
    )
    reset_database(conn)
    try:
        yield conn
    finally:
        conn.rollback()


@pytest.fixture
def cursor(connection):
    cursor = connection.cursor()
    yield cursor
