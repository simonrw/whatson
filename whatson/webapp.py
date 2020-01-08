from flask import jsonify, Flask, render_template, request
import json
from typing import NamedTuple
from .db import DB
import datetime
from functools import wraps


app = Flask("whatson")


@app.route("/")
def index():
    return render_template("index.html")


class ShowPresenter(object):
    def __init__(self, show):
        self.show = show

    def serialise(self):
        return {
            "name": self.show["title"],
            "theatre": self.show["theatre"],
            "image_url": self.show["image_url"],
            "link_url": self.show["link_url"],
            "start_date": self.show["start_date"].isoformat(),
            "end_date": self.show["end_date"].isoformat(),
        }


class ShowEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ShowPresenter):
            return o.serialise()
        else:
            return super().default(o)


app.json_encoder = ShowEncoder

# Wrapper decorator that turns any exceptions into JSON messages
def json_errors(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify(status="error", msg=str(e)), 500

    return inner


def jsonify_ok(**kwargs):
    """Wrapper function to ensure that the `status` key is present in the API result
    """
    kwargs.pop("status", None)
    return jsonify(status="ok", **kwargs)


@app.route("/api/shows", methods=["POST"])
@json_errors
def get_by_month():
    month = int(request.json["month"])
    year = int(request.json["year"])

    with DB as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM shows
                    WHERE total_months(start_date) <= total_months(%(date_ref)s)
                    AND total_months(end_date) >= total_months(%(date_ref)s)
                    ORDER BY start_date ASC
                    """,
                {"date_ref": datetime.date(year, month, 1)},
            )
            rows = cursor.fetchall()

    return jsonify_ok(shows=[ShowPresenter(show) for show in rows])


def interpolate_months(seen_months):
    """Helper function to interpolate months that do not have a start or end
    date, but are in the middle of a show run.
    """
    # Make sure to interpolate the in-between months
    current = seen_months[0]
    current_year, current_month = current["year"], current["month"]

    end = seen_months[-1]

    while True:
        if current_year > end["year"]:
            break

        if current_year == end["year"] and current_month > end["month"]:
            break

        yield {"year": current_year, "month": current_month}

        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1


@app.route("/api/months", methods=["GET"])
@json_errors
def get_months():
    with DB as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT
                            EXTRACT(MONTH FROM start_date)::int AS month,
                            EXTRACT(YEAR FROM start_date)::int AS year
                        FROM shows
                        UNION
                        SELECT
                            EXTRACT(MONTH FROM end_date)::int AS month,
                            EXTRACT(YEAR FROM end_date)::int AS year
                        FROM shows
                    ORDER BY year, month
                    """
            )
            rows = cursor.fetchall()

    dates = interpolate_months(rows)

    return jsonify_ok(dates=list(dates))
