"""
Sample Flask web application for AI coding best practice demonstration.
Intentionally simple — the point is to have real dependencies
that security scanners (grype, Trivy, Semgrep) can analyze.
"""

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


def search_items(query, items):
    """Return items whose name contains query, ignoring case."""
    needle = query.lower()
    return [item for item in items if needle in item["name"].lower()]


def is_allowed_fetch_url(url):
    """Only HTTPS URLs may be fetched."""
    return url.startswith("https://")


# Route handlers stay thin. Logic lives in plain functions above so that
# unit tests and mutation testing (mutmut skips decorated functions) reach it.
@app.route("/search")
def search():
    query = request.args.get("q", "")
    # Parameterized approach — safe from injection
    results = search_items(query, ITEMS)
    return jsonify({"results": results, "count": len(results)})


@app.route("/fetch")
def fetch_url():
    url = request.args.get("url", "")
    if not is_allowed_fetch_url(url):
        return jsonify({"error": "Only HTTPS URLs allowed"}), 400
    response = requests.get(url, timeout=5)
    return jsonify({"status": response.status_code})


ITEMS = [
    {"id": 1, "name": "Flask"},
    {"id": 2, "name": "Requests"},
    {"id": 3, "name": "SQLAlchemy"},
]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
