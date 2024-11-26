from business_logic.url_services import URLShortenerService
from utils import URLValidator


class URLShortenerAPI:
    def __init__(self):
        self.url_validator = URLValidator()
        self.url_shortener_service = URLShortenerService()

    def shorten(self, data):
        """
        Shorten a long URL
        ---
        tags:
          - URL Shortener
        parameters:
          - name: data
            in: body
            required: true
            schema:
              type: object
              properties:
                long_url:
                  type: string
                  description: The URL to be shortened
        responses:
          201:
            description: Shortened URL successfully created
            schema:
              type: object
              properties:
                short_url:
                  type: string
          400:
            description: Invalid input
          500:
            description: Internal server error
        """
        try:
            if not data:
                return {"error": "No data provided"}, 400

            long_url = data.get("long_url")

            if not long_url:
                return {"error": "Missing 'long_url' field in request body"}, 400

            if not isinstance(long_url, str):
                return {"error": "'long_url' must be a string"}, 400

            if not self.url_validator.is_valid_url(long_url):
                return {"error": "Invalid URL format"}, 400

            short_url = self.url_shortener_service.shorten_url(long_url)

            if not short_url:
                return {"error": "Failed to generate short URL, please try again"}, 500

            return {"short_url": short_url}, 201

        except Exception as e:
            return {"error": str(e)}, 500

    def redirect_to_long(self, short_url):
        """
        Redirect to the original URL
        ---
        tags:
          - URL Shortener
        parameters:
          - name: short_url
            in: path
            type: string
            required: true
            description: The shortened URL
        responses:
          200:
            description: Original URL successfully retrieved
            schema:
              type: object
              properties:
                original_url:
                  type: string
          404:
            description: Shortened URL not found
          500:
            description: Internal server error
        """
        try:
            long_url = self.url_shortener_service.get_original_url(short_url)

            if not long_url:
                return {"error": "URL not found"}, 404

            self.url_shortener_service.increment_access_count(short_url)

            return {"original_url": long_url}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def get_paginated_stats_route(self, page, page_size):
        """
        Get paginated statistics of shortened URLs
        ---
        tags:
          - URL Statistics
        parameters:
          - name: page
            in: query
            type: integer
            required: true
            description: The page number
          - name: page_size
            in: query
            type: integer
            required: true
            description: The number of records per page
        responses:
          200:
            description: Paginated URL statistics
            schema:
              type: object
              properties:
                total_records:
                  type: integer
                total_pages:
                  type: integer
                current_page:
                  type: integer
                records:
                  type: array
                  items:
                    type: object
                    properties:
                      short_url:
                        type: string
                      original_url:
                        type: string
                      access_count:
                        type: integer
          404:
            description: Page not found
          500:
            description: Internal server error
        """
        try:
            total_records = self.url_shortener_service.get_total_record_count()
            if total_records == 0:
                return {"message": "No data available."}, 200

            total_pages = (total_records + page_size - 1) // page_size

            if page > total_pages and total_records > 0:
                return {"error": f"Page {page} exceeds total pages {total_pages}."}, 404

            records = self.url_shortener_service.get_paginated_stats(page, page_size)

            response = {
                "total_records": total_records,
                "total_pages": total_pages,
                "current_page": page,
                "records": records,
            }

            return response, 200

        except Exception as e:
            return {"error": "An unexpected error occurred.", "details": str(e)}, 500
