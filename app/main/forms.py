from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms.validators import Required,Email,EqualTo
from ..models import User
from wtforms import ValidationError


class UpdateProfile(FlaskForm):
    bio = TextAreaField('Edit your bio',validators = [Required()])
    submit = SubmitField('Edit bio')


class CommentForm(FlaskForm):
    comment = TextAreaField('Enter your comment')
    submit = SubmitField('Comment')