import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'j3di20xcjnaz120ndi8c3lnxkla24'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI is not None:
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
        'postgres://', 'postgresql://')
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dbs', 'webapp.db')
    POSTS_PER_PAGE = 4
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['frx30342@protonmail.com']
    PASSWORD_RESET_EXPIRE_TIME_SECONDS = 5*60
    LANGUAGES = ['en', 'pl']
    TRANSLATION_API_KEY = os.environ.get('TRANSLATION_API_KEY')
    SEARCH_URL = os.environ.get('SEARCH_URL')
    CLEANUP_TIME_MINUTES = 30