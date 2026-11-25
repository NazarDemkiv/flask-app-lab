from flask import flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select

from ..extensions import db
from . import user_bp
from .forms import LoginForm, RegistrationForm
from .models import User


@user_bp.route("/hi/<string:name>")
def greetings(name):
    age = request.args.get("age", None, int)
    return render_template("hi.html", name=name.upper(), age=age)


@user_bp.route("/admin")
def admin():
    to_url = url_for("users.greetings", name="administrator", age=45, _external=True)
    return redirect(to_url)


@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Реєстрація успішна. Вас автоматично авторизовано.", "success")
        return redirect(url_for("users.account"))

    return render_template("register.html", form=form)


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = db.session.scalar(select(User).where(User.email == email))
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Ви успішно увійшли в систему.", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)
            return redirect(url_for("users.account"))
        flash("Неправильна електронна пошта або пароль.", "error")

    return render_template("login.html", form=form)


@user_bp.route("/account")
@login_required
def account():
    return render_template("account.html", user=current_user)


@user_bp.route("/all")
@login_required
def users_list():
    users = db.session.scalars(select(User).order_by(User.id)).all()
    return render_template("users_list.html", users=users)


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":
        if "key" in request.form:
            key = request.form.get("key", "").strip()
            value = request.form.get("value", "")
            try:
                max_age = max(0, int(request.form.get("exp", "0")))
            except ValueError:
                flash("Термін дії cookie має бути числом.", "error")
                return redirect(url_for("users.profile"))
            if not key:
                flash("Вкажіть ключ cookie.", "error")
                return redirect(url_for("users.profile"))
            response = make_response(redirect(url_for("users.profile")))
            response.set_cookie(key, value, max_age=max_age)
            flash(f"Cookie з ключем {key} успішно створена.", "success")
            return response

        if "delete_key_cookie" in request.form:
            key = request.form.get("delete_key_cookie", "")
            if key not in request.cookies:
                flash("Cookie з таким ключем не існує.", "error")
                return redirect(url_for("users.profile"))
            response = make_response(redirect(url_for("users.profile")))
            response.delete_cookie(key)
            flash(f"Cookie з ключем {key} видалена.", "success")
            return response

        if "delete_all_cookies" in request.form:
            response = make_response(redirect(url_for("users.profile")))
            for key in request.cookies:
                response.delete_cookie(key)
            flash("Усі cookie були видалені.", "success")
            return response

    return render_template(
        "profile.html",
        cookies=request.cookies,
        theme=request.cookies.get("theme", "light"),
    )


@user_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Ви вийшли із системи.", "info")
    return redirect(url_for("users.login"))


@user_bp.route("/profile/theme", methods=["POST"])
@login_required
def change_theme():

    theme = request.form.get("theme")
    if theme not in ["light", "dark"]:
        flash("Невідома кольорова схема.", "error")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie("theme", theme, max_age=60 * 60 * 24 * 30)
    flash("Кольорову схему успішно змінено.", "success")
    return response
