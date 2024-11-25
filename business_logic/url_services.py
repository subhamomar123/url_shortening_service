import hashlib
from datetime import datetime, timedelta
from models import URLLink, URLStats
from db import db
from config import IST_OFFSET, BASE_URL


class URLShortenerService:

    @staticmethod
    def get_current_time_ist():
        """
        Get the current time in IST as a naive datetime object.
        """
        utc_now = datetime.utcnow()
        return utc_now + IST_OFFSET

    @staticmethod
    def generate_short_url(long_url):
        """
        Generate a short URL by hashing the long URL and returning the first 6 characters.
        """
        return hashlib.md5(long_url.encode()).hexdigest()[:6]

    @classmethod
    def shorten_url(cls, long_url):
        """
        Shorten the provided long URL. If it already exists in the database and is not expired,
        return the existing short URL. Otherwise, create a new one.
        """
        existing_link = URLLink.query.filter_by(long_url=long_url).first()
        current_time_ist = cls.get_current_time_ist()

        if existing_link:
            if (
                existing_link.expiration_time
                and existing_link.expiration_time < current_time_ist
            ):
                existing_link.expiration_time = current_time_ist + timedelta(minutes=30)
                db.session.commit()
            return BASE_URL + existing_link.short_url

        short_url = cls.generate_short_url(long_url)
        expiration_time = current_time_ist + timedelta(minutes=30)

        new_link = URLLink(
            long_url=long_url, short_url=short_url, expiration_time=expiration_time
        )
        db.session.add(new_link)
        db.session.flush()

        new_stats = URLStats(url_id=new_link.id)
        db.session.add(new_stats)

        db.session.commit()

        return BASE_URL + short_url

    @classmethod
    def get_original_url(cls, short_url):
        """
        Retrieve the original URL corresponding to a short URL. Returns None if the short URL is expired or does not exist.
        """
        link = URLLink.query.filter_by(short_url=short_url).first()
        if link:
            current_time_ist = cls.get_current_time_ist()

            if link.expiration_time and link.expiration_time < current_time_ist:
                return None
            return link.long_url
        return None

    @classmethod
    def increment_access_count(cls, short_url):
        """
        Increment the access count and update the last accessed time for the given short URL.
        """
        link = URLLink.query.filter_by(short_url=short_url).first()
        if link and link.stats:
            link.stats.access_count += 1
            link.stats.last_accessed = cls.get_current_time_ist()
            db.session.commit()

    @staticmethod
    def get_stats_query():
        """
        Helper function to create and return the base stats query.
        """
        return (
            db.session.query(
                URLLink.long_url,
                URLLink.short_url,
                URLStats.access_count,
                URLStats.last_accessed,
            )
            .join(URLStats, URLLink.id == URLStats.url_id)
            .order_by(URLStats.last_accessed.desc())
        )

    @classmethod
    def get_total_record_count(cls):
        """
        Get the total record count from the stats query.
        """
        stats_query = cls.get_stats_query()
        return stats_query.count()

    @classmethod
    def get_paginated_stats(cls, page, page_size):
        """
        Fetch paginated URL stats from the database.
        """
        stats_query = cls.get_stats_query()

        paginated_stats = (
            stats_query.offset((page - 1) * page_size).limit(page_size).all()
        )

        records = [
            {
                "long_url": stat.long_url,
                "short_url": stat.short_url,
                "access_count": stat.access_count,
                "last_accessed": (
                    stat.last_accessed.strftime("%Y-%m-%d %H:%M:%S")
                    if stat.last_accessed
                    else None
                ),
            }
            for stat in paginated_stats
        ]

        return records
