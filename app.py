from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///autograde.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Teacher(db.Model):
    teacher_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    cnic = db.Column(db.String(13), unique=True, nullable=False)
    phone_no = db.Column(db.String(11), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self) -> str:
        return f"{self.teacher_id}, {self.name}"

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

@app.route("/assignments")
def assignments():
    return render_template("assignments.html")

if __name__ == "__main__":
    app.run(debug=True)