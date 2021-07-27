#Made by Jayden Ling
#Made in 2021
#App is essentially a personal blog
#Only 1 user can upload posts and photos if they wish

from flask import render_template, redirect, request, flash, session
from flask_login import login_user, login_manager, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from app import app, db, login_manager
from app.models import Users, Post, Comments, profanity

profanity.load_censor_words_from_file(app.config["CENSOR_WORDS"])

@login_manager.user_loader
def load_user(Users_id):
    return Users.query.get(int(Users_id))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter(Users.username == username).first()
        if user is None or not user.check_password(password):
            flash("Wrong username or password")
            return redirect("/login")
        login_user(user)
        flash(f"welcome {user.username}", "nav")
        return redirect("/articles")
    return render_template("login.html")        

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        new_user = Users()
        new_user.username = request.form.get('new_user')
        password = request.form.get('new_password')
        new_user.set_password(password)
        if Users.query.filter(new_user.username == Users.username).first():
            flash("Username is taken!")
            return redirect("/signup")
        elif new_user.username.isspace() or new_user.username == "":
            flash("That ain't a valid username or password")
            return render_template("signup.html")
        elif len(new_user.username) < 5:
            flash("Username has a minimum length of 5 characters, sorry!") 
            return redirect("/signup")
        elif password.isspace() or password == "":
            flash("Password can't be empty!")
            return redirect("/signup")
        elif len(password) < 8:
            flash("Minimum of 8 characters for passwords!")
            return redirect("/signup")
        db.session.add(new_user)
        db.session.commit()
        flash("you're all signed up")
        return redirect("/login")
    return render_template("signup.html")

@app.route('/createpost', methods=['GET','POST'])
@login_required
def createpost():
    if request.method == 'POST':
        new_post = Post()
        new_post.title = request.form.get('new_post_title')
        new_post.body = request.form.get('new_post_body')
        if new_post.title.isspace() or new_post.title == "":
            flash("That's not a valid title")
            return render_template("/createpost.html")
        if new_post.body.isspace() or new_post.body == "":
            flash("That's not a valid article")
            return render_template("/createpost.html")
        current_user.posts.append(new_post)
        db.session.commit()
        return redirect("/articles")
    return render_template('createpost.html')

@app.route('/deletepost', methods=["POST"])
def deletepost():
    old_post = Post.query.get(request.form.get('articleid'))
    db.session.delete(old_post)
    db.session.commit()
    return redirect('/articles')

@app.route('/articles')
def articles():
        posts = Post.query.all()
        return render_template('allarticles.html', posts=posts)

@app.route('/article/<post>')
def article(post):
    article = Post.query.filter(Post.id == post).first_or_404()
    comments = Comments.query.all()
    return render_template("actualarticle.html", article=article, comments=comments)

@app.route('/addcomment', methods=['POST'])
def comment():
    new_comment = Comments()
    new_comment.comment = request.form.get("comment")
    current_user.commenter.append(new_comment)
    postid = request.form.get('post_id', None)
    post = Post.query.get(postid)
    post.comments.append(new_comment)
    if new_comment.comment.isspace() or new_comment.comment == "":
        flash("That ain't it chief")
        if postid and post:
            return redirect(f'/article/{post.id}')
    if len(new_comment.comment) > 256:
        flash("Please shorten your comment")
        if postid and post:
            return redirect(f'/article/{post.id}')
    db.session.commit()
    if postid and post:
        return redirect(f'/article/{post.id}')
    else:
        return redirect('/articles')

@app.route('/deletecomment', methods=['POST'])
def deletecomment():
    old_comment = Comments.query.get(request.form.get('commentid'))
    db.session.delete(old_comment)
    postid = request.form.get('post_id', None)
    post = Post.query.get(postid)
    db.session.commit()
    if postid and post:
        return redirect(f'/article/{post.id}')
    else:
        return redirect('/articles')

@app.route('/togglensfw')
def nsfwmode():
    session['nsfw'] = not session.get('nsfw', False)
    return redirect(request.args.get('t', '/'))


@app.route("/logout")
def logout():
    session['nsfw'] = False
    logout_user()
    flash("Logout Successful", "nav")
    return redirect("/")