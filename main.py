from os import getenv
import threading

from dotenv import load_dotenv
from flask import Flask

from src import Twitch

load_dotenv()

CLIENT_ID = getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = getenv("TWITCH_CLIENT_SECRET")

auth_settings = Twitch.TwitchOAuthSettings(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:8080/oauth",
    scopes=[
        "chat:read",
        "chat:edit",
        "channel:read:redemptions",
        "channel:manage:redemptions",
    ],
)

irc_settings = Twitch.TwitchIRCSettings(
    hostname="irc.chat.twitch.tv", port=6667, bot_nick="malimore", channel="malimore"
)

api_settings = Twitch.TwitchAPISettings(
    client_id=CLIENT_ID,
)

eventsub_settings = Twitch.TwitchEventSubSettings(
    client_id=CLIENT_ID,
    eventsub_ws_url="wss://eventsub.wss.twitch.tv/ws",
)


def main():
    flask_app = Flask(__name__)
    auth_client = Twitch.TwitchOAuthClient(auth_settings, flask_app)
    irc_client = Twitch.TwitchIRCClient(irc_settings)
    api_client = Twitch.TwitchAPIClient(api_settings)
    eventsub_client = Twitch.TwitchEventSubClient(eventsub_settings)

    flask_app_thread = threading.Thread(target=lambda: flask_app.run(port=8080))
    flask_app_thread.start()

    access_token = auth_client.get_access_token()

    irc_client.connect(access_token)

    def on_chat_msg(msg: Twitch.TwitchIRCMessage):
        print(f"Message from {msg.sender}: {msg.content}---")
        if msg.content.strip() == "!hi":
            irc_client.send_message_to_chat(f"Hello, {msg.sender}!")

    def on_channel_point_redemption(red: Twitch.ChannelPointRedemption):
        print(red.__dict__)

    eventsub_client.add_channel_point_redemption_listener(on_channel_point_redemption)

    irc_client.listen_to_chat(on_chat_msg)

    user_id = api_client.get_user_id(access_token)
    _ = eventsub_client.run(access_token, user_id)


if __name__ == "__main__":
    main()
