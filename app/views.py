import logging

from flask import flash, redirect, render_template, request, url_for

from .forms import ContactForm

logger = logging.getLogger(__name__)


def resume():
    return render_template("resume.html", title="Моє резюме")


def contacts():
    form = ContactForm()
    if form.validate_on_submit():
        logger.info(
            "Contact form submitted: name=%s, email=%s, subject=%s",
            form.name.data,
            form.email.data,
            form.subject.data,
        )
        flash("Повідомлення успішно надіслано.", "success")
        return redirect(url_for("contacts"))

    return render_template("contacts.html", title="Контакти", form=form)


def home():
    agent = request.user_agent
    return render_template("resume.html", title="Головна", agent=agent)


def register_main_routes(app):
    """Register legacy site pages without creating a second Flask app."""
    app.add_url_rule("/", endpoint="resume", view_func=resume)
    app.add_url_rule(
        "/contacts", endpoint="contacts", view_func=contacts, methods=["GET", "POST"]
    )
    app.add_url_rule("/homepage", endpoint="home", view_func=home)
