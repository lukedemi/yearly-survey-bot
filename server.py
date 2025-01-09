import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables from .env file
load_dotenv()

JSONBIN_COLLECTION_ID = "67800286ad19ca34f8e86182"
JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY")
if not JSONBIN_API_KEY:
    raise ValueError("JSONBIN_API_KEY is not set in the environment or .env file")


app = Flask(__name__)


@app.route("/slack/events", methods=["POST"])
def handle_interactivity():
    try:
        # Parse payload
        payload = request.form.get("payload")
        if not payload:
            return jsonify({"error": "No payload found"}), 400
        payload = json.loads(payload)

        # Defensive parsing of the payload
        user_id = payload.get("user", {}).get("username", "unknown_user")
        state_values = payload.get("state", {}).get("values", {})
        actions = payload.get("actions", [])

        # Extracting form responses from state.values
        formatted_responses = {}
        for block_id, block_data in state_values.items():
            for action_id, action_data in block_data.items():
                if action_data["type"] == "checkboxes":
                    # For checkboxes, get selected options
                    formatted_responses[action_id] = [
                        option["text"]["text"]
                        for option in action_data.get("selected_options", [])
                    ]
                elif action_data["type"] == "plain_text_input":
                    # For text inputs, get the entered value
                    formatted_responses[action_id] = action_data.get("value", "")

        # Format the response
        response = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "responses": formatted_responses,
            "actions": actions,  # Include actions for additional context
        }

        # Log response to a file
        with open("responses.log", "a") as log_file:
            log_file.write(json.dumps(response, indent=4) + "\n")

        # Upload to JSONBin.io
        upload_to_jsonbin(response)

        return jsonify({"text": "Thank you for completing the survey!"})

    except Exception as e:
        # Handle any unexpected errors
        print(f"Error handling interactivity: {e}")
        return jsonify({"error": "Something went wrong"}), 500


def upload_to_jsonbin(data):
    """Upload responses to JSONBin.io."""
    try:
        headers = {"Content-Type": "application/json", "X-Master-Key": JSONBIN_API_KEY}
        # Check if we have a collection ID to organize data
        if JSONBIN_COLLECTION_ID:
            headers["X-Collection-Id"] = JSONBIN_COLLECTION_ID

        # Make the POST request to JSONBin.io
        response = requests.post(
            "https://api.jsonbin.io/v3/b",  # JSONBin.io create bin endpoint
            headers=headers,
            json={"data": data},
        )
        if response.status_code == 200 or response.status_code == 201:
            print(
                f"Successfully uploaded to JSONBin.io: {response.json()['metadata']['id']}"
            )
        else:
            print(
                f"Failed to upload to JSONBin.io: {response.status_code} {response.text}"
            )
    except Exception as e:
        print(f"Error uploading to JSONBin.io: {e}")


if __name__ == "__main__":
    app.run(port=9340)
