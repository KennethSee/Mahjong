import os
from datetime import datetime

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import *

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

# Custom filter
# app.jinja_env.filters["currencify"] = currencify

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to sqlite database
db = sqlite3.connect('mahjong.db', check_same_thread=False)

@app.route("/")
@login_required
def index():
    return redirect("/index")

@app.route("/index", methods=["GET"])
@login_required
def table():
    user_id = session["user_id"]
    userinfo = db.execute("SELECT DisplayName, GamesCompleted, Cash FROM Users WHERE ID = ?", (user_id,)).fetchall()
    return render_template("index.html", displayname = userinfo[0])
@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT ID, UserName, Password FROM Users WHERE UserName = ?",
                          (request.form.get("username"),)).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST
    if request.method == "POST":
        # Ensure username was created
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was created
        elif not request.form.get("password"):
            return apology("must provide password", 400)
            
        # Ensure password was confirmed
        elif not request.form.get("confirmation"):
            return apology("must enter confirmation", 400)
        
        dsiplayName = request.form.get("displayname")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        # Ensure passwords match
        if password != confirmation:
            return apology("passwords do not match", 400)

        # Reject duplicate username
        checkAvailability = db.execute("SELECT COUNT(*) AS count FROM users WHERE Username = ?", (username,)).fetchall()
        if checkAvailability[0][0] > 0:
            return apology("username already exists", 400)
            
        # Insert new user into db
        hashed_pw = generate_password_hash(password)
        db.execute("INSERT INTO users(UserName, Password, DisplayName, Cash) VALUES(?, ?, ?, ?)", (username, hashed_pw, displayName, 1000))
        db.commit()
        
        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)