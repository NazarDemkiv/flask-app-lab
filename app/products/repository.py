from pathlib import Path

from flask import current_app
from tinydb import Query, TinyDB


def _database_path() -> Path:
    default_path = Path(__file__).resolve().parents[2] / "data" / "products.json"
    path = Path(current_app.config.get("PRODUCTS_DB_PATH", default_path))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_all_products() -> list[dict]:
    with TinyDB(_database_path()) as db:
        products = db.table("products").all()
    return sorted(products, key=lambda product: product["id"])


def get_product(product_id: int) -> dict | None:
    with TinyDB(_database_path()) as db:
        return db.table("products").get(Query().id == product_id)


def create_product(product_data: dict) -> dict:
    with TinyDB(_database_path()) as db:
        table = db.table("products")
        next_id = max((item["id"] for item in table.all()), default=0) + 1
        product = {**product_data, "id": next_id}
        table.insert(product)
    return product


def update_product(product_id: int, product_data: dict) -> bool:
    with TinyDB(_database_path()) as db:
        table = db.table("products")
        updated = table.update(product_data, Query().id == product_id)
    return bool(updated)


def delete_product(product_id: int) -> bool:
    with TinyDB(_database_path()) as db:
        table = db.table("products")
        removed = table.remove(Query().id == product_id)
    return bool(removed)
