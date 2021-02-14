from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from math import radians, cos, sin, asin, sqrt
import json
import operator

# Flask and SQLAlchemy code
app = Flask(__name__)
app.secret_key = "treehacks"
app.permanent_session_lifetime = timedelta(days=3)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_BINDS'] = {'requests' : 'sqlite:///requests.sqlite3',
                                    'pros': 'sqlite:///pros.sqlite3'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

dt = '%Y-%m-%d %H:%M:%S'

class users(db.Model):
    user = db.Column(db.String(100), primary_key=True)
    pwd = db.Column(db.String(100))
    first = db.Column(db.String(100))
    last = db.Column(db.String(100))
    age = db.Column(db.Integer())
    gender = db.Column(db.String(1))
    # latt = db.Column(db.Numeric(10,7))
    # long = db.Column(db.Numeric(10,7))

    def __init__(self, user, pwd, first, last, gender, age):
        self.user = user
        self.pwd = pwd
        self.first = first
        self.last = last
        self.age = age
        self.gender = gender
        # self.latt = -360
        # self.long = -360

class pros(db.Model):
    __bind_key__ = 'pros'
    __tablename__ = "pros"
    user = db.Column(db.String(100), primary_key=True)
    first = db.Column(db.String(100))
    last = db.Column(db.String(100))
    address = db.Column(db.String(100))
    latt = db.Column(db.Numeric(10,7))
    long = db.Column(db.Numeric(10,7))
    field = db.Column(db.String(100), primary_key=True)
    job = db.Column(db.String(100), primary_key=True)

    def __init__(self, user, first, last, latt, long, field, job):
        self.user = user
        self.first = first
        self.last = last
        self.latt = latt
        self.long = long
        self.field = field
        self.job = job

class requests(db.Model):
    __bind_key__ = 'requests'
    __tablename__ = "requests"
    client = db.Column(db.String(100), primary_key=True)
    client_first = db.Column(db.String(100))
    client_last = db.Column(db.String(100))
    pro = db.Column(db.String(100), primary_key=True)
    pro_first = db.Column(db.String(100))
    pro_last = db.Column(db.String(100))
    field = field = db.Column(db.String(100))
    job = db.Column(db.String(100))
    details = db.Column(db.String(1000))
    status = db.Column(db.String(10))
    dtime = db.Column(db.DateTime(), primary_key=True)
    atime = db.Column(db.String(25))

    def __init__(self, client, client_first, client_last, pro, pro_first, pro_last, field, job, details, status, atime):
        self.client = client
        self.client_first = client_first
        self.client_last = client_last
        self.pro = pro
        self.pro_first = pro_first
        self.pro_last = pro_last
        self.field = field
        self.job = job
        self.details = details
        self.status = status
        self.dtime = datetime.now()
        self.atime = atime

def coordDist(lat1, lat2, lon1, lon2): 
    # The math module contains a function named 
    # radians which converts from degrees to radians. 
    lon1 = radians(lon1) 
    lon2 = radians(lon2) 
    lat1 = radians(lat1) 
    lat2 = radians(lat2) 
       
    # Haversine formula  
    dlon = lon2 - lon1  
    dlat = lat2 - lat1 
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  
    c = 2 * asin(sqrt(a))  
     
    # Radius of earth in kilometers. Use 3956 for miles 
    r = 6371
       
    # calculate the result 
    return(c * r * 1.609344) 

@app.route('/', methods=['GET', 'POST'])
def main():
    if "user" in session:
        if request.method == 'POST':
            if request.form.get("logout"):
                session.clear()
                flash("You have logged out")
                return redirect(url_for("main"))
            elif request.form.get("search"):
                print("pog")
                if(request.form["latt"] == ""):
                    flash("Please press the location button first")
                    return redirect(url_for("main"))
                userLatt = round((float(request.form["latt"])), 6)
                userLong = round((float(request.form["long"])), 6)
                field = request.form["field"]
                job = request.form["job"]
                print(userLatt)
                return redirect(url_for("requester", field=field, job=job, latt = userLatt, long = userLong))

        foundUser = users.query.filter_by(user=session["user"].lower()).first()
        if not(foundUser):
            session.clear()
            flash("An error has occurred. Please login again")
            return redirect(url_for("login"))
        arr = [foundUser.first, foundUser.last]
        allReqs = (requests.query.filter_by(client=session["user"].lower()).order_by(requests.dtime.desc())).all()
        foundPro = pros.query.filter_by(user=session["user"].lower()).first()
        if foundPro:
            allJobs = (requests.query.filter_by(pro=session["user"].lower(), accept="Pending").order_by(requests.dtime.desc())).all()
            return render_template("pro_home.html", arr = arr, requests = allReqs, jobs = allJobs)

        return render_template("home.html", arr = arr, requests = allReqs)

    else:
        if request.method == 'POST':
            if request.form.get("login"):
                return redirect(url_for("login"))
            else:
                return redirect(url_for("account"))
        return render_template("anon_home.html")

@app.route('/create-account', methods=['GET', 'POST'])
def account():
    if "user" in session:
        flash("You are already logged in")
        return redirect(url_for("main"))

    if request.method == 'POST':
        user = request.form["username"].strip()
        pwd = request.form["pwd"].strip()
        age = request.form["age"].strip()
        first = request.form["first"].strip()
        last = request.form["last"].strip()
        gender = request.form["gender"]

        if(user == "" or pwd == "" or age == "" or first == "" or last == ""):
            flash("Please fill out all fields")
            return redirect(url_for("account"))
        elif(user.find(" ") != -1):
            flash("No whitespace allowed in username")
            return redirect(url_for("account"))
        elif not(age.isnumeric()):
            flash("Please make age a number")
            return redirect(url_for("account"))
        
        age = int(age)
        foundUser = users.query.filter_by(user=user.lower()).first()
        if not(foundUser):
            usr = users(user.lower(), pwd, first, last, gender, age)
            db.session.add(usr)
            db.session.commit()
        else:
            flash("Username is already in use, please choose another one")
            return redirect(url_for("account"))

        session.permanent = True
        session["user"] = user.lower()
        return redirect(url_for("main"))

    return render_template("account.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if "user" in session:
        flash("You are already logged in")
        return redirect(url_for("main"))

    if request.method == 'POST':
        user = (request.form["username"]).strip()
        pwd = request.form["pwd"].strip()
        if(user == "" or pwd == ""):
            flash("Please fill out both fields")
            return redirect(url_for("login"))
        if(user.find(" ") != -1):
            flash("No whitespace allowed in username")
            return redirect(url_for("login"))

        foundUser = users.query.filter_by(user=user.lower()).first()
        # print(users.query.filter_by(user=user.lower()).all()[0])
        if not(foundUser):
            flash("Username doesn't exist")
            return redirect(url_for("login"))
        else:
            if(foundUser.pwd != pwd):
                flash("Incorrect password")
                return redirect(url_for("login"))
        
        session.permanent = True
        session["user"] = user.lower()
        return redirect(url_for("main"))

    return render_template("login.html")

@app.route('/request/<field>-<job>/<latt>%<long>', methods=['GET', 'POST'])
def requester(field, job, latt, long):
    if "user" not in session:
        flash("You need to log in")
        return redirect(url_for("main"))
    
    profs = pros.query.filter_by(field=field, job=job).all()
    profs.sort(key = lambda pr: coordDist(float(latt), pr.latt, float(long), pr.long))
    dists = []
    for i in profs:
        dists.append(round(coordDist(float(latt), i.latt, float(long), i.long),1))

    return render_template("requests.html", fd = field, jb = job, profs=profs, dists=dists)

@app.route('/request/<field>-<job>/<pro>', methods=['GET', 'POST'])
def f_requester(field, job, pro):
    if "user" not in session:
        flash("You need to log in")
        return redirect(url_for("main"))

    currPro = pros.query.filter_by(user = pro).first()
    if request.method == 'POST':
        app_date = request.form["apptime"]
        details = request.form["details"]

        if(app_date == "" or details == ""):
            flash("Please fill out all fields")
            return redirect(url_for('f_requester', field=field, job=job, pro = pro))

        app_date = app_date.replace("T", ", ")
        foundUser = users.query.filter_by(user=session["user"].lower()).first()
        req = requests(foundUser.user, foundUser.first, foundUser.last, currPro.user, currPro.first, currPro.last, field, job, details, "Pending", app_date)
        db.session.add(req)
        db.session.commit()
        flash("Request made")
        return redirect(url_for("main"))
    
    return render_template("f_request.html", pro = currPro)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)