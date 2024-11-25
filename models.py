from db import db
from sqlalchemy.sql import func


class URLLink(db.Model):
    __tablename__ = "url_links"
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(2048), nullable=False, unique=True)
    short_url = db.Column(db.String(10), nullable=False, unique=True)
    expiration_time = db.Column(db.DateTime, nullable=True)


class URLStats(db.Model):
    __tablename__ = "url_stats"
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey("url_links.id"), nullable=False)
    access_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    link = db.relationship("URLLink", backref=db.backref("stats", uselist=False))
