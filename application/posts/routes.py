from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from application import db
from application.models import Post
from application.posts.forms import PostForm
from application.posts.utils import save_picture

posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        flash(form.picture.data)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            flash(picture_file)
            post = Post(title=form.title.data, content=form.content.data, author=current_user, image_file=picture_file)
        else:
            post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Post created!", 'success')
        return redirect(url_for('main.home'))
    return render_template("create_post.html", title="New Post", form=form, legend="New Post")

@posts.route("/post/<int:post_id>")
def post(post_id):
    event = Post.query.get_or_404(post_id)
    return render_template('post.html', title=event.title, event=event)

@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    event = Post.query.get_or_404(post_id)
    if event.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.content = form.content.data
        db.session.commit()
        flash("Post updated!", 'success')
        return redirect(url_for('posts.post', post_id = event.id))
    elif request.method == 'GET':
        form.title.data = event.title
        form.content.data = event.content
    return render_template('create_post.html', title="Update Post", form=form, legend="Update Post")

@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    event = Post.query.get_or_404(post_id)
    if event.author != current_user:
        abort(403)
    else:
        db.session.delete(event)
        db.session.commit()
        flash('Post deleted!', 'success')
    return redirect(url_for('main.home'))
