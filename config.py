import os
# from app.models import profanity

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'awjdobaydvawd'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///website.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLACHEMY_ECHO = False
    UPLOAD_FOLDER = '/app/static/images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif'}
    CENSOR_WORDS = os.path.abspath('profane_words.txt')