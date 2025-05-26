from dataclasses import dataclass
import webbrowser
from flask import Flask, request
import requests


@dataclass
class OAuthSettings:
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list[str]


class OAuthClient:
    def __init__(self, settings: OAuthSettings):
        self.settings = settings
        self.auth_code = None

    def _get_auth_url(self):

        scopes = "+".join(self.settings.scopes)

        return (
            f"https://id.twitch.tv/oauth2/authorize"
            f"?client_id={self.settings.client_id}"
            f"&redirect_uri={self.settings.redirect_uri}"
            f"&response_type=code"
            f"&scope={scopes}"
        )

    def _open_auth_url(self):
        webbrowser.open(self._get_auth_url())

    def _get_tokens(self, code):
        url = "https://id.twitch.tv/oauth2/token"
        data = {
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.settings.redirect_uri,
        }
        response = requests.post(url, data=data)
        return response.json()

    def attach_to_flask_app(self, flask_app: Flask):

        auth_route = self.settings.redirect_uri.split("/")[-1]

        @flask_app.route(f"/{auth_route}")
        def handle_redirect():
            self.auth_code = request.args.get("code")
            return "Authorization successful! You can close this tab."

    def get_access_token(self):

        print("[Auth] Authenticating...")

        self.auth_code = None
        self._open_auth_url()

        while self.auth_code is None:
            pass

        print("[Auth] Auth code obtained.")

        tokens = self._get_tokens(self.auth_code)
        access_token = tokens["access_token"]

        print("[Auth] Access token obtained.")

        return access_token
