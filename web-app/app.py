"""Main Flask app for web app"""

# later get rid of unused modules
import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import pymongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from bson.objectid import ObjectId

# loading env file
load_dotenv()

# app setup
app = Flask(__name__)

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


# user class for login
class User(UserMixin):
    """User class"""

    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]


@login_manager.user_loader
def load_user(user_id):
    """User loader"""
    user_data = users.find_one({"_id": ObjectId(user_id)})
    return User(user_data) if user_data else None


# user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    """Render register page"""
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("register.html")


# user login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Render login page"""
    if request.method == "POST":
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/")
def home():
    """Render home page"""
    return render_template("page.html")


@app.route("/journal")
def journal():
    """Render journaling page"""
    return render_template("newEntry.html")


if __name__ == "__main__":
    app.run(debug=True)
