from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sing in!!!')


from webapp import db
from webapp.models import User
import sqlalchemy as sqa

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Regiterrrtr!')

    def validate_username(self, username):
        search = db.session.scalar(sqa.select(User).where(username.data == User.username))
        
        if search:
            raise ValidationError('Username already taken')
        
    def validate_email(self, email):
        search = db.session.scalar(sqa.select(User).where(email.data == User.email))

        if search:
            raise ValidationError('Email already registered')

class SearchUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Search')

    def validate_username(self, username):
        search = db.session.scalar(sqa.select(User).where(username.data == User.username))
        
        if not search:
            raise ValidationError('No such user')