from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from application import db, bcrypt
from application.models import User, Post, Newsletter_subscription
from application.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, NewsletterForm
from application.users.utils import save_picture, send_rest_email, send_newsletter_email

users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        if current_app.config['INVITE_KEY'] == form.invite_key.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_password, biography="Default Bio")
            db.session.add(user)
            db.session.commit()
            flash(f'Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('users.login'))
        else:
            flash('Invite Key Incorrect! (Access is limited to club members) ', 'danger')
    return render_template('register.html', title='Register', form=form)
    
@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    flash("Logged out!", "success")
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data.lower()
        current_user.biography = form.biography.data
        current_user.order = form.order.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email.lower()
        form.biography.data = current_user.biography
        form.order.data = current_user.order
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", title="Account", image_file=image_file, form=form)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    events = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', events=events, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        send_rest_email(user)
        flash('An email has been sent with instruction to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title = "Reset Password", form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password reset successfully! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title="Rest Password", form=form)

@users.route("/newsletter", methods=['GET', 'POST'])
@login_required
def newsletter():
    form = NewsletterForm()
    if form.validate_on_submit():
        emails = Newsletter_subscription.query.all()
        if not form.onlyme.data:
            for email in emails:
                send_newsletter_email(email.email, form.title.data, form.content.data)
            flash("Emails sent!", 'success')
        else:
            send_newsletter_email(current_user.email, form.title.data, form.content.data)
            flash("Email sent only to you!", 'success')
        return redirect(url_for('users.newsletter'))

    return render_template('newsletter.html', title="Create newsletter", form=form, legend="Create Email Newsletter (Beta)")


@users.route("/account/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.is_authenticated:
        user = User.query.get_or_404(user_id)
        if user.id != current_user.id:
            abort(403)
        else:
            events = Post.query.filter_by(author=user)
            for event in events:
                db.session.delete(event)
            db.session.commit()
            logout_user()
            db.session.delete(user)
            db.session.commit()
            flash('Account deleted!', 'success')
        return redirect(url_for('main.home'))
    else:
        abort(403)
