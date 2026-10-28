from flask import render_template, abort
from . import product_bp

products = [
    {
        "id": 1,
        "name":"Laptop",
        "price": 1200,
        "content": "Потужний ноутбук з процесором Intel Core i7, 16 ГБ оперативної пам'яті та SSD на 512 ГБ."
    },
    {
        "id": 2,
        "name": "Phone",
        "price": 800,
        "content": "Смартфон із 6.5-дюймовим OLED-дисплеем, подвійною камерою та акумулятором на 5000 мА-год."
    },
    {
        "id": 3,
        "name": "PC",
        "price": 1800,
        "content": "Настільний комп'ютер для ігор або роботи з графікою: RTX 4070, 32 ГБ RAM, 1 ТБ SSD."
    }
]

@product_bp.route("/items")
def products_items():
    return render_template("products.html", products=products)

@product_bp.route("/items/<int:id>")
def product_by_id(id):
    product = None

    for index in range(len(products)):
        if products[index]["id"] == id:
            product = products[index]
            break

    if product is None:
        abort(404)

    return render_template("detail_product.html", product=product)