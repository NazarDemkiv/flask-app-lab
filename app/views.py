from . import app
from flask import render_template, request, redirect, abort

@app.route("/")
def resume():
    return render_template("resume.html", title="Моє резюме")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html", title="Контакти")

@app.route("/homepage")
def home():
    agent = request.user_agent
    return render_template("resume.html", agent=agent)