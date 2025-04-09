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

# loading env file
load_dotenv()

# app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

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
    return render_template("index.html")


@app.route("/add-entry")
@login_required
def add_entry():
    """Render journaling page"""
    return render_template("new_entry.html")


if __name__ == "__main__":
    app.run(debug=True)
