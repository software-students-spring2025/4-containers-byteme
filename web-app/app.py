"""Main Flask app for web app"""

# later get rid of unused modules
import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import pymongo
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from bson.objectid import ObjectId
from datetime import datetime
import requests
import logging
import random

# loading env file
load_dotenv()

# app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Set up logging in Docker container's output
logging.basicConfig(level=logging.DEBUG)

# mongodb setup
mongo_host = os.getenv("MONGO_HOST")
mongo_port = os.getenv("MONGO_PORT")
mongo_db = os.getenv("MONGO_DB")
client = pymongo.MongoClient(f"mongodb://{mongo_host}:{mongo_port}/")
db = client[mongo_db]
users = db.users
entries = db.entries

# bycrypt setup
bcrypt = Bcrypt(app)

# login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_signup"


# user class for login
class User(UserMixin):
    """User class"""

    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]


# user login and registration
@app.route("/login-signup", methods=["GET", "POST"])
def login_signup():
    """Render login/signup page"""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        action = request.form["submit"]  # this will be "Login" or "Sign Up"

        if action == "Login":
            user_data = users.find_one({"username": username})
            if user_data and bcrypt.check_password_hash(
                user_data["password"], password
            ):
                user = User(user_data)
                login_user(user)
                return redirect(url_for("home"))
            return "Invalid credentials", 400

        if action == "Sign Up":
            if users.find_one({"username": username}):
                return "User already exists", 400
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            user_data = {"username": username, "password": hashed_password}
            _ = users.insert_one(user_data).inserted_id
            return redirect(url_for("login_signup"))

    return render_template("login_signup.html")


@login_manager.user_loader
def load_user(user_id):
    """User loader"""
    user_data = users.find_one({"_id": ObjectId(user_id)})
    return User(user_data) if user_data else None


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for("login_signup"))


@app.route("/")
def home():
    """Render home page"""
    if not current_user.is_authenticated:
        return redirect(url_for("login_signup"))

    # fetch prev entries to display
    user_entries = entries.find({"user_id": current_user.id}).sort("date", pymongo.DESCENDING)
    return render_template("index.html", entries=user_entries)


@app.route("/add-entry")
@login_required
def add_entry():
    """Render journaling page"""
    return render_template("new_entry.html")

@app.route("/submit-entry", methods=["POST"])
@login_required
def submit_entry():
    """Submit entry"""
    text = request.form["entry"]
    date = request.form["date"]
    doc = {
        "user_id": current_user.id,
        "journal_date": date,
        "text": text,
    }
    new_entry_id = entries.insert_one(doc).inserted_id
    app.logger.debug("*** submit_entry(): Inserted 1 entry: %s", new_entry_id)
    
    # Trigger the /analyze endpoint in the ml_client service
    analyze_url = "http://ml-client:5001/analyze"  
    response = requests.post(analyze_url, json={"entry_id": str(new_entry_id), "text": text})

    if response.status_code == 200:
        data = response.json()
        status = data.get("status")
        updated_entry_id = data.get("entry_id")

        app.logger.debug("*** submit_entry(): Analysis result=%s, entry_id=%s", status, updated_entry_id)
        return redirect(url_for("view_entry", entry_id=updated_entry_id))
    else:
        app.logger.error("*** submit_entry(): Analysis failed: %s", response.text)
        return "Error analyzing entry", 500

@app.route("/entry/<entry_id>")
@login_required
def view_entry(entry_id):
    """Render a journal entry page"""
    entry = entries.find_one({"_id": ObjectId(entry_id)})
    if not entry:
        return "Entry not found", 404
    app.logger.debug("*** view_entry(): Found entry: %s", entry)
    
    sentiment_score = entry.get("sentiment", {}).get("composite_score", 0)
    
    return render_template("page.html", entry=entry, quotes=quotes, sentiment_score=sentiment_score)

if __name__ == "__main__":
    app.run(debug=True)  
    app.logger.debug("*** web-app is running")
