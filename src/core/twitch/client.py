from dataclasses import dataclass
import threading
from flask import Flask

from .lib import *


@dataclass
class TwitchRigSettings:
    twitch_auth_settings: TwitchAuth.OAuthSettings
    twitch_irc_settings: TwitchIrc.IRCSettings
    twitch_api_settings: TwitchApi.APISettings
    twitch_eventsub_settings: TwitchEventSub.EventSubSettings


class TwitchRig:
    """Twitch Rig is an all-things twitch client"""

    def __init__(self, settings: TwitchRigSettings):
        # Create clients
        self.auth_client = TwitchAuth.OAuthClient(settings.twitch_auth_settings)
        self.irc_client = TwitchIrc.IRCClient(settings.twitch_irc_settings)
        self.api_client = TwitchApi.APIClient(settings.twitch_api_settings)
        self.eventsub_client = TwitchEventSub.EventSubClient(
            settings.twitch_eventsub_settings
        )

        # Handle OAuth Process
        self.webapp = Flask(__name__)
        self.webapp_thread = None

        # Initialize
        self.auth_client.attach_to_flask_app(self.webapp)

    def start(self):
        flask_app_thread = threading.Thread(target=lambda: self.webapp.run(port=8080))
        flask_app_thread.start()
        self.webapp_thread = flask_app_thread

        access_token = self.auth_client.get_access_token()
        self.irc_client.connect(access_token)
        self.irc_client.listen_to_chat()
        user_id = self.api_client.get_user_id(access_token)
        _ = self.eventsub_client.run(access_token, user_id)
