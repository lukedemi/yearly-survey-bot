import os
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
            text="Workplace check-in",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": ":wave: Hey!\n\nThis year we hacked up this little Slack app to do the survey (Polly would have cost $974/month).",
                        "emoji": True,
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
                    "element": {"type": "plain_text_input", "multiline": True},
                    "optional": True,
                },
                {"type": "divider"},
                {
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "Were there any talks/topics from 2024 that particularly resonated with you?",
                        "emoji": True,
                    },
                    "element": {"type": "plain_text_input", "multiline": True},
                    "optional": True,
                },
                {
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "Anything else you'd like to share?",
                        "emoji": True,
                    },
                    "element": {"type": "plain_text_input", "multiline": True},
                    "optional": True,
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


def main():
    # users = get_all_users()

    # for user in users:
    #     print(user)
    #     # user_id = user['id']

    # # U039KPWCFEF = Luke
    # # U05GCUP9PQ9 = Rick
    send_interactive_message("U05GCUP9PQ9")


if __name__ == "__main__":
    main()
