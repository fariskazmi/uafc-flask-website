from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from application import db, bcrypt
from application.models import User, Post, Newsletter_subscription
from application.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, NewsletterForm
from application.users.utils import save_picture, send_rest_email, send_newsletter_email
from secrets import token_hex

users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        admin_key = False
        if form.admin.data and current_app.config['INVITE_KEY'] == form.invite_key.data:
            with current_app.open_resource('admin_codes.txt', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if form.admin_key.data == line.rstrip():
                        admin_key = True
            if admin_key:
                with open('./admin_codes.txt', 'w') as f:
                    for line in lines:
                        if line.rstrip() != form.admin_key.data:
                            f.write(line)
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_password, biography="Default Bio", admin=True)
                db.session.add(user)
                db.session.commit()
                flash(f'Your admin account has been created! You are now able to log in', 'success')
                return redirect(url_for('users.login'))
            else:
                flash("Admin key incorrect!", 'danger')
        elif current_app.config['INVITE_KEY'] == form.invite_key.data:
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
        if current_app.config['ADMIN_KEY'] == form.admin_key.data:
            if current_user.admin:
                flash("Your account is already an admin!", 'warning')
            else:
                current_user.admin = True
                db.session.commit()
                flash("Your account has been upgraded to an admin account!", 'success')
        elif current_app.config['ADMIN_KEY'] != form.admin_key.data and form.admin_key.data != "":
            flash("Invalid admin key", 'danger')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email.lower()
        form.biography.data = current_user.biography
        form.order.data = current_user.order
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", title="Account", image_file=image_file, form=form)

@users.route("/save-users-saved-post", methods=['POST'])
@login_required
def save_users_saved_post():
    current_user.post_title_saved = request.get_json()['title']
    current_user.post_html_saved = request.get_json()['html']
    current_user.post_md_saved = request.get_json()['md']
    db.session.commit()
    return jsonify(True)

@users.route("/get-users-saved-post", methods=['POST'])
@login_required
def get_users_saved_post():
    return jsonify({"title":current_user.post_title_saved, "html": current_user.post_html_saved, "md": current_user.post_md_saved})


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

@users.route("/admin", methods=["GET"])
@login_required
def admin():
    if not current_user.admin:
        abort(403)
    else:
        return render_template("admin.html", title="Admin")

@users.route("/admin/users", methods=["GET"])
@login_required
def admin_users():
    if not current_user.admin:
        abort(403)
    else:
        users = User.query.order_by(User.order)
        return render_template("admin_users.html", title="Admin - Users", users=users)

@users.route("/admin/users/<int:user_id>", methods=["GET", "POST"])
@login_required
def admin_user(user_id):
    if not current_user.admin:
        abort(403)
    else:
        user = User.query.get_or_404(user_id)
        form = UpdateAccountForm()
        if form.is_submitted():
            bypass = False
            check_user = User.query.filter_by(username=form.username.data).first()
            if user != check_user and check_user is not None:
                flash("That username is taken. Please choose a different one.", 'danger')
                bypass = True
            check_user = User.query.filter_by(email=form.email.data).first()
            if user != check_user and check_user is not None:
                flash("That email is taken. Please choose a different one.", 'danger')
                bypass = True
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                user.image_file = picture_file
            if not bypass:
                user.username = form.username.data
                user.email = form.email.data.lower()
                user.biography = form.biography.data
                user.order = form.order.data
                db.session.commit()
                flash(f"{user.username}'s account has been updated!", 'success')
                if current_app.config['ADMIN_KEY'] == form.admin_key.data:
                    if user.admin:
                        flash(f"{user.username}'s account is already an admin!", 'warning')
                    else:
                        user.admin = True
                        db.session.commit()
                        flash(f"{user.username}'s account has been upgraded to an admin account!", 'success')
                elif current_app.config['ADMIN_KEY'] != form.admin_key.data and form.admin_key.data != "":
                    flash("Invalid admin key", 'danger')
            return redirect(url_for('users.admin_user', user_id=user.id))
        elif request.method == 'GET':
            form.username.data = user.username
            form.email.data = user.email.lower()
            form.biography.data = user.biography
            form.order.data = user.order
        image_file = url_for('static', filename='profile_pics/' + user.image_file)
        return render_template("admin_user_edit.html", title="Admin - " + user.username, user=user, form=form, image_file=image_file)

@users.route("/admin/newsletter-subscribers", methods=["GET"])
@login_required
def admin_newsletter():
    if not current_user.admin:
        abort(403)
    else:
        newsletter_subscribers = Newsletter_subscription.query.all()
        return render_template("admin_newsletter.html", title="Admin - Newsletter Subscribers", n_s=newsletter_subscribers)

@users.route("/admin/newsletter-subscribers/<string:email>/delete", methods=['POST'])
@login_required
def admin_delete_newsletter_subscription(email):
    n_s = Newsletter_subscription.query.get_or_404(email)
    if not current_user.admin:
        abort(403)
    else:
        db.session.delete(n_s)
        db.session.commit()
        flash('Newsletter subscriber deleted!', 'success')
    return redirect(url_for('users.admin_newsletter'))

@users.route("/admin/contact-forms", methods=["GET"])
@login_required
def admin_contact_forms():
    if not current_user.admin:
        abort(403)
    else:
        return render_template("admin_contact.html", title="Admin - Users")

@users.route("/admin/news-events", methods=["GET"])
@login_required
def admin_news_events():
    if not current_user.admin:
        abort(403)
    else:
        page = request.args.get('page', 1, type=int)
        events = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template("admin_events.html", title="Admin - News", events=events)

@users.route("/admin/news-events/<int:post_id>")
@login_required
def admin_news_event(post_id):
    if not current_user.admin:
        abort(403)
    else:
        event = Post.query.get_or_404(post_id)
        return render_template('admin_news_event.html', title=event.title, event=event)

