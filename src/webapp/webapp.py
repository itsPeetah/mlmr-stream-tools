from dataclasses import dataclass
import threading

from flask import Flask


@dataclass
class WebAppSettings:
    name: str
    port: int


class WebApp:
    def __init__(self, settings: WebAppSettings):
        self.settings = settings
        self.flask_app = Flask(settings.name)
        self.thread = None

    def start(self):
        if self.thread is not None:
            print(f"[Web App] WebApp {self.name} has already started.")
            return
        port = self.settings.port
        runner = lambda: self.flask_app.run(port=port)
        thread = threading.Thread(target=runner)
        thread.start()
        self.thread = thread

    def register_get(self, route, handler, **options):
        @self.flask_app.get(route, **options)
        def wrapped_handler():
            return handler()

    def register_post(self, route, handler, **options):
        @self.flask_app.post(route, **options)
        def wrapped_handler():
            return handler()
