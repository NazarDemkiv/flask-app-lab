import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from app import app


class ProductCrudTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_path = app.config.get("PRODUCTS_DB_PATH")
        self.old_csrf = app.config.get("WTF_CSRF_ENABLED", True)
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            PRODUCTS_DB_PATH=Path(self.temp_dir.name) / "products.json",
        )
        self.client = app.test_client()

    def tearDown(self):
        if self.old_db_path is None:
            app.config.pop("PRODUCTS_DB_PATH", None)
        else:
            app.config["PRODUCTS_DB_PATH"] = self.old_db_path
        app.config["WTF_CSRF_ENABLED"] = self.old_csrf
        self.temp_dir.cleanup()

    def create_product(self, **overrides):
        data = {
            "name": "Test laptop",
            "content": "A test product description",
            "price": "1250.50",
            "category": "electronics",
            "quantity": "4",
            "image": (BytesIO(b"\x89PNG\r\n\x1a\n" + b"fake image data"), "laptop.png"),
        }
        data.update(overrides)
        return self.client.post("/product/add", data=data, content_type="multipart/form-data", follow_redirects=False)

    def test_create_and_read_product(self):
        response = self.create_product()
        self.assertEqual(response.status_code, 302)

        listing = self.client.get("/product")
        self.assertEqual(listing.status_code, 200)
        self.assertIn(b"Test laptop", listing.data)
        self.assertIn(b"1250.50", listing.data)

        detail = self.client.get("/product/1")
        self.assertEqual(detail.status_code, 200)
        self.assertIn(b"A test product description", detail.data)
        self.assertIn(b"electronics", detail.data)

    def test_validation_rejects_invalid_product(self):
        response = self.create_product(name="AB", price="-5")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Не вдалося додати товар".encode(), response.data)
        self.assertEqual(self.client.get("/product").status_code, 200)
        self.assertNotIn(b"Test laptop", self.client.get("/product").data)

    def test_update_preserves_id_and_created_at(self):
        self.create_product()
        detail_before = self.client.get("/product/1")
        self.assertEqual(detail_before.status_code, 200)

        response = self.client.post(
            "/product/1/edit",
            data={
                "name": "Updated laptop",
                "content": "Updated description",
                "price": "999.99",
                "category": "electronics",
                "quantity": "8",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Updated laptop", response.data)
        self.assertIn(b"999.99", response.data)
        self.assertIn(b"ID:</strong> 1", response.data)

    def test_delete_product(self):
        self.create_product()
        response = self.client.post("/product/1/delete", data={}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("видалено".encode(), response.data)
        self.assertIn("товарів немає".encode(), response.data)

    def test_missing_product_returns_404(self):
        self.assertEqual(self.client.get("/product/999").status_code, 404)
        self.assertEqual(self.client.get("/product/999/edit").status_code, 404)
        self.assertEqual(self.client.post("/product/999/delete").status_code, 404)

    def test_price_rejects_more_than_two_decimal_places(self):
        response = self.create_product(price="12.345")
        self.assertEqual(response.status_code, 200)
        self.assertIn("не більше двох знаків".encode(), response.data)

    def test_image_extension_validation(self):
        response = self.create_product(image=(BytesIO(b"not an image"), "document.pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"File does not have an approved extension", response.data)


if __name__ == "__main__":
    unittest.main()
