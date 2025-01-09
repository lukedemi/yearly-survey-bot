import os
import time
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables from .env file
load_dotenv()

# Set your bot token
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN is not set in the environment or .env file")

client = WebClient(token=SLACK_BOT_TOKEN)


def get_all_users():
    """Fetch all users in the Slack workspace."""
    try:
        response = client.users_list()
        users = response["members"]
        return [
            user
            for user in users
            if not user["is_bot"]
            and not user["deleted"]  # Exclude bots and deactivated users
        ]
    except SlackApiError as e:
        print(f"Error fetching users: {e.response['error']}")
        return []


def send_message(user_id, message):
    """Send a message to a specific user."""
    try:
        client.chat_postMessage(channel=user_id, text=message)
        print(f"Message sent to {user_id}")
    except SlackApiError as e:
        print(f"Error sending message to {user_id}: {e.response['error']}")


def send_interactive_message(user_id):
    """Send a multiple-choice question with buttons (inline message)."""
    try:
        response = client.chat_postMessage(
            channel=user_id,
            text="Your feedback is valuable!",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":wave: Hey!\n\nThis year we hacked up this little Slack app to do the survey (Polly would have cost thousands!).",
                    },
                },
                {
                    "type": "input",
                    "element": {
                        "type": "checkboxes",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Participating in a hackathon",
                                    "emoji": True,
                                },
                                "value": "value-0",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Giving a talk (we are always looking for speakers and will provide coaching and prep help!)",
                                    "emoji": True,
                                },
                                "value": "value-1",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Volunteering to help on the day of events (greeting, AV, moving chairs)",
                                    "emoji": True,
                                },
                                "value": "value-2",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Being on-call as a backup speaker in case someone drops out",
                                    "emoji": True,
                                },
                                "value": "value-3",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Creating or curating content (like slides, graphics, or notes) for community use",
                                    "emoji": True,
                                },
                                "value": "value-4",
                            },
                        ],
                        "action_id": "checkboxes-action",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Which of the following could you be interested in this year?",
                        "emoji": True,
                    },
                    "optional": True,
                },
                {
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "What are some topics/themes you'd want to hear talks about this year?",
                        "emoji": True,
                    },
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "topics",
                    },
                    "optional": True,
                },
                {
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "Were there any talks/topics from 2024 that particularly resonated with you?",
                        "emoji": True,
                    },
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "2024",
                    },
                    "optional": True,
                },
                {
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "Anything else you'd like to share?",
                        "emoji": True,
                    },
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "other",
                    },
                    "optional": True,
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "If you get a an error ping <@U039KPWCFEF> to fix the server",
                    },
                },
                {
                    "type": "actions",
                    "block_id": "submit_block",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Submit",
                                "emoji": True,
                            },
                            "style": "primary",
                            "action_id": "submit_survey",
                        }
                    ],
                },
            ],
        )
        return response
    except SlackApiError as e:
        print(f"Error sending interactive message: {e.response['error']}")
        return None


def split_users_to_files():
    users = get_all_users()

    file_handles = [open(f"user_lists/users_{i:02}.txt", "w") for i in range(1, 11)]

    for idx, user in enumerate(users):
        file_index = idx % 10  # Determine file number (0-9 for 10 files)
        file_handles[file_index].write(user["id"] + "\n")

    # Close all files
    for handle in file_handles:
        handle.close()


# Function to read already messaged user IDs from a file
def load_messaged_users(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return set(f.read().splitlines())
    return set()


# Function to save successfully messaged user IDs to a file
def save_messaged_user(file_path, user_id):
    with open(file_path, "a") as f:
        f.write(user_id + "\n")


def main():
    # for user in users:
    #     user_id = user["id"]
    #     name = user["name"]
    #     print(user_id, name)

    # send_interactive_message("U051D560A2F")  # Luke W
    # send_interactive_message("U05GCUP9PQ9")  # Rick
    # send_interactive_message("U04T63QT4TC")  # cody
    # send_interactive_message("U04V579R2")  # jdboyd
    # send_interactive_message("U01B66ZNCQK")  # tims
    # send_interactive_message("U045QC8DM")  # zach
    # response = send_interactive_message("U039KPWCFEF")  # Luke D
    # print(response["ok"])

    input_file = (
        "user_lists/users_test.txt"  # Replace with the file you want to process
    )
    messaged_users_file = "messaged_users.txt"

    # Load the list of already messaged users
    messaged_users = load_messaged_users(messaged_users_file)

    # Process each user in the input file
    with open(input_file, "r") as f:
        for user_id in f:
            user_id = user_id.strip()
            if user_id in messaged_users:
                print(f"Skipping {user_id}, already messaged.")
                continue

            # Send an interactive message
            time.sleep(1.5)
            response = send_interactive_message(user_id)
            if response["ok"]:
                print(f"Message sent to {user_id}.")
                save_messaged_user(messaged_users_file, user_id)
                messaged_users.add(user_id)  # Update in-memory set
            else:
                print(f"Failed to send message to {user_id}.")


if __name__ == "__main__":
    main()
