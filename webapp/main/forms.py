from flask_wtf import FlaskForm
from urllib3 import request
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, Length, DataRequired

from flask_babel import lazy_gettext as _l
from flask import request

from webapp import db
from webapp.models import User
import sqlalchemy as sqa

class SearchForm(FlaskForm):
    query = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}

        super(SearchForm, self).__init__(*args, **kwargs)

class EditProfileForm(FlaskForm):
    about = TextAreaField(_l('About you'), validators=[Length(min=0, max=4095)])
    submit = SubmitField(_l('Update it'))

class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))

class PostForm(FlaskForm):
    title = StringField(_l('Title: '), validators=[Length(min=1, max=64)])
    text = TextAreaField(_l('Write: '), validators=[Length(min=1, max=1024)])
    submit = SubmitField(_l('Post it!'))
