from os import getenv
import threading

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from src import Twitch
from src.channelpoints import bounties as Bounties

load_dotenv()

## TWITCH SETTINGS ##

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

## INITIALIZATION ##


flask_app = Flask(__name__)
auth_client = Twitch.TwitchOAuthClient(auth_settings, flask_app)
irc_client = Twitch.TwitchIRCClient(irc_settings)
api_client = Twitch.TwitchAPIClient(api_settings)
eventsub_client = Twitch.TwitchEventSubClient(eventsub_settings)


## FLASK APP SETUP


@flask_app.get("/hello")
def hello_world():
    return "Hello, world!"


## TWITCH HANDLERS ##


bounties = Bounties.BountyTracker("In-Game Bounty", "BOUNTY", "./tmp/bounties.tsv")
bans = Bounties.BountyTracker("In-Game Ban", "BAN", "./tmp/bans.tsv")


def on_chat_msg(msg: Twitch.TwitchIRCMessage):
    print(f"Message from {msg.sender}: {msg.content}---")
    if msg.content.strip() == "!hi":
        irc_client.send_message_to_chat(f"Hello, {msg.sender}!")


def on_channel_point_redemption(redemption: Twitch.ChannelPointRedemption):
    bounties.handle_redemption(redemption)
    bans.handle_redemption(redemption)


@flask_app.get("/channelpoints/bounties")  # ?type=<bounties?, bans, both>
def fetch_bounties():

    result = []
    if "type" in request.args:
        print("type in args")
        request_type = request.args["type"]
        match request_type:
            case "bans":
                result = bans.get_bounties()
            case "both":
                result = bounties.get_bounties() + bans.get_bounties()
            # case "bounties":
            case _:
                result = bounties.get_bounties()
    else:
        result = bounties.get_bounties()

    result = sorted(result, key=lambda x: x.split("\t")[-1])

    return jsonify({"bounties": result})


## MAIN ##


def main():
    flask_app_thread = threading.Thread(target=lambda: flask_app.run(port=8080))
    flask_app_thread.start()

    # RUN TWITCH
    access_token = auth_client.get_access_token()
    irc_client.connect(access_token)
    eventsub_client.add_channel_point_redemption_listener(on_channel_point_redemption)
    irc_client.listen_to_chat(on_chat_msg)
    user_id = api_client.get_user_id(access_token)
    _ = eventsub_client.run(access_token, user_id)


if __name__ == "__main__":
    main()
