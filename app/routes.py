from flask import render_template, redirect, request, flash
from flask_login import login_user, login_manager
from flask_sqlalchemy import SQLAlchemy
from app import app, db, login_manager
from app.models import Users, Post

@login_manager.user_loader
def load_user(Users_id):
    return Users.query.get(int(Users_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter(Users.username == username).first()
        if user is None or not user.check_password(password):
            flash("woops")
            return redirect("/login")
        login_user(user)
        #print(user.username)
        flash("welcom bruh")
        return redirect("/")
    return render_template("login.html")        

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        new_user = Users()
        new_user.username = request.form.get('new_user')
        password = request.form.get('new_password')
        new_user.set_password(password)
        if Users.query.filter(new_user.username == Users.username).first():
            flash("Might want to find a more creative name")
            return redirect("/signup")
        if new_user.username.isspace() or new_user.username == "":
            flash("That ain't a valid username or password")
            return render_template("signup.html")
        if len(new_user.username) < 5:
            flash("Username has a minimum length of 5 characters, sorry!") 
            return redirect("/signup")
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")
    return render_template("signup.html")