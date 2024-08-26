from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Sing in!!!'))


from webapp import db
from webapp.models import User
import sqlalchemy as sqa

class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Regiterrrtr!'))

    def validate_username(self, username):
        search = db.session.scalar(sqa.select(User).where(username.data == User.username))
        
        if search:
            raise ValidationError(_l('Username already taken'))
        
    def validate_email(self, email):
        search = db.session.scalar(sqa.select(User).where(email.data == User.email))

        if search:
            raise ValidationError(_l('Email already registered'))

class PasswordResetRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request a reset'))

class PasswordResetForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Reset'))

class SearchUserForm(FlaskForm):
    username = StringField(_l('Username'))
    submit = SubmitField(_l('Search'))

    def validate_username(self, username):
        search = db.session.scalar(sqa.select(User).where(username.data == User.username))
        
        if not search:
            raise ValidationError(_l('No such user'))
        
class EditProfileForm(FlaskForm):
    about = TextAreaField(_l('About you'), validators=[Length(min=0, max=4095)])
    submit = SubmitField(_l('Update it'))

class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))

class PostForm(FlaskForm):
    title = StringField(_l('Title: '), validators=[Length(min=1, max=64)])
    text = TextAreaField(_l('Write: '), validators=[Length(min=1, max=1024)])
    submit = SubmitField(_l('Post it!'))
