import logging
from . import app
from flask import render_template, request, redirect, url_for, flash
from .forms import ContactForm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("contacts.log", encoding="utf-8"),   # Save to file
        logging.StreamHandler()          # Print to console
    ]
)

logger = logging.getLogger(__name__)

@app.route("/")
def resume():
    return render_template("resume.html", title="Моє резюме")

@app.route("/contacts", methods = ["GET", "POST"])
def contacts():
    cform = ContactForm()

    if cform.validate_on_submit():
        name = cform.name.data
        email = cform.email.data
        phone = cform.phone.data
        subject = cform.subject.data
        message = cform.message.data
        flash("Form successfully sent", "success")

        logger.info("Name: %s, Email: %s, Phone: %s, Subject: %s, Message: %s", name, email, phone, subject, message)
        return redirect(url_for("contacts"))

    return render_template("contacts.html", title="Контакти", form=cform)

@app.route("/homepage")
def home():
    agent = request.user_agent
    return render_template("resume.html", agent=agent)