import click
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy import create_engine, Column, Integer, String  # type: ignore
from sqlalchemy.types import Date  # type: ignore
from sqlalchemy.schema import UniqueConstraint  # type: ignore
from sqlalchemy.orm import sessionmaker, scoped_session  # type: ignore
from contextlib import contextmanager

engine = create_engine("postgres+psycopg2://whatson:Password123@localhost/whatson")
Session = scoped_session(sessionmaker(bind=engine))


@contextmanager
def session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


Base = declarative_base()


class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    theatre = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    __table_args__ = (UniqueConstraint("name", "theatre", "start_date", "end_date"),)

    def __repr__(self):
        return f"<{self.name} between {self.start_date} and {self.end_date} at {self.theatre}>"


@click.command()
def reset():
    from sqlalchemy import create_engine

    engine = create_engine("postgres+psycopg2://whatson:Password123@localhost/whatson")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
