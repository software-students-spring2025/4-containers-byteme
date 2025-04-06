"""Main Flask app for web app"""
#later get rid of unused modules
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    """Render home page"""
    return render_template("index.html")

@app.route("/journal")
def about():
    """Render journaling page"""
    return render_template("journal.html")

if __name__ == '__main__':
    app.run(debug=True)
