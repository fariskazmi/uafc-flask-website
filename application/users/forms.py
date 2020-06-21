from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flask_login import current_user
from application.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=127)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=127)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password'), Length(min=4, max=127)])
    invite_key = StringField('Invite Key', validators=[DataRequired()])
    admin = BooleanField('Admin Account')
    admin_key = StringField('Admin Key')
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign Up')

    def validate_username(self, username): 
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email): 
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=127)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=127)])
    remember = BooleanField('Remember Me')
    recaptcha = RecaptchaField()
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=127)])
    biography = TextAreaField('Biography', validators=[DataRequired(), Length(min=1, max=511)])
    order = IntegerField("Order - where you'll appear on the About Us page (1 is first, 99 is last)", validators=[DataRequired(), NumberRange(min=1, max=99)])
    admin_key = StringField('Admin Key - Upgrade to Admin Account')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username): 
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email): 
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=127)])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email): 
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=127)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password'), Length(min=4, max=127)])
    submit = SubmitField('Reset Password')

class NewsletterForm(FlaskForm):
    title = StringField("Subject", validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png'])])
    onlyme = BooleanField('Send Newsletter only to myself (For Previewing/Testing)')
    submit = SubmitField("Send")
