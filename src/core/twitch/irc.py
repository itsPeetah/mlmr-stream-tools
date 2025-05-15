from dataclasses import dataclass
import socket
import threading
import types


@dataclass
class TwitchIRCSettings:
    hostname: str
    port: int
    bot_nick: str
    channel: str


@dataclass
class TwitchIRCMessage:
    sender: str
    content: str


class TwitchIRCClient:
    def __init__(self, settings: TwitchIRCSettings):
        self._settings = settings
        self._sock = None
        self._listen_thread = None
        self._on_message_listeners = []
        self._on_command_listeners = {}

    def connect(self, access_token: str):

        print("[IRC] Connecting...")

        sock = socket.socket()
        sock.connect((self._settings.hostname, self._settings.port))
        sock.send(f"PASS oauth:{access_token}\r\n".encode("utf-8"))
        sock.send(f"NICK {self._settings.bot_nick}\r\n".encode("utf-8"))
        sock.send(f"JOIN #{self._settings.channel}\r\n".encode("utf-8"))
        self._sock = sock

        print("[IRC] Connected.")

    def send_message_to_chat(self, content: str):
        if self._sock is None:
            print("[IRC] Can't send message because client is not connected.")
            return
        response = f"PRIVMSG #{self._settings.channel} :{content}\r\n"
        self._sock.send(response.encode("utf-8"))

    def listen_to_chat(self, daemon: bool = True):

        if self._sock is None:
            print("[IRC] Can't listen to chat because client is not connected.")
            return
        if self._listen_thread is not None:
            print("[IRC] Already listening to chat.")
            return

        def listen_handler():
            while True:
                resp = self._sock.recv(2048).decode("utf-8")
                if resp.startswith("PING"):
                    self._sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                elif "PRIVMSG" in resp:
                    # print(resp)
                    username = resp.split("!", 1)[0][1:]
                    message = resp.split("PRIVMSG", 1)[1].split(":", 1)[1]
                    if len(message) >= 1:
                        self._handle_message(TwitchIRCMessage(username, message))

        self._listen_thread = threading.Thread(target=listen_handler)
        self._listen_thread.setDaemon(daemon)
        self._listen_thread.start()

    def _handle_message(self, msg: TwitchIRCMessage):
        if msg.content[0] == "!":
            first = msg.content[1:].split(" ")[0]
            if first in self._on_command_listeners:
                for func in self._on_command_listeners[first]:
                    func(msg)
        else:
            for func in self._on_message_listeners:
                func(msg)

    def on_message(self):
        def decorator(func):
            self._on_message_listeners.append(func)
            return func

        return decorator

    def on_command(self, command: str):
        def decorator(func):
            if command not in self._on_command_listeners:
                self._on_command_listeners[command] = []
            self._on_command_listeners.append(func)
            return func

        return decorator
