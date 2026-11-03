from flask import request, render_template, url_for, redirect, flash, session, make_response
from . import user_bp

USERNAME = "Nazar"
PASSWORD = "12345"

@user_bp.route("/hi/<string:name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)

    return render_template("hi.html", name=name, age=age)

@user_bp.route("/admin")
def admin():
    to_url = url_for("users.greetings", name="administrator", age=45, _external=True)
    print(to_url)
    return redirect(to_url)

@user_bp.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            session["username"] = username
            return redirect(url_for("users.profile"))
        else:
            flash("incorrect password or name", "error")

    return render_template("login.html")

@user_bp.route("/profile", methods = ["GET", "POST"])
def profile():
    if "username" in session:
        flash(f"You have successfully logged in! Your name is {session["username"]}")

        if request.method == "POST":
            if "key" in request.form:
                key = request.form.get("key")
                value = request.form.get("value")
                exp = int(request.form.get("exp"))

                resp = make_response(redirect(url_for("users.profile")))
                resp.set_cookie(key, value, exp)
                flash(f"Кукі з ключем {key} успішно створена!")
                return resp

            elif "delete_key_cookie" in request.form:
                delete_key_cookie = request.form.get("delete_key_cookie")

                if delete_key_cookie not in request.cookies:
                    flash("Кукі з таким ключем не існує!")
                    return redirect(url_for("users.profile"))

                resp = make_response(redirect(url_for("users.profile")))
                resp.delete_cookie(delete_key_cookie)
                flash(f"Кукі з ключем {delete_key_cookie} видалена")
                return resp

            elif "delete_all_cookies" in request.form:
                resp = make_response(redirect(url_for("users.profile")))

                for key in list(request.cookies.keys()):
                    resp.delete_cookie(key)

                flash("Всі кукі були успішно видалені")
                return resp

        cookies = request.cookies
        theme = request.cookies.get("theme", "light")

        return render_template("profile.html", cookies=cookies, theme=theme)

    flash("You need to login in", "error")
    return redirect(url_for("users.login"))

@user_bp.route("/logout")
def logout():
    if "username" in session:
        del session["username"]

    return redirect(url_for("users.login"))

@user_bp.route("/profile/theme", methods=["POST"])
def change_theme():
    if "username" not in session:
        flash("You need to login in", "error")
        return redirect(url_for("users.login"))

    theme = request.form.get("theme")

    if theme not in ["light", "dark"]:
        flash("Невідома кольорова схема!", "error")
        return redirect(url_for("users.profile"))

    resp = make_response(redirect(url_for("users.profile")))
    resp.set_cookie("theme", theme, max_age=60 * 60 * 24 * 30)

    flash("Кольорову схему успішно змінено!")
    return resp