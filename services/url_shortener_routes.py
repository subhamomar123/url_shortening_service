from flask import Blueprint, request, jsonify
from business_logic.url_services import (
    shorten_url,
    get_original_url,
    increment_access_count,
)
from utils import is_valid_url
from models import URLLink, URLStats
from db import db

url_shortener_blueprint = Blueprint("url_shortener", __name__)


@url_shortener_blueprint.route("/shorten", methods=["POST"])
def shorten():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No data provided"}), 400

        long_url = data.get("long_url")

        if not long_url:
            return jsonify({"error": "Missing 'long_url' field in request body"}), 400

        if not isinstance(long_url, str):
            return jsonify({"error": "'long_url' must be a string"}), 400

        if not is_valid_url(long_url):
            return jsonify({"error": "Invalid URL format"}), 400

        short_url = shorten_url(long_url)

        if not short_url:
            return (
                jsonify({"error": "Failed to generate short URL, please try again"}),
                500,
            )

        return jsonify({"short_url": short_url}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@url_shortener_blueprint.route("/<short_url>", methods=["GET"])
def redirect_to_long(short_url):
    try:
        long_url = get_original_url(short_url)

        if not long_url:
            return jsonify({"error": "URL not found"}), 404

        increment_access_count(short_url)

        return jsonify({"original_url": long_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@url_shortener_blueprint.route("/stats", methods=["GET"])
def get_paginated_stats():
    """
    Fetch paginated URL stats.
    """
    try:
        # Validate and extract pagination parameters
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))
        if page <= 0 or page_size <= 0:
            raise ValueError("Pagination parameters must be positive integers.")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        # Query the database for URL stats
        stats_query = (
            db.session.query(
                URLLink.long_url,
                URLLink.short_url,
                URLStats.access_count,
                URLStats.last_accessed,
            )
            .join(URLStats, URLLink.id == URLStats.url_id)
            .order_by(URLStats.last_accessed.desc())  # Sort by last accessed time
        )

        total_records = stats_query.count()
        if total_records == 0:
            return jsonify({"message": "No data available."}), 200

        total_pages = (total_records + page_size - 1) // page_size

        # Handle invalid page numbers
        if page > total_pages and total_records > 0:
            return (
                jsonify({"error": f"Page {page} exceeds total pages {total_pages}."}),
                404,
            )

        # Fetch paginated data
        paginated_stats = (
            stats_query.offset((page - 1) * page_size).limit(page_size).all()
        )

        # Prepare records for response
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

        response = {
            "total_records": total_records,
            "total_pages": total_pages,
            "current_page": page,
            "records": records,
        }
        return jsonify(response), 200

    except Exception as e:
        return (
            jsonify({"error": "An unexpected error occurred.", "details": str(e)}),
            500,
        )
