from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Users(UserMixin, db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Post(db.Model):
    __tablename__ = 'Post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    users = db.relationship('Users', backref='posts')

class Comments(db.Model):
    __tablename__ = 'Comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'))
    comment = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    post = db.relationship('Post', backref='comments')
    users = db.relationship('Users', backref='commenter')

# class Images(db.Model):
#     __tablename__ = 'Images'

#     id = db.Column(db.Integer, primary_key=True)
#     imageurl = db.Column(db.Text(100))
#     post_id = db.Column(db.Integer, db.ForeignKey('Post.id'))

#     Post = db.relationship('Post', backref='Images')

db.create_all()


def create_debug_user(username, password, is_admin):
    if Users.query.filter(Users.username==username).first() is None:
        new_user = Users(username=username, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

create_debug_user('bruh', 'bruh', 1)