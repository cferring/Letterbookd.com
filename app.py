import os
import json

from cs50 import SQL
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from PIL import Image

from helpers import apology, login_required, isbnsearch, bookidlookup, desclookup, titlesearch, trendingsearch, idsearch

# Configure application
app = Flask(__name__)
if __name__ == '__main__':
    app.run(host='185.27.134.34', port=8000)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///books.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)
        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
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
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password matches confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Ensure username unique
        username = request.form.get("username")
        existing = db.execute("SELECT username FROM users")
        for name in existing:
            print("USER: ", name['username'])
            if username in name['username']:
                return apology("Username already in use", 400)

        #INSERT new username and hashed password into finance.db's users table
        #username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        #password = request.form.get("password")
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password)
        return redirect("/login")

    # if here by GET, just show the page like normal, nothing to check or submit yet
    else:
        return render_template("register.html")

@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
#@login_required
def home():
    """reroute / to /home"""
    if request.path in ["/"]:
        return redirect("/home")
    results = trendingsearch()
    if session:
        username_data = db.execute("SELECT username FROM users WHERE user_id = ?", session["user_id"])
        username = username_data[0]['username']
        return render_template("index.html", results=results, username=username)
    else:
        return render_template("index.html", results=results)


@app.route("/mylist", methods=["GET", "POST"])
@login_required
def mylist():
    """Generate list of all items in users list"""
    mylist_data = db.execute("SELECT ISBN FROM lists WHERE user_id = ?", session["user_id"])
    my_isbns = []
    my_titles = []
    my_status = []
    # Creates a list of isbns from SQL query
    for i in range(len(mylist_data)):
        my_isbns.append(mylist_data[i]['ISBN'])
        # for every item in my_list, pull full book data
        isbn_list = isbnsearch(my_isbns[i])
        # parse list with [0] into dict
        isbn_dict = isbn_list[0]
        # parse dict with ['title'] into list
        title = isbn_dict['title']
        my_titles.append(title)
        mystatus_data = db.execute("SELECT status FROM lists WHERE user_id = ? AND ISBN = ?", session["user_id"], my_isbns[i])
        my_status.append(mystatus_data[0]['status'])

    # Receive JSON request with checkbox response
    if request.method == "POST" and "status" in request.json:
        list_item = request.json['list_item']
        print("STATUS list_item: ", list_item)
        isbn = my_isbns[list_item]
        status = request.json['status']
        db.execute("UPDATE lists SET status = ? WHERE user_id = ? AND ISBN = ?", status, session["user_id"], isbn)
        #db.commit()
        return '', 200

    # Receive JSON request with delete button response
    if request.method == "POST" and "action" in request.json:
        list_item = request.json['list_item']
        isbn = my_isbns[list_item]
        db.execute("DELETE FROM lists WHERE user_id = ? AND ISBN = ?", session["user_id"], isbn)
        #db.commit()
        return '', 200
    return render_template("mylist.html", my_titles=my_titles, my_isbns=my_isbns, my_status=my_status)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Get book title from API."""
    # Receive ISBN or Text inputs
    isbn = request.form.get("isbn")
    input = request.form.get("input")

    title = []
    author_name = []
    isbn_list = []
#   id_list = []
    cover_key = []

    # if user used ISBN, use that, otherwise check if text
    if isbn:
        isbn_list = isbnsearch(isbn)
        results = isbn_list
    # if user typed title w no ISBN, search our function
    elif input:
        search_results = titlesearch(input)

        for book in search_results:
            title.append(book['title'])
            author_name.append(book['author_name'])
            isbn_list.append(book['isbn'])
#           id_list.append(book['key'][7:])
            cover_key.append(book['cover_key'])

        results = search_results
        identifier = bookidlookup(isbn)
    else:
        return render_template("search.html")

    return render_template("search.html", results=results, isbn=isbn, input=input, author_name=author_name, title=title, isbn_list=isbn_list, cover_key=cover_key)


@app.route("/book", methods=["GET", "POST"])
@login_required
def book():
    """Generate book info page from get value submitted by search form"""
    if request.args.get("q")[0] == 'O':
        isbn = 'None'
        id = request.args.get("q")
        identifier = id
        description = desclookup(identifier)
        id_list = idsearch(identifier)
        title = id_list['title']
        author_name = [id_list['authors'][0]['name']]
    else:
        isbn = request.args.get("q")
        isbn_list = isbnsearch(isbn)
        # parse list with [0] into dict
        isbn_dict = isbn_list[0]
        # parse dict with ['title'] into list
        title = isbn_dict['title']
        author_name = isbn_dict['author_name']

        identifier = bookidlookup(isbn)
        description = desclookup(identifier)

    # Check if isbn is on list
    on_list = bool(db.execute("SELECT * FROM lists WHERE user_id = ? AND ISBN = ?", session["user_id"], isbn))
    # Check read status of ISBN, if not in list, assume unread
    if on_list:
        mystatus_data = db.execute("SELECT status FROM lists WHERE user_id = ? AND ISBN = ?", session["user_id"], isbn)
        my_status = (mystatus_data[0]['status'])
    else:
        my_status = 'unread'

    # POST data received for read or list updates
    if request.method == "POST":
        print("POST")
        #check read status
        readStatus = request.json['readStatus']
        listStatus = request.json['listStatus']

        print("###readStatus: ", readStatus)
        print("###listStatus: ", listStatus)
        # If the book already exists in user's list, update the status column. else, insert new row.
        on_list = bool(db.execute("SELECT * FROM lists WHERE user_id = ? AND ISBN = ?", session["user_id"], isbn))
        if on_list:
            db.execute("UPDATE lists SET status = ? WHERE user_id = ? AND ISBN = ?", readStatus, session["user_id"], isbn)
            # Delete from list if removed
            if listStatus == 'offlist' and readStatus =='unread':
                db.execute("DELETE FROM lists WHERE user_id = ? AND ISBN = ?", session["user_id"], isbn)
        else:
            db.execute("INSERT INTO lists (user_id, isbn, status) VALUES (?, ?, ?)", session["user_id"], isbn, readStatus)
        return '', 200

    return render_template("book.html",  isbn=isbn, title=title, author_name=author_name, identifier=identifier, description=description, my_status=my_status, on_list=on_list)




# Unused
@app.route("/suggest", methods=["GET", "POST"])
@login_required
def suggest():
    """Form to submit suggestions and view books suggested to you"""
    users = db.execute("SELECT username FROM users")
    return render_template("suggest.html", users=users)


# TO DO

# Make Search a bit prettier (square it? Title, author, date?)


# README file
# plan video
# Film + submit!