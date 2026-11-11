from flask import flash, make_response, redirect, render_template, request, session, url_for

from . import user_bp

USERNAME = "Nazar"
PASSWORD = "12345"


@user_bp.route("/hi/<string:name>")
def greetings(name):
    age = request.args.get("age", None, int)
    return render_template("hi.html", name=name.upper(), age=age)


@user_bp.route("/admin")
def admin():
    to_url = url_for("users.greetings", name="administrator", age=45, _external=True)
    return redirect(to_url)


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == USERNAME and password == PASSWORD:
            session["username"] = username
            flash("Ви успішно увійшли в систему.", "success")
            return redirect(url_for("users.profile"))
        flash("Неправильне ім'я користувача або пароль.", "error")
    return render_template("login.html")


@user_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        flash("Спочатку потрібно увійти в систему.", "error")
        return redirect(url_for("users.login"))

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


@user_bp.route("/logout")
def logout():
    session.pop("username", None)
    flash("Ви вийшли із системи.", "success")
    return redirect(url_for("users.login"))


@user_bp.route("/profile/theme", methods=["POST"])
def change_theme():
    if "username" not in session:
        flash("Спочатку потрібно увійти в систему.", "error")
        return redirect(url_for("users.login"))

    theme = request.form.get("theme")
    if theme not in ["light", "dark"]:
        flash("Невідома кольорова схема.", "error")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie("theme", theme, max_age=60 * 60 * 24 * 30)
    flash("Кольорову схему успішно змінено.", "success")
    return response
