from flask import Flask, render_template, request
from search import search


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    query_limit = 10

    query = None
    result = []
    if request.method == "POST":
        query = request.form["query"]
        result = search(query, query_limit)

    return render_template("index.html", query=query, result=result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
