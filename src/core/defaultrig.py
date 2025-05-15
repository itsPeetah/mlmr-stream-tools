from dataclasses import dataclass

from .twitch import *

from .webapp import WebAppSettings, WebApp


@dataclass
class DefaultRigSettings:
    web_app_settings: WebAppSettings
    twitch_auth_settings: TwitchOAuthSettings
    twitch_irc_settings: TwitchIRCSettings
    twitch_api_settings: TwitchAPISettings
    twitch_eventsub_settings: TwitchEventSubSettings


class DefaultRig:
    def __init__(self, settings: DefaultRigSettings):
        # Create clients
        self.webapp = WebApp(settings.web_app_settings)
        self.auth_client = TwitchOAuthClient(settings.twitch_auth_settings)
        self.irc_client = TwitchIRCClient(settings.twitch_irc_settings)
        self.api_client = TwitchAPIClient(settings.twitch_api_settings)
        self.eventsub_client = TwitchEventSubClient(settings.twitch_eventsub_settings)

        # Initialize
        self.auth_client.attach_to_flask_app(self.webapp)

    def start(self):
        self.webapp.start()
        access_token = self.auth_client.get_access_token()
        self.irc_client.connect(access_token)
        self.irc_client.listen_to_chat()
        user_id = self.api_client.get_user_id(access_token)
        _ = self.eventsub_client.run(access_token, user_id)
