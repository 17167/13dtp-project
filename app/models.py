from app import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from better_profanity import Profanity
from better_profanity.constants import ALLOWED_CHARACTERS
from better_profanity.utils import (
    any_next_words_form_swear_word,
    get_complete_path_of_file,
    get_replacement_for_swear_word,
)
from flask import session
# from profanityfilter import ProfanityFilter

class ProfanityWithLength(Profanity):
    def _hide_swear_words(self, text, censor_char):
        """Replace the swear words with censor characters."""
        censored_text = ""
        cur_word = ""
        skip_index = -1
        next_words_indices = []
        start_idx_of_next_word = self._get_start_index_of_next_word(text, 0)

        # If there are no words in the text, return the raw text without parsing
        if start_idx_of_next_word >= len(text) - 1:
            return text

        # Left strip the text, to avoid inaccurate parsing
        if start_idx_of_next_word > 0:
            censored_text = text[:start_idx_of_next_word]
            text = text[start_idx_of_next_word:]

        # Splitting each word in the text to compare with censored words
        for index, char in iter(enumerate(text)):
            if index < skip_index:
                continue
            if char in ALLOWED_CHARACTERS:
                cur_word += char
                continue

            # Skip continuous non-allowed characters
            if cur_word.strip() == "":
                censored_text += char
                cur_word = ""
                continue

            # Iterate the next words combined with the current one
            # to check if it forms a swear word
            next_words_indices = self._update_next_words_indices(
                text, next_words_indices, index
            )
            contains_swear_word, end_index = any_next_words_form_swear_word(
                cur_word, next_words_indices, self.CENSOR_WORDSET
            )
            if contains_swear_word:
                cur_word = self.get_replacement_for_swear_word(censor_char, cur_word)
                skip_index = end_index
                char = ""
                next_words_indices = []

            # If the current a swear word
            if cur_word.lower() in self.CENSOR_WORDSET:
                cur_word = self.get_replacement_for_swear_word(censor_char, cur_word)

            censored_text += cur_word + char
            cur_word = ""

        # Final check
        if cur_word != "" and skip_index < len(text) - 1:
            if cur_word.lower() in self.CENSOR_WORDSET:
                cur_word = self.get_replacement_for_swear_word(censor_char, cur_word)
            censored_text += cur_word
        return censored_text

    def get_replacement_for_swear_word(self, censor_char, cur_word="****"):
        if current_user.is_authenticated and session.get('nsfw', False):
            return cur_word
        else:
            return censor_char * len(cur_word)


profanity = ProfanityWithLength()

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

    @property
    def title_censored(self):
        return profanity.censor(self.title)

    @property
    def body_censored(self):
        return profanity.censor(self.body)

class Comments(db.Model):
    __tablename__ = 'Comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'))
    comment = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    post = db.relationship('Post', backref='comments')
    users = db.relationship('Users', backref='commenter')

    @property
    def comment_censored(self):
        return profanity.censor(self.comment)

# class Images(db.Model):
#     __tablename__ = 'Images'

#     id = db.Column(db.Integer, primary_key=True)
#     imageurl = db.Column(db.Text(100))
#     post_id = db.Column(db.Integer, db.ForeignKey('Post.id'))

#     Post = db.relationship('Post', backref='images')

db.create_all()


def create_debug_user(username, password, is_admin):
    if Users.query.filter(Users.username==username).first() is None:
        new_user = Users(username=username, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

create_debug_user('bruh', 'bruh', 1)