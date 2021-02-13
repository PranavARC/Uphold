from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

# Flask and SQLAlchemy code
app = Flask(__name__)
app.secret_key = "treehacks"
app.permanent_session_lifetime = timedelta(days=3)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class users(db.Model):
    user = db.Column(db.String(100), primary_key=True)
    pwd = db.Column(db.String(100))
#     mbti = db.Column(db.String(6))
#     dnd = db.Column(db.String(15))
#     types = db.Column(db.String(10))

    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
#         self.mbti = "?"
#         self.dnd = "?"
#         self.types = "?"

@app.route('/', methods=['GET', 'POST'])
def main():
    # if "user" in session:
    #     flash("You are already logged in")
    #     return redirect(url_for("profile", name=session["user"]))
    
    if request.method == 'POST':
        session.permanent = True
        user = (request.form["username"]).strip()
        password = request.form["password"].strip()
        if(user == "" or password == ""):
            flash("Please fill out both fields")
            return redirect(url_for("main"))
        if(user.find(" ") != -1):
            flash("No whitespace allowed in username")
            return redirect(url_for("main"))

        foundUser = users.query.filter_by(user=user.lower()).first()
        if not(foundUser):
            usr = users(user.lower(), password)
            db.session.add(usr)
            db.session.commit()
        else:
            if(foundUser.pwd != password):
                flash("Incorrect password")
                return render_template("login.html")
        
        foundUser = users.query.filter_by(user=user.lower()).first()

        # session["user"] = user.lower()

        flash("You've logged in, "+ user)
        return redirect(url_for("main"))

    return render_template("login.html")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)