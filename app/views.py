from . import app
from flask import render_template, request, redirect, url_for, flash
from .forms import ContactForm

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

        print(f"Name: {name}, Email: {email}, Phone: {phone}, Subject: {subject}, Message: {message}")
        return redirect(url_for("contacts"))

    return render_template("contacts.html", title="Контакти", form=cform)

@app.route("/homepage")
def home():
    agent = request.user_agent
    return render_template("resume.html", agent=agent)