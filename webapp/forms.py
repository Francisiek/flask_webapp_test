from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

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

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request a reset')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')

class SearchUserForm(FlaskForm):
    username = StringField('Username')
    submit = SubmitField('Search')

    def validate_username(self, username):
        search = db.session.scalar(sqa.select(User).where(username.data == User.username))
        
        if not search:
            raise ValidationError('No such user')
        
class EditProfileForm(FlaskForm):
    about = TextAreaField('About you', validators=[Length(min=0, max=4095)])
    submit = SubmitField('Update it')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    title = StringField('Title: ', validators=[Length(min=1, max=64)])
    text = TextAreaField('Write: ', validators=[Length(min=1, max=1024)])
    submit = SubmitField('Post it!')
