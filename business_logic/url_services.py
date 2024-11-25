import hashlib
from datetime import datetime, timedelta
from models import URLLink, URLStats
from db import db
from config import IST_OFFSET, BASE_URL


def get_current_time_ist():
    """
    Get the current time in IST as a naive datetime object.
    """
    utc_now = datetime.utcnow()
    return utc_now + IST_OFFSET


def generate_short_url(long_url):
    return hashlib.md5(long_url.encode()).hexdigest()[:6]


def shorten_url(long_url):
    existing_link = URLLink.query.filter_by(long_url=long_url).first()
    current_time_ist = get_current_time_ist()

    if existing_link:
        # Check if the existing link is expired
        if (
            existing_link.expiration_time
            and existing_link.expiration_time < current_time_ist
        ):
            existing_link.expiration_time = current_time_ist + timedelta(minutes=30)
            db.session.commit()
        return BASE_URL + existing_link.short_url

    short_url = generate_short_url(long_url)
    expiration_time = current_time_ist + timedelta(minutes=30)

    # Create a new link with expiration time
    new_link = URLLink(
        long_url=long_url, short_url=short_url, expiration_time=expiration_time
    )
    db.session.add(new_link)
    db.session.flush()

    new_stats = URLStats(url_id=new_link.id)
    db.session.add(new_stats)

    db.session.commit()

    return BASE_URL + short_url


def get_original_url(short_url):
    link = URLLink.query.filter_by(short_url=short_url).first()
    if link:
        current_time_ist = get_current_time_ist()

        # Check if the link has expired
        if link.expiration_time and link.expiration_time < current_time_ist:
            return None
        return link.long_url
    return None


def increment_access_count(short_url):
    link = URLLink.query.filter_by(short_url=short_url).first()
    if link and link.stats:
        link.stats.access_count += 1
        link.stats.last_accessed = get_current_time_ist()
        db.session.commit()
