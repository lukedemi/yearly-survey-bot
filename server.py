import json
import logging
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables from .env file
load_dotenv()

JSONBIN_COLLECTION_ID = "67800286ad19ca34f8e86182"
JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN is not set in the environment or .env file")
if not JSONBIN_API_KEY:
    raise ValueError("JSONBIN_API_KEY is not set in the environment or .env file")

client = WebClient(token=SLACK_BOT_TOKEN)

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/slack/events", methods=["POST"])
def handle_interactivity():
    try:
        # Parse payload
        payload = request.form.get("payload")
        if not payload:
            return jsonify({"error": "No payload found"}), 400

        # Log everything to a file
        with open("./logs/everything.log", "a") as log_file:
            log_file.write(payload + "\n")

        payload = json.loads(payload)

        # Defensive parsing of the payload
        user_id = payload.get("user", {}).get("id", "unknown_user")
        username = payload.get("user", {}).get("username", "unknown_user")

        # do this asap so we have a record of who has at least touched it
        with open("./logs/seen_users.log", "a") as log_file:
            log_file.write(username + "\n")

        channel_id = payload.get("channel", {}).get("id", "unknown_channel")
        message_ts = payload.get("message", {}).get("ts", "unknown_ts")
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

        for action in actions:
            if action["action_id"] == "submit_survey":
                text = (
                    f"{user_id}\t"
                    f"{'|'.join(map(str, formatted_responses.get('checkboxes-action', []))) or 'None'}\t"
                    f"{formatted_responses.get('topics', 'None')}\t"
                    f"{formatted_responses.get('2024', 'None')}\t"
                    f"{formatted_responses.get('other', 'None')}\n"
                )

                with open("./logs/submitted.tsv", "a") as file:
                    file.write(text)

                update_slack_message(channel_id, message_ts)

                slack_text = (
                    f"<@{user_id}>\n\n"
                    f"Willing to: {', '.join(map(str, formatted_responses['checkboxes-action']))}\n"
                    f"Future topics: {formatted_responses['topics']}\n"
                    f"Fav 2024: {formatted_responses['2024']}\n"
                    f"Other: {formatted_responses['other']}\n"
                )
                client.chat_postMessage(channel="C0880G0AJV9", text=slack_text)
                upload_to_jsonbin(response)

        return jsonify({"text": "Thank you for completing the survey!"})

    except Exception as e:
        # Handle any unexpected errors
        print(f"Error handling interactivity: {e}")
        return jsonify({"error": "Something went wrong"}), 500


def update_slack_message(channel_id, message_ts):
    """Update the Slack message to confirm submission."""
    try:
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="Thank you for your submission!",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":white_check_mark: Thank you for your submission!",
                    },
                }
            ],
        )
        print(f"Successfully updated Slack message in channel {channel_id}")
    except SlackApiError as e:
        print(f"Error updating Slack message: {e.response['error']}")


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
    app.debug = True
    app.run(host="0.0.0.0", port=9340)
