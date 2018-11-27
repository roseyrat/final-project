import os
import time

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helper import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///spaces.db")

# Does not work completely because the home button does not work. Clicking the red title gets you there
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    """ Displays locations user rated or added """
    if request.method == "GET":
        places = db.execute("SELECT name FROM locations WHERE id = :id", id=session["user_id"])
        return render_template("home.html", places=places)
    else:
        return redirect("/")

# Does not work completely because the template it renders does not work
@app.route("/lookup", methods=["GET", "POST"])
@login_required
def lookup():
    """ Allows user to look up locations """
    if request.method == "GET":
        places = db.execute("SELECT name FROM locations")
        return render_template("lookup.html", places=places)
    else:
        return redirect("location.html")

# This page should be taken down and new one put up when the averages are caluclated
@app.route("/")
@login_required
def location():
    """ Displays information about a location """
    row = db.execute("SELECT * FROM locations WHERE name = :name",
                          name=request.form.get("loaction"))
    return render_template("location.html", row=location)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """ Referenced https://stackoverflow.com/questions/4108341/generating-an-ascending-list-of-numbers-of-arbitrary-length-in-python """
    """ Allows user to add a location """
    if request.method == "POST":
        result = db.execute("INSERT INTO locations (name, comments, noise, rating, atmosphere, crowdedness, activity, time, maps, id) VALUES(:name, :comments, :noise, :rating, :atmosphere, :crowdedness, :activity, :time, :maps, :id)",
                            name=request.form.get("location"), comments=request.form.get("comments"), noise=request.form.get("noise"), rating=request.form.get("rating"), atmosphere=request.form.get("atmosphere"), crowdedness=request.form.get("crowdedness"), activity=request.form.get("activity"), time=request.form.get("time"), maps=request.form.get("map"),id=session["user_id"])
        if not result:
            return apology("could not insert into table")
        return redirect("/")
    else:
        activities = ["studying alone", "studying with friends", "hanging out", "reading", "playing games", "sleeping"]
        times = list(range(1, 24))
        return render_template("add.html", activities=activities, times=times)


@app.route("/rate", methods=["GET", "POST"])
@login_required
def rate():
    """ Allows user to rate a location """
    if request.method == "POST":
        result = db.execute("INSERT INTO locations (name, comments, noise, rating, atmosphere, crowdedness, activity, time, maps, id) VALUES(:name, :comments, :noise, :rating, :atmosphere, :crowdedness, :activity, :time, :maps, :id)",
                            name=request.form.get("location"), comments=request.form.get("comments"), noise=request.form.get("noise"), rating=request.form.get("rating"), atmosphere=request.form.get("atmosphere"), crowdedness=request.form.get("crowdedness"), activity=request.form.get("activity"), time=request.form.get("time"), maps=request.form.get("map"), id=session["user_id"])
        if not result:
            return apology("could not insert into table")
        return redirect("/")
    else:
        activities = ["studying alone", "studying with friends", "hanging out", "reading", "playing games", "sleeping"]
        times = list(range(1, 24))
        places = db.execute("SELECT name FROM locations")
        return render_template("rate.html", activities=activities, times=times, places=places)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        if not request.form.get("username"):
            return apology("must provide a username")
        p = request.form.get("password")
        if len(p) < 8:
            return apology("must provide a password with at least 8 characters")
        if not p:
            return apology("must provide a password")
        c = request.form.get("confirmation")
        if not c:
            return apology("must provide another password")
        if not p == c:
            return apology("passwords must match")
        hash1 = generate_password_hash(p)
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash1)",
                            username=request.form.get("username"), hash1=hash1)
        if not result:
            return apology("could not insert into table")
        return redirect("/login")


@app.route("/checkname", methods=["GET"])
def checkname():
    """ Referenced https://stackoverflow.com/questions/19435906/what-is-the-correct-way-to-format-true-in-json """
    """ Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    username = username.lower()
    rows = db.execute("SELECT username FROM users WHERE username = :username", username=username)
    if len(rows) != 0 or len(username) < 0:
        return jsonify(False)
    return jsonify(True)


@app.route("/checkloc", methods=["GET"])
def checkloc():
    """ Referenced https://stackoverflow.com/questions/19435906/what-is-the-correct-way-to-format-true-in-json """
    """ Return true if location is not already in the database, else false, in JSON format"""
    location = request.args.get("location")
    location = location.lower()
    rows = db.execute("SELECT name FROM location WHERE location = :location", location=location)
    if len(rows) != 0 or len(location) < 0:
        return jsonify(False)
    return jsonify(True)

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
