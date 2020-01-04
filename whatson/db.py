import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()


DB = psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)


def reset_database():
    with DB as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS shows")
        cursor.execute(
            """CREATE TABLE shows (
                id SERIAL PRIMARY KEY,
                theatre VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                image_url VARCHAR(1024) NOT NULL,
                link_url VARCHAR(1024) NOT NULL,
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
