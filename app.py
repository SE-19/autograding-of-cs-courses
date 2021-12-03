from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file, jsonify
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import math
import random

from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import smtplib
from random import randint

from mark_assignment import extract_assignments, generate_plag_report, \
                clean_assignment_dir, get_directories, test_function, archive_reports, clean_reports_dir

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

    def __repr__(self) -> str:
        return f"{self.ta_id}, {self.name}"

class Assignment(db.Model):
    assignment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(1000), unique=True, nullable=False)
    graded=db.Column(db.Boolean,default=False,nullable=False)
    teacher_id = db.Column(db.Integer,db.ForeignKey('teacher.teacher_id'))
    # functions=db.relationship('Function',backref="assignment")

    def __repr__(self) -> str:
        return f"<Assignment {self.title}, {self.assignment_id}>"

class Function(db.Model):
    function_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    assignment_id = db.Column(db.Integer,db.ForeignKey('assignment.assignment_id'))
    docstring = db.Column(db.String(2000))
    parameters = db.Column(db.String(2000))
    func_name = db.Column(db.String(200),nullable=False)
    marks = db.Column(db.Integer,nullable=False)
    
    def __repr__(self) -> str:
        return f"<Function {self.func_name}, {self.function_id}>"

class TestFunctions(db.Model):
    func_param_rel_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    function_id = db.Column(db.Integer,db.ForeignKey('function.function_id'))
    
    def __repr__(self) -> str:
        return f"<FunctionParameterRelation {self.func_param_rel_id}>"

class Parameter(db.Model):
    param_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    func_param_rel_id= db.Column(db.Integer,db.ForeignKey('test_functions.func_param_rel_id'))
    parameter = db.Column(db.String(1000))

    def __repr__(self) -> str:
        return f"<Parameter {self.parameter}, {self.datatype}, {self.param_id}>"

class ExpectedValue(db.Model):
    expected_value_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    func_param_rel_id= db.Column(db.Integer,db.ForeignKey('test_functions.func_param_rel_id'))
    expected_value= db.Column(db.String(1000))

    def __repr__(self) -> str:
        return f"<ExpectedValue {self.expected_value}, {self.datatype}, {self.expected_value_id}>"


@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/auth", methods=["GET", "POST"])
def login_register():
    if 'logged_in_teacher_id' in session:
        return redirect(url_for("homepage"))
    if "logged_in_ta_id" in session:
        return redirect(url_for("homepage"))
    if request.method == "POST":
        error = None
        if 'email' in request.form:
            # meaning first form fill kia hai
            email = request.form['email']
            password = request.form['password']
            # print(email, password)
            teacher = Teacher.query.filter_by(email=email).first()# get record from database.
            if teacher == None:
                ta = TA.query.filter_by(email=email).first()
                if ta == None:
                    error = "Email not found!"
                    flash(error)
                else:
                    if check_password_hash(ta.password, password):
                        # print("logged in successfully")
                        session['logged_in_ta_id'] = ta.ta_id
                        flash("Log-in Successful!")
                        return redirect(url_for("homepage"))
                    else:
                        error = "The Password did not match! Please try again!"
                        flash(error)
            else:
                if check_password_hash(teacher.password, password):
                    # print("logged in successfully")
                    session['logged_in_teacher_id'] = teacher.teacher_id
                    flash("Log-in Successful!")
                    return redirect(url_for("homepage"))
                else:
                    error = "The Password did not match! Please try again!"
                    flash(error)
        elif request.form['name'] != "":
            if request.form['role'] == '1':
                name = request.form['name']
                cnic = request.form['cnic']
                department = request.form['department']
                phone_no = request.form['phone_no']
                email_add = request.form['email_add']
                password = request.form['pass']
                otp = OTPgenerator()
                new_teacher = Teacher(name=name, cnic=cnic,department=department, phone_no=phone_no, email=email_add, password=generate_password_hash(password), otp=otp)

                try:
                    db.session.add(new_teacher)
                    db.session.commit()
                except exc.IntegrityError:
                    error = "CNIC, Phone No or Email address already exist!"
                    flash(error)
            elif request.form['role'] == '2':
                name = request.form['name']
                cnic = request.form['cnic']
                department = request.form['department']
                phone_no = request.form['phone_no']
                email_add = request.form['email_add']
                password = request.form['pass']
                otp = request.form['otp']
                teacher = Teacher.query.filter_by(otp=otp).first()
                if teacher == None:
                    error = "OTP is incorrect"
                    flash("OTP is incorrect")
                else:
                    teacher.otp = OTPgenerator()
                    new_TA = TA(name=name,head_id=teacher.teacher_id, cnic=cnic,department=department, phone_no=phone_no, email=email_add, password=generate_password_hash(password))
                    try:
                        db.session.add(new_TA)
                        db.session.commit()
                    except exc.IntegrityError:
                        error = "CNIC, Phone No or Email address already exist!"
                        flash(error)

    return render_template("logreg.html")

@app.route("/create_assignment", methods=["GET", "POST"])
def create_assignment():
    # print(session)
    session['assignment'] = 'an assignment'
    if 'logged_in_teacher_id' not in session and "logged_in_ta_id" not in session:
        return redirect(url_for("login_register"))
    if "logged_in_ta_id" in session:
        error = "TA does not have access to create Assignments!"
        flash(error)
        return redirect(url_for('homepage'))
    if request.method == 'POST':
        assignment_var = request.get_json()
        assignment = Assignment(title=assignment_var['assignment_title'], teacher_id=session['logged_in_teacher_id'])
        db.session.add(assignment)
        db.session.commit()
        functions = assignment_var['functions_testcases']
        #'functions_testcases': [{'func_name': '', 'params': [], 'marks': 0, 'docstring': '', 'test_cases': []}]
        for func in range(len(functions)-1):# skip the last one..
            f = functions[func]
            # print(f)
            function = Function(assignment_id=assignment.assignment_id, parameters=f['params'], docstring=f['docstring'], marks=f['marks'], func_name=f['func_name'])
            db.session.add(function)
            db.session.commit()
            # print(function)
            for t in f['test_cases']:
                test_case = TestFunctions(function_id=function.function_id)
                db.session.add(test_case)
                db.session.commit()
                for i in t['test_params']:
                    test_param = Parameter(func_param_rel_id=test_case.func_param_rel_id, parameter=i)
                    db.session.add(test_param)
                    db.session.commit()
                ex_val = ExpectedValue(func_param_rel_id=test_case.func_param_rel_id, expected_value=t['ex_value'])
                db.session.add(ex_val)
                db.session.commit()
        print("ALLL DONEEEE")
    return render_template("create_assignment.html")

@app.route("/mark_assignment", methods=["GET", "POST"])
def mark_assignment():
    if 'logged_in_teacher_id' not in session and "logged_in_ta_id" not in session:
        return redirect(url_for("login_register"))
    if request.method == "POST":
        assignment_id = request.form['select_assignment']
        # print(assignment_id)
        plagiarism_check = 'off'
        if 'plagiarism' in request.form:
            plagiarism_check = request.form['plagiarism']
            print(plagiarism_check)
        file = request.files["filename"]
        if not check_extension(file.filename):
            flash("The extension must be a .zip or .rar file!")
        else:
            file_name = ""
            if file.filename.endswith(".zip"):
                file_name = "assignments.zip"
            if file.filename.endswith(".rar"):
                file_name = "assignments.rar"
            file.save("./assignment/" + file_name)
            # print(file_name)
            extract_assignments(file_name)
            if plagiarism_check == "on":
                generate_plag_report()
            test_function(get_test_cases(assignment_id), get_directories())
            clean_assignment_dir()
            archive_reports()
            clean_reports_dir()
            return send_file("reports.zip", as_attachment=True)
    if 'logged_in_teacher_id' in session:
        all_assignments = Assignment.query.filter_by(teacher_id=session['logged_in_teacher_id']).all()
    if 'logged_in_ta_id' in session:
        ta = TA.query.filter_by(ta_id=session['logged_in_ta_id']).first()
        all_assignments = Assignment.query.filter_by(teacher_id=ta.head_id).all()
    # print(all_assignments)
    return render_template("mark_assignment.html", assignments=all_assignments)

def check_extension(filename):
    return filename.endswith(".zip") or filename.endswith(".rar")

@app.route("/assignments")
def assignments():
    if 'logged_in_teacher_id' not in session and "logged_in_ta_id" not in session:
        return redirect(url_for("login_register"))
    if 'logged_in_teacher_id' in session:
        all_assignments = Assignment.query.filter_by(teacher_id=session['logged_in_teacher_id']).all()
        # print(all_assignments)
    if 'logged_in_ta_id' in session:
        ta = TA.query.filter_by(ta_id=session['logged_in_ta_id']).first()
        all_assignments = Assignment.query.filter_by(teacher_id=ta.head_id).all()
        # print(all_assignments)
    return render_template("assignments.html", assignments=all_assignments)

@app.route("/profile")
def profile():
    if 'logged_in_teacher_id' in session:
        user = Teacher.query.filter_by(teacher_id = session['logged_in_teacher_id']).first()
        return render_template("profile.html",c_user=user)
    elif 'logged_in_ta_id' in session:
        user = TA.query.filter_by(ta_id = session['logged_in_ta_id']).first()
        return render_template("profile.html",c_user=user)
    else:
        redirect(url_for('login_register'))


@app.route("/change_password" ,methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        cur_pass = request.form['cur_pass']
        new_pass = request.form['new_pass']
        conf_pass = request.form['conf_pass']
        # print(cur_pass,new_pass,conf_pass)
        if 'logged_in_teacher_id' in session:
            user = Teacher.query.filter_by(teacher_id = session['logged_in_teacher_id']).first()
        elif 'logged_in_ta_id' in session:
            user = TA.query.filter_by(ta_id = session['logged_in_ta_id']).first()
        if check_password_hash(user.password,cur_pass):
            if new_pass == conf_pass:
                user.password = generate_password_hash(new_pass)
                db.session.commit()
                return redirect('logout')
            else:
                flash("Password is not confirmed")
                return render_template("change_password.html")
        else:
            flash("Wrong current password")
            return render_template("change_password.html")
    return render_template("change_password.html")
# Here started the forgot password scene
@app.route('/forgotpass')
def forgotpass():
    return render_template("forgotpass.html")

def send_email(from_addr, to_addr_list,message,login, password, smtpserver='smtp.gmail.com:587'):
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    server.sendmail(from_addr, to_addr_list,message)
    server.quit()

@app.route("/accountfound",methods=['GET','POST'])
def accountfound():
    errornf=False
    accf=False
    if request.method=="POST":
        email=request.form["email"]
        query= Teacher.query.filter_by(email=email).first()
        if(query is None):
            errornf=True
            return render_template("forgotpass.html",errornf=errornf)
        else:
            accf=True
            otp=f"{randint(100,999)}-{randint(100,999)}"
            session["otp"]=otp
            session["emailtochange"]=email
            msg=f"Dear Sir,\n\t\tWe are glad that your account can be recovered. Your verification code is: {otp}"
            send_email("Auto Grade",f"{email}",msg,"autogradeforcs@gmail.com","123testing!")
            return render_template("forgotpass.html",accf=accf)
    return redirect(url_for("forgot_password"))

@app.route("/otpver",methods=['GET','POST'])
def otp_verification():
    errorincotp=False
    if request.method=="POST":
        otp=request.form["otp"]
        if(session["otp"]!=otp):
            errorincotp=True
            return render_template("forgotpass.html",errorincotp=errorincotp)
        else:
            otpiscorrect=True
            session.pop("otp",None)
            return render_template("forgotpass.html",otpiscorrect=otpiscorrect)

    if "otp" in session and "emailtochange" in session:
        session.pop("otp",None)
        session.pop("emailtochange",None)
    return redirect(url_for("forgot_password"))

@app.route("/updatepassword",methods=['GET','POST'])
def update_pass():
    if request.method=="POST":
        newpass=request.form["newpass"]
        query=Teacher.query.filter_by(email=session["emailtochange"]).first()
        query.password = generate_password_hash(newpass)
        db.session.commit()
        session.pop("emailtochange",None)
        # print("Password changed successfully.", newpass)
        return redirect(url_for("login_register"))
    if "emailtochange" in session:
           session.pop("emailtochange",None)
    return redirect(url_for("forgot_password"))

@app.route("/TA_manage", methods=['GET','POST'])
def TA_manage():
    if request.method == 'POST':
        ta_id = request.form['ta_id']
        TA.query.filter_by(ta_id = ta_id).delete()
    if "logged_in_teacher_id" not in session:
        return redirect(url_for("homepage"))
    if "logged_in_ta_id" in session:
        error = "Access Denied!"
        flash(error)
        return redirect(url_for(homepage))
    teacher = Teacher.query.filter_by(teacher_id=session['logged_in_teacher_id']).first()
    data = {}
    data['Teacher_otp'] = teacher.otp
    data['TAs'] = TA.query.filter_by(head_id = session['logged_in_teacher_id']).all()
    return render_template("TA_manage.html",data=data)
  
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_register'))

def OTPgenerator():
    string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    OTP = ""

    for c in range(22):
        OTP += string[math.floor(random.randint(0,len(string)-1))]
    return OTP
  

def get_test_cases(assignment_id):
    # assignment = Assignment.query.filter_by(assignment_id=assignment_id).first()
    # print("-"*10 + "Assignment: " + assignment.title + "-"*10)
    functions = Function.query.filter_by(assignment_id=assignment_id).all()
    test_cases = []
    for function in functions:
        # print("-"*10 + "Function: " + function.func_name + "-"*10)
        relations = TestFunctions.query.filter_by(function_id=function.function_id).all()
        marks = function.marks/len(relations)
        for r in relations:
            temp = [function.func_name]
            # print("-"*10 + "Relations: " + str(r) + "-"*10)
            params = Parameter.query.filter_by(func_param_rel_id=r.func_param_rel_id).all()
            parameters = []
            for p in params:
                parameters.append(eval(p.parameter))
            # print(parameters)
            temp.append(parameters)
            ev = ExpectedValue.query.filter_by(func_param_rel_id=r.func_param_rel_id).first()
            expected_value = eval(ev.expected_value)
            # print(expected_value)
            temp.append(expected_value)
            temp.append(marks)
            test_cases.append(temp)
    # print(test_cases)
    return test_cases

if __name__ == "__main__":
    app.run(debug=True)

