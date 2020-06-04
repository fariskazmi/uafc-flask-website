import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from application import mail

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
    msg.body = f''' To reset your password, visit the following link:
    {url_for('users.reset_token', token=token, _external=True)}


    If you did not make this request then simply ignore this email and no changes will be made
    '''
    mail.send(msg)