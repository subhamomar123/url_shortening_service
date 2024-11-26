
# URL Shortening Service

A simple URL shortening service built with Python. This service allows users to shorten URLs, redirect to the original URL, and view usage statistics.

## Features
- Shorten long URLs to compact, shareable links.
- Redirect to original URLs using shortened links.
- Paginated statistics for shortened URLs.
- Integrated Swagger documentation for API endpoints.

## Technologies Used
- Python
- Flask
- SQLite
- Flask-Swagger (Flasgger) for API documentation

---

## Installation

### 1. Clone the Repository:
```bash
git clone https://github.com/subhamomar123/url_shortening_service.git
```

### 2. Install Dependencies:
#### Using a Virtual Environment (Recommended):
1. Create and activate the virtual environment:
   - On **Windows**:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

2. Install required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

---

### 3. Run the Application:
Run the Flask server:
```bash
python app.py
```
The application will be available at: [http://localhost:5000](http://localhost:5000)

---

### 4. Access API Documentation:
The API documentation is accessible via Swagger at:
[http://localhost:5000/apidocs](http://localhost:5000/apidocs)

---

### 5. Run Tests:
Run all test cases to ensure the application is working correctly:
```bash
pytest
```

---

