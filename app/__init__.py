from flask import Flask, render_template

app = Flask(__name__)

from . import views

from .users import user_bp
from .products import product_bp

app.register_blueprint(user_bp)
app.register_blueprint(product_bp)