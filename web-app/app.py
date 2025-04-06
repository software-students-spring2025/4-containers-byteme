#later get rid of unused modules
from flask import Flask, render_template, request, redirect, abort, url_for, make_response, session
from dotenv import load_dotenv 
import os
import pymongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/journal")
def about():
    return render_template("journal.html")

if __name__ == '__main__':
    app.run(debug=True)
