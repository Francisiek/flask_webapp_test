from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, Length

from flask_babel import lazy_gettext as _l

from webapp import db
from webapp.main.models import User
import sqlalchemy as sqa

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
