from flask import render_template, redirect
from app import app

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("home.html")