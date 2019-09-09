from flask import jsonify, Flask, render_template


app = Flask("whatson")


@app.route("/")
def index():
    return render_template("index.html")
