from os import getenv

from dotenv import load_dotenv
from flask import jsonify, request
from flask_socketio import emit, send

from src.core import Twitch, FlaskApp
from src.core.defaultrig import DefaultRig, DefaultRigSettings
from src.extensions import ChannelPoints

load_dotenv()

## TWITCH SETTINGS ##

CLIENT_ID = getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = getenv("TWITCH_CLIENT_SECRET")

webapp_settings = FlaskApp.WebAppSettings(name=__name__, port=8080)

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

default_rig = DefaultRig(
    DefaultRigSettings(
        web_app_settings=webapp_settings,
        twitch_auth_settings=auth_settings,
        twitch_irc_settings=irc_settings,
        twitch_api_settings=api_settings,
        twitch_eventsub_settings=eventsub_settings,
    )
)

## FLASK APP SETUP


@default_rig.webapp.flask_app.get("/hello")
def hello():
    return "Hello, world!"


## TWITCH HANDLERS ##

bounties = ChannelPoints.bounties.BountyTracker(
    "In-Game Bounty", "BOUNTY", "./tmp/bounties.tsv"
)
bans = ChannelPoints.bounties.BountyTracker("In-Game Ban", "BAN", "./tmp/bans.tsv")
tts = ChannelPoints.tts.ScuffedTTS(
    "TTS Message", "./tmp/ttslog.tsv", "./tmp/latest.mp3"
)


@default_rig.irc_client.on_message()
def on_chat_msg(msg: Twitch.TwitchIRCMessage):
    print(f"Message from {msg.sender}: {msg.content}---")
    if msg.content.strip() == "!hi":
        default_rig.irc_client.send_message_to_chat(f"Hello, {msg.sender}!")


@default_rig.eventsub_client.channel_point_redemption()
def on_channel_point_redemption(redemption: Twitch.ChannelPointRedemption):
    bounties.handle_redemption(redemption)
    bans.handle_redemption(redemption)
    tts.handle_redemption(redemption)


@default_rig.webapp.flask_app.get(
    "/channelpoints/bounties"
)  # ?type=<bounties?, bans, both>
def fetch_bounties():
    """this could be a ws event"""

    result = []
    if "type" in request.args:
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


@default_rig.webapp.flask_app.get("/scuffedtts/latest")
def fetch_tts():
    """this could be a ws event"""

    result = tts.get_latest_fifo()
    return jsonify({"data": result})


@default_rig.webapp.socketio.on("message")
def handle_message(msg):
    print(f"Received message: {msg}")
    send(f"Server received: {msg}", broadcast=True)


@default_rig.webapp.socketio.on("custom_event")
def handle_custom_event(data):
    print(f"Custom event data: {data}")
    emit("response_event", {"data": f"Hello {data['name']}!"})


## MAIN ##


def main():
    default_rig.start()


if __name__ == "__main__":
    main()
