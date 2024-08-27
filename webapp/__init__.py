from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l

def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth.login_page'
login.login_message = _l('Please log in to access that resource.')
mail = Mail(app)
moment = Moment(app)
babel = Babel(app, locale_selector=get_locale)

from webapp.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from webapp.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/blog.log', maxBytes=16384, backupCount=16)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:\n %(message)s in %(pathname)s:%(lineno)d'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Starting up...')

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'],app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='logs@'+app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Blog logg',
            credentials=auth, secure=secure
        )
        mail_handler.setLevel(logging.INFO)
        app.logger.addHandler(mail_handler)

from webapp import routes, models