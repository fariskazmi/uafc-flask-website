from flask_mail import Message
from application import mail

def send_contact_email(email, message, default_email="developber.accounp@gmail.com"):
    msg = Message('Contact Form submitted on website', sender='noreply@futurecreators.com', recipients=[default_email])
    msg.body = f''' Someone submitted a contact form on the Future Creators Website.
They said their email was: {email} 
Their message is:
    {message}


    This is an automatic email. Please do not reply to the sender, but to the email the user specified.
    '''
    mail.send(msg)