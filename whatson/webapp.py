from flask import jsonify, Flask, render_template, request
from .models import Show, session
from sqlalchemy import func
import json


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


@app.route("/api/calendar", methods=["POST"])
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
        print(query)
        shows = query.all()

        print(shows)

        return jsonify(status="ok", shows=[ShowPresenter(show) for show in shows])
