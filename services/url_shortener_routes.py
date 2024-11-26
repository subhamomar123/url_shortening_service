from flask import Blueprint, request, jsonify
from flasgger import swag_from
from url_shortener_api import URLShortenerAPI

url_shortener_blueprint = Blueprint("url_shortener", __name__)

url_shortener_api = URLShortenerAPI()


@url_shortener_blueprint.route("/shorten", methods=["POST"])
@swag_from(
    {
        "tags": ["Shorten URL"],
        "summary": "Shorten a long URL",
        "parameters": [
            {
                "name": "data",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "long_url": {
                            "type": "string",
                            "description": "The URL to be shortened",
                        },
                    },
                },
            }
        ],
        "responses": {
            "201": {"description": "Shortened URL created successfully"},
            "400": {"description": "Invalid input"},
            "500": {"description": "Internal server error"},
        },
    }
)
def shorten():
    """Shorten a long URL."""
    data = request.json
    response, status_code = url_shortener_api.shorten(data)
    return jsonify(response), status_code


@url_shortener_blueprint.route("/<short_url>", methods=["GET"])
@swag_from(
    {
        "tags": ["Redirect URL"],
        "summary": "Redirect to the original URL using the shortened URL",
        "parameters": [
            {
                "name": "short_url",
                "in": "path",
                "type": "string",
                "required": True,
                "description": "The shortened URL",
            }
        ],
        "responses": {
            "200": {"description": "Original URL retrieved successfully"},
            "404": {"description": "Short URL not found"},
            "500": {"description": "Internal server error"},
        },
    }
)
def redirect_to_long(short_url):
    """Redirect to the original URL."""
    response, status_code = url_shortener_api.redirect_to_long(short_url)
    return jsonify(response), status_code


@url_shortener_blueprint.route("/stats", methods=["GET"])
@swag_from(
    {
        "tags": ["Statistics"],
        "summary": "Retrieve paginated statistics of shortened URLs",
        "parameters": [
            {
                "name": "page",
                "in": "query",
                "type": "integer",
                "required": False,
                "description": "The page number for pagination",
            },
            {
                "name": "page_size",
                "in": "query",
                "type": "integer",
                "required": False,
                "description": "The number of records per page",
            },
        ],
        "responses": {
            "200": {"description": "Statistics retrieved successfully"},
            "400": {"description": "Invalid pagination parameters"},
            "500": {"description": "Internal server error"},
        },
    }
)
def get_paginated_stats_route():
    """Retrieve paginated statistics."""
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))

        # Validate pagination parameters
        if page <= 0 or page_size <= 0:
            return (
                jsonify({"error": "Pagination parameters must be positive integers."}),
                400,
            )

        response, status_code = url_shortener_api.get_paginated_stats_route(
            page, page_size
        )
        return jsonify(response), status_code

    except ValueError:
        return jsonify({"error": "Invalid pagination parameters."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
