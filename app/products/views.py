from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import abort, current_app, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from . import product_bp
from . import repository
from .forms import DeleteProductForm, ProductCreateForm, ProductEditForm

UPLOAD_FOLDER = Path(__file__).resolve().parent / "static" / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def _save_image(uploaded_file) -> str:
    original_name = secure_filename(uploaded_file.filename or "")
    extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported image extension")

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.{extension}"
    uploaded_file.save(UPLOAD_FOLDER / filename)
    return f"uploads/{filename}"


def _delete_image(image_path: str | None) -> None:
    if not image_path:
        return
    filename = Path(image_path).name
    target = (UPLOAD_FOLDER / filename).resolve()
    if target.parent == UPLOAD_FOLDER.resolve() and target.is_file():
        target.unlink()


def _with_image_url(product: dict) -> dict:
    result = dict(product)
    image_path = result.get("image")
    if image_path:
        filename = Path(image_path).name
        image_file = UPLOAD_FOLDER / filename
        result["image_url"] = (
            url_for("products.static", filename=f"uploads/{filename}")
            if image_file.is_file()
            else None
        )
    else:
        result["image_url"] = None
    return result


def _form_values(form) -> dict:
    return {
        "name": form.name.data.strip(),
        "content": form.content.data.strip(),
        # Store as a JSON number rounded to two decimal places.
        "price": round(float(form.price.data), 2),
        "category": form.category.data,
        "quantity": form.quantity.data,
    }


@product_bp.route("/product")
def products_list():
    products = [_with_image_url(item) for item in repository.get_all_products()]
    return render_template("products.html", title="Товари", products=products)


@product_bp.route("/product/add", methods=["GET", "POST"])
def add_product():
    form = ProductCreateForm()
    if form.validate_on_submit():
        image_path = _save_image(form.image.data)
        product_data = _form_values(form)
        product_data.update(
            image=image_path,
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        product = repository.create_product(product_data)
        flash(f"Товар «{product['name']}» успішно додано.", "success")
        return redirect(url_for("products.product_detail", product_id=product["id"]))

    if request.method == "POST":
        flash("Не вдалося додати товар. Перевірте заповнення форми.", "danger")
    return render_template("add_product.html", title="Додати товар", form=form)


@product_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = repository.get_product(product_id)
    if product is None:
        abort(404)
    return render_template(
        "detail_product.html",
        title=product["name"],
        product=_with_image_url(product),
        delete_form=DeleteProductForm(),
    )


@product_bp.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    product = repository.get_product(product_id)
    if product is None:
        abort(404)

    if request.method == "GET":
        form = ProductEditForm(
            data={key: product[key] for key in ("name", "content", "price", "category", "quantity")}
        )
    else:
        form = ProductEditForm()

    if form.validate_on_submit():
        updated_data = _form_values(form)
        uploaded_file = form.image.data
        old_image = product.get("image")
        if uploaded_file and uploaded_file.filename:
            updated_data["image"] = _save_image(uploaded_file)
        repository.update_product(product_id, updated_data)
        if updated_data.get("image") and updated_data["image"] != old_image:
            _delete_image(old_image)
        flash("Інформацію про товар оновлено.", "success")
        return redirect(url_for("products.product_detail", product_id=product_id))

    if request.method == "POST":
        flash("Не вдалося оновити товар. Перевірте заповнення форми.", "danger")
    return render_template(
        "edit_product.html", title="Редагувати товар", form=form, product=product
    )


@product_bp.route("/product/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    product = repository.get_product(product_id)
    if product is None:
        abort(404)

    form = DeleteProductForm()
    if not form.validate_on_submit():
        flash("Не вдалося підтвердити видалення товару.", "danger")
        return redirect(url_for("products.product_detail", product_id=product_id))

    repository.delete_product(product_id)
    _delete_image(product.get("image"))
    flash(f"Товар «{product['name']}» видалено.", "success")
    return redirect(url_for("products.products_list"))


# Compatibility routes for links/tests from the previous laboratory work.
@product_bp.route("/products/items")
def products_items():
    return redirect(url_for("products.products_list"))


@product_bp.route("/products/items/<int:id>")
def product_by_id(id):
    return redirect(url_for("products.product_detail", product_id=id))
