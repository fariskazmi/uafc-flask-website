from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email

class ContactForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    content = TextAreaField('Message', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Send")

class VolunteerContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email (uAlberta preferred)', validators=[DataRequired(), Email()])
    faculty = StringField('Faculty', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    interest = SelectField('I am interested in', validators=[DataRequired()], choices=[("Developing Projects", "Developing Projects"), ("Mentoring", "Mentoring"), ("Both", "Both"), ("Other (outreach/business/etc)", "Other (outreach/business/etc)")])
    content = TextAreaField('Anything else you would like us to know?', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Sign up")

class TeacherContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    school = StringField('School', validators=[DataRequired()])
    grade = StringField('Grade(s)', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number')
    content = TextAreaField('Anything else you would like us to know?', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Sign up")

class NewsletterSignUpConfirmationForm(FlaskForm):
    recaptcha = RecaptchaField()
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Confirm Subscription")
    
