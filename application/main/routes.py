from flask import render_template, request, Blueprint, flash, redirect, url_for
from application.models import Post, User
from application.main.forms import ContactForm
from application.main.utils import send_contact_email

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    events = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', events=events)

@main.route('/about')
def about():
    users = User.query.all()
    return render_template('about.html', title='About', users=users)

@main.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        send_contact_email(form.email.data, form.content.data)
        flash("Message sent!", 'success')
        return redirect(url_for('main.contact'))
    return render_template("contact.html", title="Contact", form=form, legend="Contact")

@main.route('/teachers')
def teachers():
    return render_template('teachers.html', title='Teachers')

@main.route('/volunteers')
def volunteers():
    return render_template('volunteers.html', title='Volunteers')


