from dataclasses import dataclass

import requests


@dataclass
class TwitchAPISettings:
    client_id: str


class TwitchAPIClient:

    def __init__(self, settings: TwitchAPISettings):
        self.settings = settings

    def get_user_id(self, access_token):
        headers = {
            "Client-ID": self.settings.client_id,
            "Authorization": f"Bearer {access_token}",
        }
        r = requests.get("https://api.twitch.tv/helix/users", headers=headers)
        return r.json()["data"][0]["id"]
