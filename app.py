from flask import *

app = Flask(__name__)


@app.route("/")
def homepage():
    return render_template("mark_assignment.html")

if __name__ == "__main__":
    app.run(debug=True)