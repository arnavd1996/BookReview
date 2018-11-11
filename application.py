import os

from flask import Flask, session, render_template, request, redirect, flash, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
	if not session.get("logged_in"):
		return render_template("index.html")
	else:
		return render_template("home.html")

@app.route("/register")
def register():
	"""Signup if not done so yet"""
	return render_template("register.html")

@app.route("/createuser", methods=["POST"])
def createuser():

	username = request.form.get("username")
	password = request.form.get("password")

	db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
			{"username": username, "password": password})
	db.commit()
	return render_template("success.html")

@app.route("/login", methods=['POST'])
def login():

	username = request.form.get("username")
	password = request.form.get("password")

	use = db.execute("SELECT * FROM users WHERE username = :username", 
			{"username": username}).fetchone()
	pass_status = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", 
			{"username":username, "password":password}).fetchone()
	if use is None:
		return render_template("error.html", message="User not registered")
	elif pass_status is None:
		return render_template("error.html", message="Wrong Password")
	else:
		session['logged_in'] = True
		return render_template("home.html")

@app.route("/logout", methods=['POST'])
def logout():
	
	session['logged_in'] = False
	return render_template("error.html", message="You have been logged out")

@app.route("/search", methods=['POST'])
def search():

	query = request.form.get("query")
	results = db.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE LOWER(:query)) OR (LOWER(title) LIKE LOWER(:query)) OR (author LIKE LOWER(:query)) LIMIT 10",
			{ "query": '%' + query + '%'} ).fetchall()
	if results is None:
		return render_template("error.html", message="No results found")
	else:
		return render_template("search.html", results=results)

@app.route("/book/<book_id>")
def book(book_id):
	details = db.execute("SELECT * FROM books WHERE id = :id", 
			{"id":book_id}).fetchone()
	return render_template("book.html", details=details)

@app.route("/addreview", methods=['POST'])
def addreview():

	review = request.form.get("review")
	rating = request.form.get("rating")

	db.execute(
		"INSERT INTO reviews (review, rating, userid, bookid) VALUES (:review, :rating, :userid, :bookid )",
		{"review": review, "rating": rating , "user_id": username, "book_id": book_id }
	)
	db.commit()



