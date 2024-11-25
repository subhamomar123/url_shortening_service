from flask import Blueprint, request, jsonify
from url_shortener_api import URLShortenerAPI

url_shortener_blueprint = Blueprint("url_shortener", __name__)

url_shortener_api = URLShortenerAPI()


@url_shortener_blueprint.route("/shorten", methods=["POST"])
def shorten():
    data = request.json
    response, status_code = url_shortener_api.shorten(data)
    return jsonify(response), status_code


@url_shortener_blueprint.route("/<short_url>", methods=["GET"])
def redirect_to_long(short_url):
    response, status_code = url_shortener_api.redirect_to_long(short_url)
    return jsonify(response), status_code


@url_shortener_blueprint.route("/stats", methods=["GET"])
def get_paginated_stats_route():
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))

        if page <= 0 or page_size <= 0:
            raise ValueError("Pagination parameters must be positive integers.")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    response, status_code = url_shortener_api.get_paginated_stats_route(page, page_size)
    return jsonify(response), status_code
