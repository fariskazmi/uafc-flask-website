from flask import render_template, request, Blueprint, flash, redirect, url_for, current_app, jsonify
from application.models import Post, User, Newsletter_subscription
from application.main.forms import ContactForm, VolunteerContactForm, TeacherContactForm, NewsletterSignUpConfirmationForm
from application.main.utils import send_contact_email, send_newsletter_email, verify_newsletter_token, get_newsletter_token, verify_unsubscribe_token
from application import db
from pyhunter import PyHunter

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    events = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', events=events)

@main.route('/about')
def about():
    users = User.query.order_by(User.order)
    return render_template('about.html', title='About', users=users)

@main.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        send_contact_email(form.email.data, form.content.data)
        flash("Message sent!", 'success')
        return redirect(url_for('main.contact'))
        
    return render_template("contact.html", title="Contact", form=form, legend="Contact")

@main.route('/teachers', methods=['GET', 'POST'])
def teachers():
    form = TeacherContactForm()
    if form.validate_on_submit():
        flash("Message sent! (Not actually)", 'success')
        return redirect(url_for('main.teachers'))
    return render_template('teachers.html', title='Teachers', form=form, legend="Teachers - Sign up!")

@main.route('/volunteers', methods=['GET', 'POST'])
def volunteers():
    form = VolunteerContactForm()
    if form.validate_on_submit():
        flash("Message sent! (Not actually)", 'success')
        return redirect(url_for('main.volunteers'))
    return render_template('volunteers.html', title='Volunteers', form=form, legend="Volunteers - Sign up!")

@main.route('/newsletter_signup', methods=['POST'])
def newsletter_signup():
    form = NewsletterSignUpConfirmationForm(request.form)
    if form.validate_on_submit():
        token = get_newsletter_token(form.email.data)
        send_newsletter_email(form.email.data, token)
        flash("An email has been sent to confirm your subscription to our newsletter.", 'success')
        return redirect(url_for('main.home'))
    email = request.form['email']
    return render_template('newsletter_signup_confirm.html', title='Newsletter Signup', heading="Thanks for signing up!", body="Complete the following reCAPTCHA to confirm your subscription", form=form, legend="", email=email, email_verification_failed = "False")

@main.route('/newsletter_signup/<token>', methods=["GET"])
def newsletter_signup_verify(token):
    email = verify_newsletter_token(token)
    if email is None:
        flash("Invalid token", 'danger')
        return render_template('newsletter_signup.html', title='Newsletter Signup', heading="Invalid token!", body="Either the token timed out, or is invalid. You can sign up again by scrolling to the bottom of the page.")
    elif Newsletter_subscription.query.filter_by(email=email).first() is None:
        # add to database
        newsletter_email = Newsletter_subscription(email=email)
        db.session.add(newsletter_email)
        db.session.commit()
        flash("Your subscription is confirmed!", 'success')
        return render_template('newsletter_signup.html', title='Newsletter Signup', heading="Subscription confirmed!", body="Thanks for signing up!")
    elif email == Newsletter_subscription.query.filter_by(email=email).first().email:
        flash("Already subscribed!", 'warning')
        return render_template('newsletter_signup.html', title='Newsletter Signup', heading="Already subscribed!", body="You have already subscribed to our newsletter! If you would like to unsuscribe, check any of our recent emails.")


@main.route('/newsletter_unsubscribe/<token>', methods=["GET"])
def newsletter_unsubscribe_verify(token):
    email = verify_unsubscribe_token(token)
    if email is None or Newsletter_subscription.query.filter_by(email=email).first() is None:
        flash("No such email exits", 'danger')
        return render_template('newsletter_signup.html', title='Newsletter Unsubscribe', heading="No such email exists", body="The email address you are trying to unsubscribe from our newsletter does not exist in the database.")
    else:
        # remove from database
        newsletter_email = Newsletter_subscription.query.filter_by(email=email).first()
        db.session.delete(newsletter_email)
        db.session.commit()
        flash("Your subscription has been cancelled!", 'success')
        return render_template('newsletter_signup.html', title='Newsletter Unsubscribe', heading="Subscription cancelled!", body="We're sorry to see you go. If you would like to tell us why you unsubscribed, please go to our contact page")

@main.route('/verify-email', methods=['POST'])
def verify_email():
    email = request.get_json()['email']
    hunter = PyHunter(current_app.config['HUNTER_API_KEY'])
    verification_result = hunter.email_verifier(email)
    return jsonify(verification_result['result'] != 'undeliverable')



