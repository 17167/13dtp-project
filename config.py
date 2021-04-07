import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'awjdobaydvawd'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///website.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLACHEMY_ECHO = False