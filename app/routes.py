#Made by Jayden Ling
#Made in 2021

import re
from flask import render_template, redirect, request, flash, session
from flask_login import login_user, login_manager, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from app import app, db, login_manager
from app.models import Users, Post, Comments, profanity

#loads list of profane words to censor
profanity.load_censor_words_from_file(app.config["CENSOR_WORDS"])


ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
        filenamr.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(Users_id):
    return Users.query.get(int(Users_id))

#HOME PAGE
@app.route('/')
def index():
    return render_template("index.html")

#LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username") #user inputs their username
        password = request.form.get("password") #user inputs password
        user = Users.query.filter(Users.username == username).first()   #checks database if input username is in database
        if user is None or not user.check_password(password):   #if user doesn't exist or wrong password
            flash("Wrong username or password") 
            return redirect("/login")
        login_user(user) #if user exists AND correct password, login user
        flash(f"welcome {user.username}", "nav") #show message to user after logging in
        return redirect("/articles")
    return render_template("login.html")        

#SIGNUP PAGE
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        new_user = Users()
        new_user.username = request.form.get('new_user') #user input desired username
        password = request.form.get('new_password') #user input desired password
        new_user.set_password(password) #hash password
        if Users.query.filter(new_user.username == Users.username).first(): #is desired username already exists
            flash("Username is taken!")
            return redirect("/signup")
        elif new_user.username.isspace() or new_user.username == "": #if username is just blank or spaces
            flash("That ain't a valid username or password")
            return render_template("signup.html")
        elif len(new_user.username) < 5: #username shorter than 5 characters
            flash("Username has a minimum length of 5 characters") 
            return redirect("/signup")
        elif len(new_user.username) > 16: #username longer than 16 characters
            flash("Username has a max length of 16!")
            return redirect("/signup")
        elif password.isspace() or password == "": #password empty or spaces
            flash("Password can't be empty!")
            return redirect("/signup")
        elif len(password) < 8: #password smaller than 8 characters
            flash("Minimum of 8 characters for passwords!")
            return redirect("/signup")
        db.session.add(new_user) #signs up new user
        db.session.commit() #adds to database
        flash("you're all signed up")
        login_user(new_user)
        return redirect("/articles")
    return render_template("signup.html")

#CREATE-A-POST PAGE
@app.route('/createpost', methods=['GET','POST'])
@login_required
def createpost():   
    if request.method == 'POST':
        new_post = Post()
        new_post.title = request.form.get('new_post_title') #user input post title
        new_post.body = request.form.get('new_post_body')   #user input post body
        if request.files['new_post_image']: #if user has file upload
            new_post.image = request.files["new_post_image"].filename 
            request.files['new_post_image'].save(f'app/static/images/{new_post.image}') #save image to folder
        if new_post.title.isspace() or new_post.title == "": #blank title or space
            flash("That's not a valid title")
            return render_template("createpost.html")
        if len(new_post.title) > 50: #title longer than 50 characters
            flash("That's too long a title")
            return render_template("createpost.html")
        if new_post.body.isspace() or new_post.body == "": #body empty or space
            flash("That's not a valid article")
            return render_template("createpost.html")
        if len(new_post.body) > 1000: #body longer than 1k characters
            flash("Article too long!")
            return render_template("createpost.html")
        current_user.posts.append(new_post) #link new post to user
        db.session.commit() #add new post to databse
        return redirect("/articles")
    return render_template('createpost.html')

#DELETE POST
@app.route('/deletepost', methods=["POST"])
def deletepost():
    old_post = Post.query.get(request.form.get('articleid')) #finds id of post
    db.session.delete(old_post) #deletes post
    db.session.commit()
    return redirect('/articles')

#PAGE TO SHOW ALL CREATED POSTS
@app.route('/articles')
def articles():
        posts = Post.query.all() #grabs all posts in the table
        return render_template('allarticles.html', posts=posts)

#SPECIFIC ARTICLE PAGE
@app.route('/article/<post>')
def article(post):
    article = Post.query.filter(Post.id == post).first_or_404() #grabs specific article user has clicked 
    comments = Comments.query.all() #grabs all comments
    return render_template("actualarticle.html", article=article, comments=comments)

#ADD COMMENT 
@app.route('/addcomment', methods=['POST'])
def comment():
    new_comment = Comments()
    new_comment.comment = request.form.get("comment") #user input comment
    current_user.commenter.append(new_comment) #link comment to user
    postid = request.form.get('post_id', None) #get post id to add comment to
    post = Post.query.get(postid)
    post.comments.append(new_comment) #add comment
    if new_comment.comment.isspace() or new_comment.comment == "": #if comment blank or space
        flash("Invalid Comment")
        return redirect(request.args.get('t', '/')) #redirects user to previous page they were on, aka the post
    if len(new_comment.comment) > 256: #comment longer than 256 characters
        flash("Please shorten your comment")
        return redirect(request.args.get('t', '/'))
    db.session.commit()
    return redirect(request.args.get('t', '/'))

#DELETE COMMENTS
@app.route('/deletecomment', methods=['POST'])
def deletecomment():
    old_comment = Comments.query.get(request.form.get('commentid')) #get id of comment to delete
    db.session.delete(old_comment) #delete comment
    db.session.commit()
    return redirect(request.args.get('t', '/'))

#TOGGLE NSFW MODE 
@app.route('/togglensfw')
def nsfwmode():
    session['nsfw'] = not session.get('nsfw', False) #turns nsfw session on and off
    return redirect(request.args.get('t', '/'))

#LOGOUT
@app.route("/logout")
def logout():
    session['nsfw'] = False #sets nsfw mode to off
    logout_user() #logouts user
    flash("Logout Successful", "nav")
    return redirect("/")