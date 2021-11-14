from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import math
import random

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
    otp = db.Column(db.String(25), nullable=False)


    # tas=db.relationship('TA',backref="head")
    # assignments=db.relationship('Assignment',backref="teacher")
    

    def __repr__(self) -> str:
        return f"{self.teacher_id}, {self.name}"

class TA(db.Model):
    ta_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    head_id = db.Column(db.Integer,db.ForeignKey('teacher.teacher_id'))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    cnic = db.Column(db.String(13), unique=True, nullable=False)
    phone_no = db.Column(db.String(11), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(500), nullable=False)

class Assignment(db.Model):
    assignment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(1000), unique=True, nullable=False)
    graded=db.Column(db.Boolean,default=False,nullable=False)
    teacher_id = db.Column(db.Integer,db.ForeignKey('teacher.teacher_id'))
    # functions=db.relationship('Function',backref="assignment")

class Function(db.Model):
    function_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    graded=db.Column(db.String(5),nullable=False)
    assignment_id = db.Column(db.Integer,db.ForeignKey('assignment.assignment_id'))
    docstring = db.Column(db.String(2000))
    marks = db.Column(db.Integer,nullable=False)
    # parameters_id=db.relationship('FPR',backref="function")

class Fpr(db.Model):
    func_param_rel_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    function_id = db.Column(db.Integer,db.ForeignKey('function.function_id'))
    # parameters=db.relationship('Parameter',backref="funcparamrel",uselist=False)
    # expected_values=db.relationship('ExpectedValue',backref="funcparamrel",uselist=False)

class Parameter(db.Model):
    param_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    func_param_rel_id= db.Column(db.Integer,db.ForeignKey('fpr.func_param_rel_id'))
    parameter = db.Column(db.String(1000))

class ExpectedValue(db.Model):
    expected_value_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    func_param_rel_id= db.Column(db.Integer,db.ForeignKey('fpr.func_param_rel_id'))
    expected_value= db.Column(db.String(1000))


@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/auth", methods=["GET", "POST"])
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
                ta = TA.query.filter_by(email=email).first()
                if ta == None:
                    error = "Email not found!"
                    flash(error)
                else:
                    if check_password_hash(ta.password, password):
                        print("logged in successfully")
                        session['logged_in_ta_id'] = ta.ta_id
                        flash("Log-in Successful!")
                        return redirect(url_for("homepage"))
                    else:
                        error = "The Password did not match! Please try again!"
            else:
                if check_password_hash(teacher.password, password):
                    print("logged in successfully")
                    session['logged_in_teacher_id'] = teacher.teacher_id
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
            try:
                db.session.add(new_teacher)
                db.session.commit()
            except exc.IntegrityError:
                error = "CNIC, Phone No or Email address already exist!"
                flash(error)
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

@app.route("/TA_manage")
def TA_manage():
    return render_template("TA_manage.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homepage'))

def OTPgenerator():
    string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    OTP = ""

    for c in range(22):
        OTP += string[math.floor(random.randint(0,len(string)-1))]
    return OTP

if __name__ == "__main__":
    app.run(debug=True)

