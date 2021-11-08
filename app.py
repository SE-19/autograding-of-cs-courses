from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
SECRET_KEY = secrets.token_urlsafe(16)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///autograde.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = SECRET_KEY
db = SQLAlchemy(app)

class Teacher(db.Model):
    teacher_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    cnic = db.Column(db.String(13), unique=True, nullable=False)
    phone_no = db.Column(db.String(11), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(500), nullable=False)

    def __repr__(self) -> str:
        return f"{self.teacher_id}, {self.name}"

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/login_register", methods=["GET", "POST"])
def login_register():
    if request.method == "POST":
        error = None
        if 'email' in request.form:
            # meaning first form fill kia hai
            email = request.form['email']
            password = request.form['password']
            print(email, password)
            teacher = Teacher.query.filter_by(email=email).first()# get record from database.
            if teacher == None:
                error = "Email not found!"
            else:
                if check_password_hash(teacher.password, password):
                    print("logged in successfully")
                    session['logged_in_user_id'] = teacher.teacher_id
                    flash("Log-in Successful!")
                    return redirect(url_for("homepage"))
                else:
                    error = "The Password did not match! Please try again!"
            flash(error)
        elif request.form['name'] != "":
            name = request.form['name']
            cnic = request.form['cnic']
            department = request.form['department']
            phone_no = request.form['phone_no']
            email_add = request.form['email_add']
            password = request.form['pass']
            new_teacher = Teacher(name=name, cnic=cnic,department=department, phone_no=phone_no, email=email_add, password=generate_password_hash(password))
            db.session.add(new_teacher)
            db.session.commit()
    return render_template("logreg.html")

@app.route("/auth")
def authentication():
    return render_template("new-log-reg.html")

@app.route("/create_assignment")
def create_assignment():
    return render_template("create_assignment.html")

@app.route("/mark_assignment")
def mark_assignment():
    return render_template("mark_assignment.html")

@app.route("/assignments")
def assignments():
    return render_template("assignments.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homepage'))
if __name__ == "__main__":
    app.run(debug=True)