import os
import requests
from flask import Flask, request, jsonify

# Create a Flask application instance.
app = Flask(__name__)

# The main URL to which the proxy will forward data.
# This value is retrieved from the Vercel environment variables.
# For security, you must set the PRIVATE_API_URL in your Vercel dashboard.
# DO NOT hardcode your URL here.
MAIN_API_URL = os.environ.get("PRIVATE_API_URL")

@app.route("/", defaults={"path": ""}, methods=["POST"])
@app.route("/<path:path>", methods=["POST"])
def proxy(path):
    """
    This function acts as a proxy, forwarding POST requests to a main API.

    It receives data from an Android client, forwards it to the specified
    MAIN_API_URL, and returns the response received from that URL back to
    the Android client.
    """
    # Check if the main API URL is set.
    if not MAIN_API_URL:
        # If the environment variable is missing, return an error message.
        return jsonify({"error": "Configuration error: Main API URL not set."}), 500

    try:
        # Get the JSON data from the incoming request.
        request_data = request.get_json(silent=True)
        if not request_data:
            return jsonify({"error": "No JSON data received."}), 400

        # Construct the full URL to forward the request to.
        # This appends any path parameters from the incoming request.
        full_forward_url = f"{MAIN_API_URL}/{path}"

        # Forward the POST request to the main API.
        # The json parameter automatically handles sending the data as JSON.
        response = requests.post(full_forward_url, json=request_data)

        # Check if the forwarding was successful.
        response.raise_for_status()

        # Return the response content and status code directly from the main API.
        return (response.content, response.status_code, response.headers.items())

    except requests.exceptions.RequestException as e:
        # If there's an error connecting to the main API, return an error.
        return jsonify({"error": f"Failed to forward request: {str(e)}"}), 502
    except Exception as e:
        # Catch any other unexpected errors.
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
