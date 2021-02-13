from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import datetime

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
    latt = db.Column(db.Numeric(10,7))
    long = db.Column(db.Numeric(10,7))

    def __init__(self, user, pwd, first, last, gender, age):
        self.user = user
        self.pwd = pwd
        self.first = first
        self.last = last
        self.age = age
        self.gender = gender
        self.latt = -360
        self.long = -360

class pros(db.Model):
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
    client = db.Column(db.String(100))
    pro = db.Column(db.String(100))
    field = field = db.Column(db.String(100))
    job = db.Column(db.String(100))
    details = db.Column(db.String(1000))
    status = db.Column(db.String(10))
    dtime = db.Column(db.DateTime(), primary_key=True)
    atime = db.Column(db.String(25))

    def __init__(self, client, pro, field, job, details, status, atime):
        self.client = client
        self.pro = pro
        self.field = field
        self.job = job
        self.details = details
        self.status = status
        self.dtime = (datetime.datetime.now()).strftime(dt)
        self.atime = atime


@app.route('/', methods=['GET', 'POST'])
def main():
    if "user" in session:
        if request.method == 'POST':
            session.clear()
            flash("You have logged out")
            return redirect(url_for("main"))
        foundUser = users.query.filter_by(user=session["user"].lower()).first()
        if not(foundUser):
            session.clear()
            flash("An error has occurred. Please login again")
            return redirect(url_for("login"))
        arr = [foundUser.first, foundUser.last]
        allReqs = requests.query.filter_by(client=session["user"].lower()).order_by(requests.dtime.desc())
        foundPro = pros.query.filter_by(user=session["user"].lower()).first()
        if foundPro:
            allJobs = requests.query.filter_by(pro=session["user"].lower(), accept="Pending").order_by(requests.dtime.desc())
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


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)