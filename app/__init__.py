from flask import Flask, render_template
from flask_session import Session

app = Flask(__name__)
app.secret_key = "_my_secret_key_"

app.config["SESSION_PERMANENT"] = False 
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

from . import views

from .users import user_bp
from .products import product_bp

app.register_blueprint(user_bp)
app.register_blueprint(product_bp)