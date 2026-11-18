from flask import flash, redirect, render_template, request, session, url_for

from ..extensions import db
from . import post_bp
from .forms import DeletePostForm, PostForm
from .models import Post


def _assign_form_to_post(form: PostForm, post: Post) -> None:
    post.title = form.title.data.strip()
    post.content = form.content.data.strip()
    post.is_active = bool(form.enabled.data)
    post.posted = form.publish_date.data
    post.category = form.category.data


@post_bp.route("", methods=["GET"])
def post_list():
    stmt = (
        db.select(Post)
        .where(Post.is_active.is_(True))
        .order_by(Post.posted.desc())
    )
    posts = db.session.scalars(stmt).all()
    return render_template("posts/posts.html", title="Публікації", posts=posts)


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            author=str(session.get("username", "Anonymous"))[:20] or "Anonymous"
        )
        _assign_form_to_post(form, post)
        db.session.add(post)
        db.session.commit()
        flash("Пост успішно створено.", "success")
        return redirect(url_for("posts.post_detail", post_id=post.id))

    return render_template(
        "posts/add_post.html",
        title="Створити пост",
        form=form,
        page_heading="Створити пост",
    )


@post_bp.route("/<int:post_id>", methods=["GET"])
def post_detail(post_id: int):
    post = db.get_or_404(Post, post_id)
    return render_template("posts/detail_post.html", title=post.title, post=post)


@post_bp.route("/<int:post_id>/update", methods=["GET", "POST"])
def update_post(post_id: int):
    post = db.get_or_404(Post, post_id)
    if request.method == "GET":
        form = PostForm(obj=post)
        form.enabled.data = post.is_active
        form.publish_date.data = post.posted
    else:
        form = PostForm()

    if form.validate_on_submit():
        _assign_form_to_post(form, post)
        db.session.commit()
        flash("Пост успішно оновлено.", "success")
        return redirect(url_for("posts.post_detail", post_id=post.id))

    return render_template(
        "posts/add_post.html",
        title="Редагувати пост",
        form=form,
        page_heading="Редагувати пост",
    )


@post_bp.route("/<int:post_id>/delete", methods=["GET", "POST"])
def delete_post(post_id: int):
    post = db.get_or_404(Post, post_id)
    form = DeletePostForm()

    if request.method == "POST":
        if not form.validate_on_submit():
            flash("Не вдалося підтвердити видалення поста.", "danger")
            return redirect(url_for("posts.post_detail", post_id=post.id))
        db.session.delete(post)
        db.session.commit()
        flash("Пост успішно видалено.", "success")
        return redirect(url_for("posts.post_list"))

    return render_template(
        "posts/delete_confirm.html", title="Видалити пост", post=post, form=form
    )
