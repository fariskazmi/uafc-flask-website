from flask_mail import Message
from application import mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import JSONWebSignatureSerializer as UntimedSerializer
from flask import url_for, current_app, render_template

def send_contact_email(email, message, default_email="developber.accounp@gmail.com"):
    msg = Message('Contact Form submitted on website', sender='noreply@futurecreators.com', recipients=[default_email])
    msg.body = f''' Someone submitted a contact form on the Future Creators Website.
They said their email was: {email} 
Their message is:
    {message}

    This is an automatic email. Please do not reply to the sender, but to the email the user specified.
    '''
    msg.html = render_template('contact_email.html', link="mailto:" + email, title="Contact Form Submitted", sub_title="Someone submitted a contact form on the Future Creators Website", button_text="Reply", bottom_content="Email: " + email, bottom_header=message, bottom_top_header="Message:")
    mail.send(msg)

def send_newsletter_email(email, token):
    msg = Message('Newsletter subscription', sender='noreply@futurecreators.com', recipients=[email])
    msg.body = f''' Thanks for signing up to our newsletter! To confirm your subscription, click the following URL (expires in 24 hours):
{url_for('main.newsletter_signup_verify', token=token, _external=True)}

    If you did not sign up for our newsletter, don't click the above URL and no action will be taken. This is an automatic email. Please do not reply.
    '''
    msg.html = render_template('confirm_email.html', link=url_for('main.newsletter_signup_verify', token=token, _external=True), title="Confirm your subscription", sub_title="Please confirm your subscription to our newsletter (links expire in 24 hours)", button_text="Confirm Your Subscription", bottom_header="Didn't sign up?", bottom_content="If you believe this was a mistake or you did not intend on subscribing to our newsletter, you can ignore this message and nothing will happen.")
    mail.send(msg)

def get_newsletter_token(email, expires_sec=86400):
    s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    return s.dumps({'email': email}).decode('utf-8')


def verify_newsletter_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token)['email']
    except:
        return None
    return email

def verify_unsubscribe_token(token):
    s = UntimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token)['email']
    except:
        return None
    return email