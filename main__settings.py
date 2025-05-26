from os import getenv

from dotenv import load_dotenv
from src.core import FlaskApp
import src.core.twitch.lib as TwitchLib

load_dotenv()

CLIENT_ID = getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = getenv("TWITCH_CLIENT_SECRET")

webapp_settings = FlaskApp.WebAppSettings(name=__name__, port=8080)

auth_settings = TwitchLib.TwitchAuth.OAuthSettings(
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

irc_settings = TwitchLib.TwitchIrc.IRCSettings(
    hostname="irc.chat.twitch.tv", port=6667, bot_nick="malimore", channel="malimore"
)

api_settings = TwitchLib.TwitchApi.APISettings(
    client_id=CLIENT_ID,
)

eventsub_settings = TwitchLib.TwitchEventSub.EventSubSettings(
    client_id=CLIENT_ID,
    eventsub_ws_url="wss://eventsub.wss.twitch.tv/ws",
)
