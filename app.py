from flask import *

app = Flask(__name__)


@app.route("/")
def homepage():
    return "Home Page here..."

if __name__ == "__main__":
    app.run(debug=True)