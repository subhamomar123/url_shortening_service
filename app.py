from flask import Flask
from flasgger import Swagger


class URLShortenerApp:
    def __init__(self, config=None):
        self.app = Flask(__name__)
        self.config = (
            config
            if config
            else {
                "SQLALCHEMY_DATABASE_URI": "sqlite:///url_shortener.db",
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SWAGGER": {
                    "title": "URL Shortener Service",
                    "uiversion": 3,
                },
            }
        )
        self._configure_app()
        self.swagger = Swagger(self.app)  # Initialize Swagger

    def _configure_app(self):
        """Set up app configurations"""
        self.app.config.update(self.config)

    def _register_blueprints(self):
        """Register blueprints for routes"""
        from services.url_shortener_routes import url_shortener_blueprint

        self.app.register_blueprint(url_shortener_blueprint, url_prefix="/api")

    def _initialize_db(self):
        """Initialize database with app context"""
        from db import db

        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def run(self):
        """Run the Flask application"""
        self.app.run(debug=True)

    def setup(self):
        """Set up the application (configure, register blueprints, initialize DB)"""
        self._register_blueprints()
        self._initialize_db()


if __name__ == "__main__":
    app_instance = URLShortenerApp()
    app_instance.setup()
    app_instance.run()
