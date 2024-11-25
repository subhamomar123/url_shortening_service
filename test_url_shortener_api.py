import unittest
from flask import Flask, jsonify
from services.url_shortener_routes import url_shortener_blueprint
from db import db


class TestURLShortenerAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Runs once before all tests"""
        cls.app = Flask(__name__)
        cls.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        cls.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        cls.app.register_blueprint(url_shortener_blueprint)
        db.init_app(cls.app)
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Runs once after all tests"""
        with cls.app.app_context():
            db.drop_all()

    def setUp(self):
        """Runs before each test"""
        self.client = self.app.test_client()

    def tearDown(self):
        """Runs after each test"""
        pass

    def test_shorten_valid_url(self):
        """Test shortening a valid URL"""
        data = {"long_url": "https://www.example.com"}
        response = self.client.post("/shorten", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("short_url", response.json)

    def test_shorten_invalid_url_format(self):
        """Test shortening an invalid URL format"""
        data = {"long_url": "htp://invalid-url"}
        response = self.client.post("/shorten", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Invalid URL format")

    def test_shorten_no_data(self):
        """Test when no data is provided in the request"""
        response = self.client.post(
            "/shorten", json={}
        )  # Use empty object instead of None
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "No data provided")

    def test_redirect_to_long_url_found(self):
        """Test redirect to long URL when short URL is found"""
        # First, shorten a URL to generate a short URL.
        data = {"long_url": "https://www.example.com"}
        response = self.client.post("/shorten", json=data)
        short_url = response.json["short_url"].split("/")[-1]

        # Now, test redirect to the original long URL
        response = self.client.get(f"/{short_url}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("original_url", response.json)

    def test_redirect_to_long_url_not_found(self):
        """Test redirect to long URL when short URL is not found"""
        response = self.client.get("/nonexistentshorturl")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "URL not found")

    def test_get_paginated_stats(self):
        """Test getting paginated stats"""
        response = self.client.get("/stats?page=1&page_size=10")
        if response.json.get("message") == "No data available.":
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["message"], "No data available.")
        else:
            self.assertEqual(response.status_code, 200)
            self.assertIn("total_records", response.json)

    def test_get_paginated_stats_invalid_page(self):
        """Test invalid page number"""
        response = self.client.get("/stats?page=-1&page_size=10")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["error"], "Pagination parameters must be positive integers."
        )

    def test_get_paginated_stats_no_data(self):
        """Test when no stats are available"""
        response = self.client.get("/stats?page=1&page_size=10")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "No data available.")


if __name__ == "__main__":
    unittest.main()
