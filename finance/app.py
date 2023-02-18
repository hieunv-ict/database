import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if (request.method=="POST"):
        symbol_value=request.form.get("symbol").upper()
        item = lookup(symbol_value)

        if not symbol_value:
            return apology("Please enter a symbol!")

        elif not item:
            return apology("The symbol does not exists")

        try:
            shares = int(request.form.get("shares"))
        except:
            ("Your shares is not valid!")

        if shares <= 0:
            return apology("Shares must be a positive integer!")

        user_id = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

        item_name = item["name"]
        item_price = item["price"]
        total_price = shares * item_price


        #check if the user's cash is enough
        if (cash >= total_price):
            #update information of the transaction of that user
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash - total_price, user_id)
            db.execute("INSERT INTO transactions(user_id, name, shares, price, type, symbol) VALUES(?, ?, ?, ?, ?, ?)", user_id, item_name, shares, item_price, 'buy', symbol_value)

        else:
            return apology("Sorry, you don't have enough cash.")
        return redirect("/")

    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if (request.method == "POST"):
        symbol_value = request.form.get("symbol")

        if not symbol_value:
            return apology("Please enter a symbol")

        result = lookup(symbol_value)

        if not result:
            return apology("The symbol does not exists")
        else:
            return render_template("quoted.html",stocks=result)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if (request.method == "POST"):
        #Check for filling all the boxes:
        if not request.form.get("username"):
            return apology("Must provide username")

        elif not request.form.get("password"):
            return apology("Must provide password")

        elif not request.form.get("confirmation"):
            return apology("Must provide password confirmation")

        if request.form.get("password")!=request.form.get("confirmation"):
            return apology("The password don't match the confirmation")

        p_hash = generate_password_hash(request.form.get("password"))

        #check if the user's username has been taken yet

        try:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get("username"), p_hash)
            return redirect("/")
        except:
            apology("Sorry, username has already existed")

    else:
        return render_template("register.html")





@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
