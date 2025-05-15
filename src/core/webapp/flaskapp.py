from dataclasses import dataclass
import threading

from flask import Flask
from flask_socketio import SocketIO


@dataclass
class WebAppSettings:
    name: str
    port: int


class WebApp:
    def __init__(self, settings: WebAppSettings):
        self.settings = settings
        self.flask_app = Flask(settings.name)
        self.socketio = SocketIO(self.flask_app, debug=True, cors_allowed_origins="*")

        self.thread = None

    def start(self):
        if self.thread is not None:
            print(f"[Web App] WebApp {self.name} has already started.")
            return
        port = self.settings.port
        runner = lambda: self.socketio.run(
            app=self.flask_app,
            debug=True,
            host="0.0.0.0",
            port=port,
            use_reloader=False,
        )
        thread = threading.Thread(target=runner)
        thread.start()
        print("[Web App] Started WebApp.")
        self.thread = thread
