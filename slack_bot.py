import os
import slack_sdk
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError

# Initialize a Web API client
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

def distribute_bacon(amount, user):
    # Logic to interact with the Bacon system and distribute tokens
    # This is a placeholder function and should be implemented with actual logic
    print(f"Distributing {amount} bacon to {user}")

def handle_command(command, user_id):
    try:
        if command.startswith('/distribute'):
            parts = command.split()
            if len(parts) == 4 and parts[2].lower() == 'bacon':
                amount = int(parts[1])
                user = parts[3]
                distribute_bacon(amount, user)
                client.chat_postMessage(channel=user_id, text=f"Distributed {amount} bacon to {user}")
            else:
                client.chat_postMessage(channel=user_id, text="Invalid command format. Use /distribute <amount> bacon @<user>")
        else:
            client.chat_postMessage(channel=user_id, text="Unknown command")
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")

if __name__ == "__main__":
    from flask import Flask, request, jsonify

    app = Flask(__name__)

    @app.route("/slack/events", methods=["POST"])
    def slack_events():
        data = request.json
        if "challenge" in data:
            return jsonify({"challenge": data["challenge"]})
        if "event" in data:
            event = data["event"]
            if event["type"] == "app_mention":
                user_id = event["user"]
                text = event["text"]
                handle_command(text, user_id)
        return jsonify({"status": "ok"})

    app.run(port=3000)
