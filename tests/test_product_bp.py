import unittest
from app import app

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_products_list(self):
        response = self.client.get("/products/items")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)
        self.assertIn(b"Phone", response.data)
        self.assertIn(b"PC", response.data)

    def test_product_detail(self):
        response = self.client.get("/products/items/1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)
        self.assertIn(b"1200", response.data)
        self.assertIn(b"Intel Core i7", response.data)

    def test_product_not_found(self):
        response = self.client.get("/products/items/999")
        self.assertEqual(response.status_code, 404)

    def test_invalid_product_id(self):
        response = self.client.get("/products/items/abc")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()