from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email

class ContactForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField("Send")
