import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from application import mail
from itsdangerous import JSONWebSignatureSerializer as UntimedSerializer
from flask import render_template

def save_picture(form_picture):
    random_hex = secrets.token_hex(8) 
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    i = Image.open(form_picture)
    img = i.resize((600, 600))
    img.save(picture_path)

    return picture_fn

def send_rest_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request - Future Creators', sender='noreply@futurecreators.com', recipients=[user.email])
    msg.body = f''' To reset your password, visit the following link (expires in 30 min):
    {url_for('users.reset_token', token=token, _external=True)}

    If you did not make this request then simply ignore this email and no changes will be made
    '''
    msg.html = render_template('confirm_email.html', link=url_for('users.reset_token', token=token, _external=True), title="Password Reset Request", sub_title="To reset your password, visit the following link (expires in 30 min)", button_text="Reset Password", bottom_header="Didn't request a password reset?", bottom_content="If you believe this was a mistake or you did not intend on resetting your password, you can ignore this message and nothing will happen.")
    mail.send(msg)

def get_unsubscribe_token(email):
    s = UntimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps({'email': email}).decode('utf-8')

def send_newsletter_email(email, subject, content):
    msg = Message(subject, sender='noreply@futurecreators.com', recipients=[email])
    msg.body = f''' Example Newsletter. Have fun! {content} 
    
    Unsubscribe: {url_for('main.newsletter_unsubscribe_verify', token=get_unsubscribe_token(email), _external=True)}
     '''
    msg.html = render_template('newsletter_email.html', title=subject, sub_title=content, unsubscribe_link=url_for('main.newsletter_unsubscribe_verify', token=get_unsubscribe_token(email), _external=True))
    mail.send(msg)