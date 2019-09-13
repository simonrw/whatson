from flask import jsonify, Flask, render_template, request
from .models import Show, session
from sqlalchemy import func
import json
from typing import NamedTuple


app = Flask("whatson")


@app.route("/")
def index():
    return render_template("index.html")


class ShowPresenter(object):
    def __init__(self, show):
        self.show = show

    def serialise(self):
        return {
            "name": self.show.name,
            "theatre": self.show.theatre,
            "image_url": self.show.image_url,
            "link_url": self.show.link_url,
            "start_date": self.show.start_date.isoformat(),
            "end_date": self.show.end_date.isoformat(),
        }


class ShowEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ShowPresenter):
            return o.serialise()
        else:
            return super().default(o)


app.json_encoder = ShowEncoder


@app.route("/api/shows", methods=["POST"])
def get_by_month():
    try:
        month = int(request.json["month"])
        year = int(request.json["year"])
    except Exception as e:
        # TODO(srw): more robust error handling
        return jsonify(status="error", error=str(e)), 400

    with session() as sess:
        query = (
            sess.query(Show)
            .filter(func.extract("month", Show.start_date) >= month)
            .filter(func.extract("year", Show.start_date) >= year)
            .filter(func.extract("month", Show.end_date) <= month)
            .filter(func.extract("year", Show.end_date) <= year)
        )
        shows = query.all()

        return jsonify(shows=[ShowPresenter(show) for show in shows])


class DateMonthYear(NamedTuple):
    month: int
    year: int


@app.route("/api/months", methods=["GET"])
def get_months():
    with session() as sess:
        query = sess.query(Show)

        shows = query.all()

        combos = set()
        for show in shows:
            combos.add(
                DateMonthYear(month=show.start_date.month, year=show.start_date.year)
            )
            combos.add(
                DateMonthYear(month=show.end_date.month, year=show.end_date.year)
            )

        return jsonify(dates=[{"month": d.month, "year": d.year} for d in combos])
