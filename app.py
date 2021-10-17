from flask import *

app = Flask(__name__)


@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/login_register")
def login_register():
    return render_template("logreg.html")

@app.route("/create_assignment")
def create_assignment():
    return render_template("create_assignment.html")

@app.route("/mark_assignment")
def mark_assignment():
    return render_template("mark_assignment.html")

if __name__ == "__main__":
    app.run(debug=True)