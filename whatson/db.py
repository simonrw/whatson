"""
Whatson db

This module handles talking to Postgres via `psycopg2`.
"""

import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

LOG = logging.getLogger("whatson.db")
LOG.setLevel(logging.DEBUG)


DB = psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)


def reset_database():
    """Resets the database to its basic schema"""
    with DB as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS shows")
        cursor.execute(
            """CREATE TABLE shows (
                id SERIAL PRIMARY KEY,
                theatre VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                image_url TEXT NOT NULL,
                link_url TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
        )
        cursor.execute(
            """CREATE UNIQUE INDEX _idx_shows_theatre_title
                ON shows (theatre, title)
                """
        )

        cursor.execute(
            """CREATE OR REPLACE FUNCTION total_months(date)
            RETURNS int AS
                'select (extract(year from $1) * 12 + extract(month from $1))::int'
                    language sql immutable
            """
        )
