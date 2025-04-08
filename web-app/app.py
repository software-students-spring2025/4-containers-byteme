
"""Main Flask app for web app"""

# later get rid of unused modules
import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import pymongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from bson.objectid import ObjectId

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import uuid
import requests


# loading env file
load_dotenv()

# app setup
app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5000", "http://localhost:5000"])


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

# MongoDB setup (local)
client = MongoClient("mongodb://localhost:27017")
db = client.FeelWrite  # make sure this matches MongoDB casing
users = db.users
entries = db.entries

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if users.find_one({'username': data['username']}):
        return jsonify({'error': 'Username already exists'}), 400
    users.insert_one({'username': data['username'], 'password': data['password']})
    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = users.find_one({'username': data['username'], 'password': data['password']})
    if user:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@app.route("/journal")
def journal():
    """Render journaling page"""
    return render_template("newEntry.html")

@app.route('/add-entry', methods=['POST'])
def add_entry():
    data = request.json
    username = data['username']
    content = data['content']
    date = data['date']


    try:
        ml_response = requests.post('http://localhost:5001/analyze', json={'text': content})
        mood_score = ml_response.json().get('score', 3)
    except Exception as e:
        print("ML agent error:", e)
        mood_score = 3

    entry = {
        "id": str(uuid.uuid4()),
        "username": username,
        "date": date,
        "content": content,
        "mood_score": mood_score
    }

    entries.insert_one(entry)
    return jsonify({'message': 'Entry added', 'score': mood_score}), 201

@app.route('/entries/<username>', methods=['GET'])
def get_entries(username):
    user_entries = list(entries.find({'username': username}, {'_id': 0}))
    return jsonify(user_entries)

# Serve HTML pages
@app.route('/')
def serve_signup():
    return send_from_directory('templates', 'signUp.html')

@app.route('/index.html')
def serve_index():
    return send_from_directory('templates', 'index.html')

@app.route('/newEntry.html')
def serve_new_entry():
    return send_from_directory('templates', 'newEntry.html')

@app.route('/page.html')
def serve_entry_page():
    return send_from_directory('templates', 'page.html')


@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('templates/images', filename)


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin in ["http://localhost:5000", "http://127.0.0.1:5000"]:
        response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

if __name__ == '__main__':
    app.run(debug=True)
