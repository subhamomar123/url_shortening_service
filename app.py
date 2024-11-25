from flask import Flask
from db import db
from services.url_shortener_routes import url_shortener_blueprint

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///url_shortener.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.register_blueprint(url_shortener_blueprint)

db.init_app(app)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
