import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import cop, login_required

from datetime import datetime

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["cop"] = cop

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///mybudget.db")


# Log in page - Session
@app.route("/login", methods=["GET", "POST"])
def login():

    # erase all the data from previous session
    session.clear()

    if request.method == "POST":

        # Validate user's information
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("login.html", error = True, msgerror = "Please fill the bank")
        # The user name already exist
        repited = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(repited) != 1:
            return render_template("login.html", error = True, msgerror = "Username not found")
        # The username and password don't match
        elif check_password_hash(repited[0]["hash"], request.form.get("password")) == False:
            return render_template("login.html", error = True, msgerror = "Username and Password don't match")

        # Remember which user has logged in
        session["user_id"] = repited[0]["id"]

        return redirect("/")
    else:
        return render_template("login.html")


# Log out
@ app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # validate user's information
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return render_template("register.html", error= True, msgerror="Please fill all the blanks")
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", error= True, msgerror="Password and confirmation don't match")

        # Look if there is another username with the same text
        repited = db.execute("SELECT COUNT(username) FROM users WHERE username = ?", request.form.get("username"))
        if repited[0]["COUNT(username)"] > 0:
            return render_template("register.html", error= True, msgerror="Username already exits")

        # if the user has provided a username and password correctly, then it update the dataBase
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

            return redirect("/login")


# Index page . Session required
@app.route("/", methods=["GET"])
@login_required
def index():
    # Look the info of the user
    user = db.execute("SELECT username, date, cash FROM users WHERE id = ?", session["user_id"])
    # Look for info of the transactions
    history = db.execute("SELECT date, money, description, account, subaccount FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT 10", session["user_id"])
    # Look for info in the accounts and subaccounts tables
    accounts = db.execute("SELECT id, name, description FROM accounts WHERE user_id = ?", session["user_id"])
    subaccounts = db.execute("SELECT id, name_purpose, account FROM subaccounts WHERE user_id  =?", session["user_id"])

    earn = db.execute("SELECT COALESCE(SUM(money),0) FROM transactions WHERE user_id = ? AND money > 0", session["user_id"])[0]["COALESCE(SUM(money),0)"]
    pay = db.execute("SELECT COALESCE(SUM(money),0) FROM transactions WHERE user_id = ? AND money < 0", session["user_id"])[0]["COALESCE(SUM(money),0)"]
    summary = {
        "earn": earn,
        "pay": pay,
        "total": user[0]["cash"]
    }
    # db.execute("UPDATE users SET date = ?", datetime.now() )
    return render_template("index.html", date = user[0]["date"], history = history, accounts = accounts, subaccounts = subaccounts, summary = summary, today = datetime.now().strftime("%Y-%m-%d"))


# Add tranfer according the form in index
@app.route("/addtransfer", methods=["POST"])
@login_required
def addtransfer():

    if request.method == "POST":
        # Validate the user info
        date = request.form.get("input_date")
        description = request.form.get("input_description")
        amount = int(request.form.get("input_amount"))
        kind_transfer = int(request.form.get("input_trans"))
        account = request.form.get("input_account")
        purpose = request.form.get("input_purpose")

        # Look for info in the accounts, subaccounts and transfer tables
        accounts = db.execute("SELECT id, name, description FROM accounts WHERE user_id = ?", session["user_id"])
        subaccounts = db.execute("SELECT id, name_purpose, account FROM subaccounts WHERE user_id  =?", session["user_id"])
        history = db.execute("SELECT date, money, description, account, subaccount FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT 10", session["user_id"])

        if not date or not description or not amount or not kind_transfer or not account:
            return render_template("index.html", error = True, msgerror = "Please fill the required blanks", accounts = accounts, subaccounts = subaccounts, history = history, today = datetime.now().strftime("%Y-%m-%d"))
        elif amount <= 0:
            return render_template("index.html", error = True, msgerror = "The amount should be positive", accounts = accounts, subaccounts = subaccounts, history = history, today = datetime.now().strftime("%Y-%m-%d"))

        # Consider if is credit or a debit
        money = amount * kind_transfer
        # Look the actual cash of the user
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = cash[0]["cash"] + money;
        # Update the cash or money available
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])
        # Add the transaction in the dataBase
        db.execute("INSERT INTO transactions (user_id, date, money, description, account, subaccount) VALUES (?, ?, ?, ?, ?, ?)",session["user_id"], date, money, description, account, purpose)
        # Select all the transactions in DESC order
        history = db.execute("SELECT date, money, description, account, subaccount FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT 10", session["user_id"])

        earn = db.execute("SELECT COALESCE(SUM(money),0) FROM transactions WHERE user_id = ? AND money > 0", session["user_id"])[0]["COALESCE(SUM(money),0)"]
        pay = db.execute("SELECT COALESCE(SUM(money),0) FROM transactions WHERE user_id = ? AND money < 0", session["user_id"])[0]["COALESCE(SUM(money),0)"]
        summary = {
            "earn": earn,
            "pay": pay,
            "total": cash
        }

        # Update the last date of edition
        db.execute("UPDATE users SET date = ? WHERE id = ?", datetime.now(), session["user_id"] )
        # Return to the index
        return render_template("index.html", date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"), history = history, accounts = accounts, subaccounts = subaccounts, summary = summary, today = datetime.now().strftime("%Y-%m-%d"))


# Show the history of thw transactions
@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    # Look for info in the accounts and subaccounts tables
    accounts = db.execute("SELECT id, name, description FROM accounts WHERE user_id = ?", session["user_id"])
    if request.method == "GET":
        # Look the data available in the data Base
        history = db.execute("SELECT trans_id, date, money, description, account, subaccount FROM transactions WHERE user_id = ? ORDER BY date DESC", session["user_id"])
        return render_template("history.html", history = history, accounts = accounts)
    elif request.method == "POST":
        # Is going to delete or edit one transaction
        trans_edit = int(request.form.get("id"))
        action = int(request.form.get("action"))
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])


        # If the user delete some line
        if action == 0:
            # Delete the transaction
            db.execute("DELETE FROM transactions WHERE trans_id = ?", trans_edit)
            # Update the cash on the user table
            money = int(request.form.get("money"))
            db.execute("UPDATE users SET cash = ? WHERE id = ?",cash[0]["cash"] - money, session["user_id"])

            #Look the data and show it
            history = db.execute("SELECT trans_id, date, money, description, account, subaccount FROM transactions WHERE user_id = ? ORDER BY date DESC", session["user_id"])
            return render_template("history.html", history = history, accounts=accounts)

        # If the user change some values in one line
        elif action == 1:
            # Validate the user info
            date = request.form.get("input_date")
            description = request.form.get("input_description")
            amount = int(request.form.get("input_amount"))
            account = request.form.get("input_account")
            purpose = request.form.get("input_purpose")
            trans_id = request.form.get("id")

            # Show the error
            if not date or not description or not amount or not account:
                error = True
                msgerror = "Please fill the required blanks"
            # Falta validar las opciones de account y porpouse
            else:
                error = False
                msgerror = ""
                db.execute("UPDATE transactions SET date = ?, money = ?, description = ?, Account = ?, Subaccount = ? WHERE user_id = ? AND trans_id = ?", date, amount, description, account, purpose, session["user_id"], trans_id)
                # Update the cash on the user table
                money = int(request.form.get("money"))
                db.execute("UPDATE users SET cash = ? WHERE id = ?",cash[0]["cash"] - money + amount, session["user_id"])
            #Look the data and show it
            history = db.execute("SELECT trans_id, date, money, description, account, Subaccount FROM transactions WHERE user_id = ? ORDER BY date DESC", session["user_id"])
            return render_template("history.html", history = history, error = error, msgerror = msgerror, accounts = accounts)
        # if the user push edit in another line
        else:
            history = db.execute("SELECT trans_id, date, money, description, account, subaccount FROM transactions WHERE user_id = ? ORDER BY date DESC", session["user_id"])
            # Look for info in the accounts and subaccounts tables
            subaccounts = db.execute("SELECT id, name_purpose, account FROM subaccounts WHERE user_id  =?", session["user_id"])
            return render_template("history_change.html", history = history, trans_edit = trans_edit, accounts = accounts, subaccounts = subaccounts)


# Add an account or a purpose
@app.route("/add_account", methods=["GET", "POST"])
@login_required
def add():
     # Look for info in the accounts and subaccounts tables
    accounts = db.execute("SELECT id, name, description FROM accounts WHERE user_id = ?", session["user_id"])
    subaccounts = db.execute("SELECT subaccounts.id, name_purpose, name FROM subaccounts JOIN accounts ON subaccounts.account = accounts.id WHERE subaccounts.user_id  = ? ", session["user_id"])
    if request.method == "GET":
        # Direct the user to add account, porpuse page
        return render_template("add_account.html", accounts = accounts, subaccounts = subaccounts)
    elif request.method == "POST":
        # Know which button was pressed
        action = int(request.form.get("action"))

        if action == 1:
            # Add account
            account = request.form.get("input_account")
            description = request.form.get("input_description")
            # Validate the data
            if not account:
                return render_template("add_account.html", error = True, msgerror = "Please fill the Account name blank", accounts = accounts, subaccounts = subaccounts)
            else:
                for name in accounts:
                    if name["name"] == account:
                        return render_template("add_account.html", error = True, msgerror = "Account name already used, choose another one...", accounts = accounts, subaccounts = subaccounts)
                # It is correct the name of the account
                db.execute("INSERT INTO accounts (user_id, name, description) VALUES (?, ?, ?)", session["user_id"], account, description)
                return redirect("/")
        elif action == 2:
            # Add purpose
            purpose = request.form.get("input_purpose")
            account_purpose = request.form.get("input_account_purpose")
            # Validate the users data
            if not purpose:
                return render_template("add_account.html", error = True, msgerror = "Please fill the Purpose name blank", accounts = accounts, subaccounts = subaccounts)
            else:
                for name in subaccounts:
                    if name["name"] == purpose:
                        return render_template("add_account.html", error = True, msgerror = "Purpose name already used, choose another one...", accounts = accounts, subaccounts = subaccounts)
                # It is correct the name of the account
                db.execute("INSERT INTO subaccounts (user_id, name, account) VALUES (?, ?, ?)", session["user_id"], purpose, account_purpose)
                return redirect("/")
        elif action == 3:
            # Delete account
            row_id = request.form.get("row_id")
            db.execute("DELETE FROM accounts WHERE id = ?",row_id)
            accounts = db.execute("SELECT id, name, description FROM accounts WHERE user_id = ?", session["user_id"])
        elif action == 4:
            # Delete account
            row_id = request.form.get("row_id")
            db.execute("DELETE FROM subaccounts WHERE id = ?",row_id)
            subaccounts = db.execute("SELECT subaccounts.id, name_purpose, name FROM subaccounts JOIN accounts ON subaccounts.account = accounts.id WHERE subaccounts.user_id  = ? ", session["user_id"])


        # They can add, edit or delete account
        return render_template("add_account.html",accounts = accounts, subaccounts = subaccounts)


# Accounts filter
@app.route("/account_filter", methods=["GET", "POST"])
@login_required
def filter():
    if request.method == "GET":
        if "account" in request.args:
            account = request.args["account"]
            # Look for info in the accounts and subaccounts tables
            accounts = db.execute("SELECT id, name, description FROM accounts WHERE user_id = ?", session["user_id"])
            # Look the data available in the data Base
            history = db.execute("SELECT trans_id, date, money, description, subaccount FROM transactions WHERE user_id = ? AND account = ? ORDER BY date DESC", session["user_id"], account)
            # Look the summary of the account
            earn = db.execute("SELECT COALESCE(SUM(money),0) FROM transactions WHERE user_id = ? AND money > 0 AND account = ?", session["user_id"], account)[0]["COALESCE(SUM(money),0)"]
            pay = db.execute("SELECT COALESCE(SUM(money),0) FROM transactions WHERE user_id = ? AND money < 0 AND account = ?", session["user_id"], account)[0]["COALESCE(SUM(money),0)"]
            summary = {
                "earn": earn,
                "pay": pay,
                "total": earn + pay
            }
            return render_template("account_filter.html", history = history, account = account, accounts = accounts, summary = summary, today = datetime.now().strftime("%Y-%m-%d"))
        else:
            return redirect("/history")
    elif request.method == "POST":
        account = request.form.get("account")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        if not start_date or not end_date:
            return redirect("/account_filter?account="+account)
        else:
            # Look for info in the accounts and subaccounts tables
            accounts = db.execute("SELECT id, name, description FROM accounts WHERE user_id = ?", session["user_id"])
            # Look the data available in the data Base
            history = db.execute("SELECT trans_id, date, money, description, subaccount FROM transactions WHERE user_id = ? AND account = ? AND date >= ? AND date <= ? ORDER BY date DESC", session["user_id"], account, start_date, end_date)
            # Look the summary of the account
            earn = db.execute("SELECT COALESCE(SUM(money),0) FROM transactions WHERE user_id = ? AND money > 0 AND account = ? AND date >= ? AND date <= ?", session["user_id"], account, start_date, end_date)[0]["COALESCE(SUM(money),0)"]
            pay = db.execute("SELECT COALESCE(SUM(money),0) FROM transactions WHERE user_id = ? AND money < 0 AND account = ? AND date >= ? AND date <= ?", session["user_id"], account, start_date, end_date)[0]["COALESCE(SUM(money),0)"]
            summary = {
                "earn": earn,
                "pay": pay,
                "total": earn + pay
            }
            return render_template("account_filter.html", history = history, account = account, accounts = accounts, summary = summary, today = datetime.now().strftime("%Y-%m-%d"))