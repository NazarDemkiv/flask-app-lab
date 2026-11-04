from flask import Blueprint

product_bp = Blueprint(
    "products",
    __name__,
    template_folder="templates/products",
    static_folder="static",
    static_url_path="/products/static",
)

from . import views  # noqa: E402,F401
